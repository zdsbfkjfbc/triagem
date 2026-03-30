import hashlib
import os
import re
import time
import unicodedata
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Semaphore
from typing import Any, Dict, List, Optional, Tuple

from src.core.entities.candidate import Candidate, Experience, JobProfile
from src.core.interfaces.ai_provider import AIProvider
from src.core.interfaces.file_parser import FileParser
from src.infrastructure.database.repository import TriageRepository


class ResumeTriageApp:
    def __init__(
        self,
        parser: FileParser,
        ai: AIProvider,
        repository: Optional[TriageRepository] = None,
    ):
        self.parser = parser
        self.ai = ai
        self.repo = repository or TriageRepository()
        self.max_workers = 3
        self.semaphore = Semaphore(self.max_workers)
        self.confidence_threshold = 0.6
        self.review_score_floor = 6.0

    def _normalize_text(self, text: str) -> str:
        if not text:
            return ""
        normalized = unicodedata.normalize("NFKD", text)
        normalized = "".join(ch for ch in normalized if not unicodedata.combining(ch))
        return normalized.lower()

    def _get_file_hash(self, file_path: str) -> str:
        hasher = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    def _is_generic_verdict(self, verdict: str) -> bool:
        v = self._normalize_text(verdict)
        generic_patterns = [
            "sem comprovacao de requisitos",
            "sem comprovacao de requisito",
            "habilidades essenciais",
            "nao foi possivel",
            "candidato com experiencia",
        ]
        return any(p in v for p in generic_patterns)

    def _tokenize_keywords(self, text: str) -> List[str]:
        stopwords = {
            "para",
            "com",
            "sem",
            "que",
            "uma",
            "como",
            "dos",
            "das",
            "por",
            "nos",
            "nas",
            "aos",
            "aas",
            "ser",
            "sua",
            "seu",
            "sao",
            "tem",
            "mais",
            "muito",
            "muita",
        }
        words = re.findall(r"[a-z0-9_]{4,}", text)
        return [w for w in words if w not in stopwords]

    def _context_similarity(self, candidate_text: str, job_text: str) -> float:
        cand_tokens = set(self._tokenize_keywords(candidate_text))
        job_tokens = set(self._tokenize_keywords(job_text))
        if not cand_tokens or not job_tokens:
            return 0.0
        overlap = cand_tokens.intersection(job_tokens)
        union = cand_tokens.union(job_tokens)
        return round(len(overlap) / max(1, len(union)), 3)

    def _extract_required_flags(self, candidate_text: str, job_text: str) -> Dict[str, Dict[str, bool]]:
        job_has_ensino_medio = "ensino medio" in job_text
        cand_has_ensino_medio = bool(re.search(r"\bensino\s+medio\b", candidate_text))

        job_has_flex = ("flexibilidade de horario" in job_text) or ("disponibilidade de horario" in job_text)
        cand_has_flex = (
            ("flexibilidade de horario" in candidate_text)
            or ("disponibilidade de horario" in candidate_text)
            or ("disponibilidade" in candidate_text and "horario" in candidate_text)
        )

        return {
            "ensino_medio": {"requerido": job_has_ensino_medio, "encontrado": cand_has_ensino_medio},
            "flexibilidade_horario": {"requerido": job_has_flex, "encontrado": cand_has_flex},
        }

    def _build_final_verdict(self, heuristic: Dict[str, Any]) -> str:
        missing_required = heuristic.get("requisitos_obrigatorios_pendentes", [])
        evidence_count = len(heuristic.get("evidencias_encontradas", []))
        score = float(heuristic.get("score_heuristico", 0.0))

        if missing_required:
            labels = ", ".join(missing_required)
            return (
                "Candidato com experiência relevante, porém com pendências em requisitos obrigatórios: "
                f"{labels}."
            )
        if score >= 7.5:
            return "Candidato com forte aderência contextual à vaga e evidências consistentes nos requisitos principais."
        if evidence_count >= 3:
            return "Candidato com aderência parcial à vaga, com boa experiência contextual e pontos a validar em entrevista."
        return "Candidato com aderência limitada no contexto textual para esta vaga."

    def _build_heuristic_analysis(self, original_text: str, job_description: str) -> Dict[str, Any]:
        source = self._normalize_text(original_text)
        job = self._normalize_text(job_description)
        competency_map = {
            "atendimento_consultivo": ["atendimento consultivo", "experiencia do cliente", "jornada do cliente"],
            "fidelizacao_pos_venda": ["fidelizacao", "pos-venda", "pos venda", "relacionamento com a marca"],
            "vendas_digitais": ["whatsapp", "instagram", "redes sociais", "digital", "online"],
            "vm_loja": ["vm", "visual merchandising", "vitrine", "padrao visual", "reposicao"],
            "metas_resultados": ["metas", "superacao", "supercotas", "kpi", "vendedora do mes"],
            "colaboracao_comunicacao": ["trabalho em equipe", "colaboradora", "apoio a gerente", "comunicacao"],
            "ensino_medio": ["ensino medio"],
            "flexibilidade_horario": ["flexibilidade de horario", "disponibilidade de horario"],
        }

        evidence: List[str] = []
        missing: List[str] = []
        required_count = 0
        for competency, keywords in competency_map.items():
            job_relevant = any(k in job for k in keywords)
            candidate_hit = any(k in source for k in keywords)
            if job_relevant:
                required_count += 1
                if candidate_hit:
                    evidence.append(competency)
                else:
                    missing.append(competency)
            elif candidate_hit:
                evidence.append(competency)

        required_flags = self._extract_required_flags(source, job)
        missing_required: List[str] = []
        for key, values in required_flags.items():
            if values["requerido"] and not values["encontrado"]:
                missing_required.append(key)
                if key not in missing:
                    missing.append(key)
            if values["requerido"] and values["encontrado"] and key not in evidence:
                evidence.append(key)

        effective_required = max(1, required_count + sum(1 for v in required_flags.values() if v["requerido"]))
        coverage = len([e for e in evidence if e in competency_map or e in required_flags]) / effective_required
        context_similarity = self._context_similarity(source, job)
        heuristic_score = round(min(10.0, (coverage * 7.0) + (context_similarity * 3.0)), 2)

        return {
            "score_heuristico": heuristic_score,
            "evidencias_encontradas": evidence,
            "lacunas_reais": missing,
            "cobertura_competencias": round(coverage, 3),
            "similaridade_contexto": context_similarity,
            "requisitos_obrigatorios": required_flags,
            "requisitos_obrigatorios_pendentes": missing_required,
        }

    def _compute_confidence(
        self,
        candidate: Candidate,
        ai_result: Dict[str, Any],
        heuristic: Dict[str, Any],
    ) -> float:
        confidence = 0.5
        if candidate.skills:
            confidence += 0.2
        if candidate.experience:
            confidence += 0.2
        if heuristic.get("cobertura_competencias", 0) >= 0.4:
            confidence += 0.1

        verdict = str(ai_result.get("veredito", ""))
        if self._is_generic_verdict(verdict):
            confidence -= 0.2
        if not ai_result.get("score_final"):
            confidence -= 0.1

        return round(max(0.0, min(1.0, confidence)), 3)

    def _compose_hybrid_result(
        self,
        candidate: Candidate,
        basic_match: Dict[str, Any],
        heuristic: Dict[str, Any],
    ) -> Dict[str, Any]:
        ai_score = float(basic_match.get("score_final", 0.0))
        heuristic_score = float(heuristic.get("score_heuristico", 0.0))
        combined_score = round((ai_score * 0.7) + (heuristic_score * 0.3), 2)
        confidence = self._compute_confidence(candidate, basic_match, heuristic)

        generic_verdict = self._is_generic_verdict(str(basic_match.get("veredito", "")))
        low_confidence = (not candidate.skills) or generic_verdict or (confidence < self.confidence_threshold)

        final_score = combined_score
        status = "novo"
        if low_confidence:
            status = "revisao_assistida"
            final_score = max(final_score, self.review_score_floor)

        final_verdict = self._build_final_verdict(heuristic)

        return {
            "score_ai": ai_score,
            "score_final": round(final_score, 2),
            "confidence_score": confidence,
            "status_sugerido": status,
            "baixa_confianca": low_confidence,
            "veredito": final_verdict,
            "motivo_da_nota": {
                "ai": ai_score,
                "heuristico": heuristic_score,
                "peso_ai": 0.7,
                "peso_heuristico": 0.3,
            },
        }

    def process_single_resume(self, path: str, job_profile: JobProfile, job_id: int) -> Candidate:
        with self.semaphore:
            t_init = time.perf_counter()
            f_hash = self._get_file_hash(path)
            timings: Dict[str, float] = {
                "cache_lookup_s": 0.0,
                "parse_s": 0.0,
                "extract_s": 0.0,
                "heuristic_s": 0.0,
                "basic_triage_s": 0.0,
                "full_triage_s": 0.0,
                "save_result_s": 0.0,
            }

            candidate: Candidate
            t_cache = time.perf_counter()
            cached_candidate = self.repo.get_candidate_by_hash(f_hash)
            timings["cache_lookup_s"] = round(time.perf_counter() - t_cache, 3)
            if cached_candidate:
                exp_list = cached_candidate.extracted_json.get("experience", [])
                experiences = [Experience(**e) if isinstance(e, dict) else e for e in exp_list]
                candidate = Candidate(
                    name=cached_candidate.name,
                    email=getattr(cached_candidate, "email", ""),
                    skills=cached_candidate.extracted_json.get("skills", []),
                    experience=experiences,
                    metadata={
                        "cached": True,
                        "original_text": getattr(cached_candidate, "original_text", "") or "",
                    },
                )
                cand_id = cached_candidate.id
            else:
                t_parse = time.perf_counter()
                text = self.parser.parse(path)
                timings["parse_s"] = round(time.perf_counter() - t_parse, 3)

                t_extract = time.perf_counter()
                candidate = self.ai.extract_candidate_data(text)
                timings["extract_s"] = round(time.perf_counter() - t_extract, 3)
                candidate.metadata["original_text"] = text
                extracted_data = {
                    "skills": candidate.skills,
                    "experience": [exp.__dict__ for exp in candidate.experience],
                }
                new_cand = self.repo.create_candidate(
                    f_hash, candidate.name, extracted_data, text, email=candidate.email
                )
                cand_id = new_cand.id

            t_basic = time.perf_counter()
            basic_match = self.ai.perform_triage(candidate, job_profile, level="basic")
            timings["basic_triage_s"] = round(time.perf_counter() - t_basic, 3)
            if not basic_match or "score_final" not in basic_match:
                raise ValueError(
                    f"Falha na IA: Nao foi possivel analisar o candidato {candidate.name} para esta vaga."
                )

            source_text = str(candidate.metadata.get("original_text", ""))
            t_heuristic = time.perf_counter()
            heuristic = self._build_heuristic_analysis(source_text, job_profile.raw_description)
            timings["heuristic_s"] = round(time.perf_counter() - t_heuristic, 3)
            hybrid = self._compose_hybrid_result(candidate, basic_match, heuristic)

            candidate.fast_match = {
                **basic_match,
                **hybrid,
                "evidencias_encontradas": heuristic.get("evidencias_encontradas", []),
                "lacunas_reais": heuristic.get("lacunas_reais", []),
            }
            candidate.fit_score = float(hybrid.get("score_final", 0.0))
            candidate.detailed_audit = None

            if candidate.fit_score >= 7.5:
                print(f"{candidate.name} obteve {candidate.fit_score}. Acionando Auditoria Profunda...")
                t_full = time.perf_counter()
                detailed = self.ai.perform_triage(candidate, job_profile, level="full")
                timings["full_triage_s"] = round(time.perf_counter() - t_full, 3)
                if detailed and "score_final" in detailed:
                    candidate.detailed_audit = detailed

            analysis_data = {
                "fast_match": candidate.fast_match,
                "detailed_audit": candidate.detailed_audit,
                "diagnostics": {
                    "timings": timings,
                },
            }
            t_save = time.perf_counter()
            self.repo.save_triage_result(
                job_id,
                cand_id,
                candidate.fit_score,
                analysis_data,
                status=hybrid.get("status_sugerido", "novo"),
            )
            timings["save_result_s"] = round(time.perf_counter() - t_save, 3)

            candidate.metadata["timings"] = timings
            candidate.metadata["total_time"] = round(time.perf_counter() - t_init, 2)
            print(
                f"[timing] {candidate.name}: "
                f"cache={timings['cache_lookup_s']}s "
                f"parse={timings['parse_s']}s "
                f"extract={timings['extract_s']}s "
                f"basic={timings['basic_triage_s']}s "
                f"full={timings['full_triage_s']}s "
                f"heuristic={timings['heuristic_s']}s "
                f"save={timings['save_result_s']}s "
                f"total={candidate.metadata['total_time']}s"
            )
            return candidate

    def process_resumes(
        self,
        file_paths: List[str],
        job_description: str,
        job_id: Optional[int] = None,
    ) -> Tuple[List[Candidate], JobProfile]:
        print(f"Iniciando Triagem de {len(file_paths)} arquivos...")
        job_profile = self.ai.analyze_job(job_description)

        if not job_id:
            new_job = self.repo.create_job(
                title=job_profile.title,
                description=job_description,
                requirements_json=job_profile.requirements,
            )
            job_id = new_job.id

        results: List[Candidate] = []
        total = len(file_paths)

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(self.process_single_resume, p, job_profile, job_id): p for p in file_paths}

            count = 0
            for future in as_completed(futures):
                count += 1
                file_path = futures[future]
                file_name = os.path.basename(file_path)

                try:
                    candidate = future.result()
                    results.append(candidate)
                    self.repo.increment_task_progress(job_id)
                    progress = int((count / total) * 10)
                    bar = "#" * progress + "-" * (10 - progress)
                    print(f"[{bar}] {int(count / total * 100)}% | {candidate.name} finalizado.")
                except Exception as exc:
                    print(f"Erro ao processar {file_name}: {exc}")
                    self.repo.log_triage_error(job_id, file_name, str(exc))
                    self.repo.increment_task_progress(job_id, status="running")

        results.sort(key=lambda x: x.fit_score, reverse=True)
        return results, job_profile
