"use client";
import { useEffect, useState, Suspense } from "react";
import { fetchTalentPool, deleteTalentResult } from "@/lib/api";
import { useToast } from "@/components/ui/Toast";
import { Drawer } from "@/components/ui/Drawer";
import { useSearchParams } from "next/navigation";
import { parseAnalysisData, formatAnalysisList } from "@/lib/utils";

function ScoreBadge({ score }: { score: number }) {
  let barColor = "bg-slate-400";
  let badgeClass = "bg-surface-container text-slate-600";
  let label = "Under Review";
  if (score >= 8) { barColor = "bg-emerald-500"; badgeClass = "bg-[#E8F2EF] text-primary"; label = "Strong Match"; }
  else if (score >= 6) { barColor = "bg-primary/60"; badgeClass = "bg-surface-container text-primary/80"; label = "Potential"; }

  return (
    <div className="flex flex-col gap-1.5">
      <div className="flex items-center gap-2">
        <span className="text-xs font-black text-primary">{score.toFixed(1)}</span>
        <div className="w-12 h-1 bg-surface-container-low rounded-full">
          <div className={`h-full ${barColor} rounded-full transition-all duration-1000`} style={{ width: `${Math.min(score * 10, 100)}%` }}></div>
        </div>
      </div>
      <span className={`px-2 py-0.5 ${badgeClass} rounded-md text-[9px] font-black uppercase tracking-widest w-fit border border-outline-variant/10 shadow-sm`}>
        {label}
      </span>
    </div>
  );
}

function TalentContent() {
  const { toast } = useToast();
  const searchParams = useSearchParams();
  const globalQuery = searchParams.get("q") || "";
  const [candidates, setCandidates] = useState<any[]>([]);
  const [filter, setFilter] = useState("");
  const [sortOrder, setSortOrder] = useState<"desc" | "asc">("desc");
  const [selectedCandidate, setSelectedCandidate] = useState<any>(null);
  const [initialLoad, setInitialLoad] = useState(true);

  async function loadData() {
    try { setCandidates(await fetchTalentPool()); } 
    catch { toast("Erro ao buscar", "Talent pool indisponível no momento.", "error"); }
    finally { setInitialLoad(false); }
  }

  useEffect(() => { loadData(); }, []);

  const activeFilter = globalQuery || filter;

  const filtered = candidates
    .filter((c) =>
      c.candidate_name?.toLowerCase().includes(activeFilter.toLowerCase()) ||
      c.job_title?.toLowerCase().includes(activeFilter.toLowerCase())
    )
    .sort((a, b) => {
      const scoreA = a.score || 0;
      const scoreB = b.score || 0;
      return sortOrder === "desc" ? scoreB - scoreA : scoreA - scoreB;
    });

  const handleExport = () => {
    toast("Exportando", "Gerando relatório PDF...", "info");
    setTimeout(() => window.print(), 500);
  };

  const analysis = selectedCandidate ? parseAnalysisData(selectedCandidate.analysis) : null;

  return (
    <div className="space-y-8">
      {/* HEADER SECTION */}
      <section className="flex flex-col md:flex-row md:items-end justify-between gap-6">
        <div className="space-y-1">
          <h1 className="text-3xl font-black text-primary tracking-tight">Talent Pool Analytics</h1>
          <p className="text-sm text-outline font-medium">Gestão inteligente de candidatos e performance de triagem IA.</p>
        </div>
        <div className="flex items-center gap-3">
          <button 
            onClick={handleExport}
            className="flex items-center gap-2 px-5 py-2.5 bg-white border border-outline-variant/30 rounded-lg font-bold text-xs text-primary hover:bg-surface-container-low transition-all active:scale-95 shadow-sm"
          >
            <span className="material-symbols-outlined text-lg">download</span> Exportar PDF
          </button>
          <button 
            onClick={() => {
              setInitialLoad(true);
              loadData().then(() => toast("Sincronizado", "Dados atualizados.", "success"));
            }}
            className="flex items-center gap-2 px-5 py-2.5 bg-primary text-white rounded-lg font-bold text-xs shadow-lg shadow-primary/10 hover:bg-primary-container transition-all active:scale-95"
          >
            <span className="material-symbols-outlined text-lg">sync</span> Atualizar
          </button>
        </div>
      </section>

      {/* METRIC CARDS */}
      <section className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-xl border border-outline-variant/10 shadow-[0_1px_3px_rgba(47,93,82,0.06)]">
          <div className="flex items-center justify-between mb-4">
            <span className="text-[10px] font-black uppercase tracking-[0.15em] text-outline">Total Candidatos</span>
            <div className="bg-[#E8F2EF] p-2 rounded-lg text-primary">
               <span className="material-symbols-outlined text-xl">group</span>
            </div>
          </div>
          {initialLoad ? (
            <div className="h-9 w-16 bg-surface-container mt-1 mb-2 rounded skeleton-pulse" />
          ) : (
            <h3 className="text-3xl font-black text-primary">{candidates.length}</h3>
          )}
          <div className="mt-4 h-1 w-full bg-surface-container-low rounded-full overflow-hidden">
            <div className="h-full bg-primary transition-all duration-1000" style={{ width: initialLoad ? '0%' : '75%' }}></div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl border border-outline-variant/10 shadow-[0_1px_3px_rgba(47,93,82,0.06)]">
          <div className="flex items-center justify-between mb-4">
            <span className="text-[10px] font-black uppercase tracking-[0.15em] text-outline">Strong Matches</span>
            <div className="bg-[#E8F2EF] p-2 rounded-lg text-primary">
               <span className="material-symbols-outlined text-xl">verified</span>
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            {initialLoad ? (
              <div className="h-9 w-16 bg-surface-container mt-1 mb-2 rounded skeleton-pulse" />
            ) : (
              <h3 className="text-3xl font-black text-primary">{candidates.filter(c => (c.score || 0) >= 8).length}</h3>
            )}
            {!initialLoad && <span className="text-[10px] font-bold text-emerald-600 uppercase">Aptos</span>}
          </div>
          <div className="mt-4 h-1 w-full bg-surface-container-low rounded-full overflow-hidden">
            <div className="h-full bg-emerald-500 transition-all duration-1000" style={{ width: initialLoad ? '0%' : `${candidates.length ? (candidates.filter(c => c.score >= 8).length / candidates.length * 100) : 0}%` }}></div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl border border-outline-variant/10 shadow-[0_1px_3px_rgba(47,93,82,0.06)]">
          <div className="flex items-center justify-between mb-4">
            <span className="text-[10px] font-black uppercase tracking-[0.15em] text-outline">Score Médio</span>
            <div className="bg-[#E8F2EF] p-2 rounded-lg text-primary">
               <span className="material-symbols-outlined text-xl">psychology</span>
            </div>
          </div>
          <div className="flex items-baseline gap-2">
            {initialLoad ? (
              <div className="h-9 w-16 bg-surface-container mt-1 mb-2 rounded skeleton-pulse" />
            ) : (
              <h3 className="text-3xl font-black text-primary">
                {candidates.length ? (candidates.reduce((s, c) => s + (c.score || 0), 0) / candidates.length).toFixed(1) : "—"}
              </h3>
            )}
            {!initialLoad && <span className="text-[10px] font-bold text-outline uppercase">Média Geral</span>}
          </div>
          <div className="mt-4 h-1 w-full bg-surface-container-low rounded-full overflow-hidden">
            <div className="h-full bg-primary/40 transition-all duration-1000" style={{ width: initialLoad ? '0%' : `${candidates.length ? (candidates.reduce((s, c) => s + (c.score || 0), 0) / candidates.length * 10) : 0}%` }}></div>
          </div>
        </div>
      </section>

      {/* DATA TABLE & FILTERS */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* FILTERS SIDEBAR */}
        <aside className="lg:col-span-3 space-y-4 fixed lg:relative bottom-4 right-4 lg:bottom-auto lg:right-auto z-30">
          <div className="bg-white p-6 rounded-2xl border border-outline-variant/10 shadow-xl lg:shadow-none">
            <div className="flex items-center justify-between mb-6">
              <h4 className="text-[11px] font-black uppercase tracking-widest text-outline">Filtros</h4>
              <button 
                onClick={() => setFilter("")}
                className="text-[10px] font-bold text-primary hover:underline transition-all"
              >
                Limpar
              </button>
            </div>
            
            <div className="relative group">
              <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-lg text-outline group-focus-within:text-primary transition-colors">search</span>
              <input 
                value={filter} 
                onChange={(e) => setFilter(e.target.value)}
                className="w-full pl-10 pr-4 py-2.5 bg-surface-container-low border border-transparent focus:border-outline-variant/30 rounded-xl text-xs font-medium focus:ring-0 transition-all placeholder:text-outline/50"
                placeholder="Nome ou vaga..." 
              />
            </div>
          </div>
        </aside>

        {/* DATA TABLE */}
        <div className="lg:col-span-9">
          <div className="bg-white rounded-2xl border border-outline-variant/10 shadow-[0_1px_3px_rgba(47,93,82,0.06)] overflow-hidden">
            <div className="px-6 py-5 flex items-center justify-between border-b border-outline-variant/5 bg-surface-container-low/20">
              <div className="flex items-center gap-4">
                <h2 className="text-sm font-black text-on-surface uppercase tracking-widest">Base de Talentos</h2>
                <div className="px-2 py-0.5 bg-[#E8F2EF] text-primary text-[10px] font-black rounded-md">{filtered.length} Resultados</div>
              </div>
              <div className="flex items-center gap-1.5">
                <button 
                  onClick={() => {
                    const newOrder = sortOrder === "desc" ? "asc" : "desc";
                    setSortOrder(newOrder);
                    toast("Ordenado", `Scores ${newOrder === "desc" ? "maiores" : "menores"} primeiro`, "info");
                  }}
                  className={`w-9 h-9 flex items-center justify-center rounded-lg transition-all ${sortOrder === "desc" ? "bg-primary text-white shadow-md" : "bg-white border border-outline-variant/20 text-outline hover:bg-surface-container-low"}`}
                >
                  <span className="material-symbols-outlined text-lg">sort</span>
                </button>
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="bg-surface-container-low/50">
                    <th className="px-6 py-4 text-[10px] font-black uppercase tracking-widest text-outline">Candidato</th>
                    <th className="px-6 py-4 text-[10px] font-black uppercase tracking-widest text-outline">Vaga Alvo</th>
                    <th className="px-6 py-4 text-[10px] font-black uppercase tracking-widest text-outline">IA Match</th>
                    <th className="px-6 py-4 text-[10px] font-black uppercase tracking-widest text-outline text-right">Ações</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-outline-variant/5">
                  {filtered.length === 0 ? (
                    <tr>
                      <td colSpan={4} className="px-6 py-24 text-center">
                        <div className="flex flex-col items-center gap-3">
                          <span className="material-symbols-outlined text-5xl text-outline/20">person_search</span>
                          <p className="text-sm font-bold text-outline">Nenhum talento encontrado</p>
                          <p className="text-xs text-outline/50">Tente ajustar seus filtros ou realizar uma nova triagem.</p>
                        </div>
                      </td>
                    </tr>
                  ) : (
                    filtered.map((candidate, idx) => (
                      <tr key={idx} className="hover:bg-surface-container-low/30 transition-all group cursor-pointer" onClick={() => setSelectedCandidate(candidate)}>
                        <td className="px-6 py-5">
                          <div className="flex items-center gap-3">
                            <div className="w-10 h-10 bg-secondary-container rounded-xl flex items-center justify-center text-primary font-black text-xs shadow-sm group-hover:scale-105 transition-transform">
                              {candidate.candidate_name?.split(" ").map((n: string) => n[0]).join("").slice(0, 2) || "??"}
                            </div>
                            <div>
                              <p className="text-sm font-bold text-on-surface group-hover:text-primary transition-colors">{candidate.candidate_name}</p>
                              <p className="text-[10px] text-outline font-medium">Cadastrado em {candidate.date ? new Date(candidate.date).toLocaleDateString("pt-BR") : "—"}</p>
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-5">
                          <span className="text-xs font-bold text-on-surface-variant bg-surface-container-low px-2 py-1 rounded-md border border-outline-variant/10">
                            {candidate.job_title}
                          </span>
                        </td>
                        <td className="px-6 py-5">
                          <ScoreBadge score={candidate.score || 0} />
                        </td>
                        <td className="px-6 py-5 text-right">
                           <button 
                             onClick={(e) => {
                               e.stopPropagation();
                               setSelectedCandidate(candidate);
                             }}
                             className="w-10 h-10 flex items-center justify-center rounded-full text-outline hover:bg-primary/5 hover:text-primary transition-all opacity-0 group-hover:opacity-100"
                           >
                              <span className="material-symbols-outlined">chevron_right</span>
                           </button>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
            
            <div className="px-6 py-4 bg-surface-container-low/20 border-t border-outline-variant/5">
              <span className="text-[10px] font-bold text-outline uppercase tracking-wider">Final da lista • {filtered.length} talentos mapeados</span>
            </div>
          </div>
        </div>
      </div>

      {/* CANDIDATE DRAWER */}
      <Drawer 
        isOpen={!!selectedCandidate} 
        onClose={() => setSelectedCandidate(null)} 
        title="Perfil do Talento"
      >
        {selectedCandidate && (
          <div className="space-y-8 animate-in fade-in slide-in-from-right-4 duration-300 pb-20">
            <header className="flex items-center gap-5 border-b border-outline-variant/10 pb-8">
              <div className="w-20 h-20 bg-secondary-container rounded-3xl flex items-center justify-center text-primary font-black text-3xl shadow-lg shadow-primary/5">
                {selectedCandidate.candidate_name?.split(" ").map((n: string) => n[0]).join("").slice(0, 2) || "??"}
              </div>
              <div className="space-y-1">
                <h3 className="text-2xl font-black text-primary leading-tight">{selectedCandidate.candidate_name}</h3>
                <p className="text-sm font-bold text-outline flex items-center gap-2">
                   <span className="material-symbols-outlined text-base">work</span>
                   {selectedCandidate.job_title}
                </p>
              </div>
            </header>
            
            <section className="bg-surface-container-low/40 p-6 rounded-2xl border border-outline-variant/10 space-y-6">
              <div className="flex items-center justify-between">
                 <h4 className="text-[11px] font-black uppercase tracking-[0.2em] text-outline">Análise do Match IA</h4>
                 <span className="material-symbols-outlined text-primary" style={{ fontVariationSettings: "'FILL' 1" }}>psychology</span>
              </div>
              
              <div className="flex flex-col gap-4">
                <div className="flex items-center justify-between">
                   <span className="text-sm font-bold text-on-surface">Compatibilidade Técnica</span>
                   <span className="text-xl font-black text-primary">{(selectedCandidate.score * 10).toFixed(0)}%</span>
                </div>
                <div className="w-full h-2.5 bg-white rounded-full overflow-hidden border border-outline-variant/10">
                   <div className="h-full bg-primary rounded-full" style={{ width: `${selectedCandidate.score * 10}%` }}></div>
                </div>
              </div>

              <div className="space-y-4">
                <p className="text-xs font-black text-outline uppercase tracking-widest">Parecer Detalhado do Sistema</p>
                <div className="text-sm text-on-surface-variant leading-relaxed space-y-3">
                  {!analysis || (!analysis.verdict && !analysis.strengths && !analysis.gaps && !analysis.interviewQuestion) ? (
                    <p className="text-outline/60 italic">Este candidato ainda não possui uma análise detalhada estruturada.</p>
                  ) : (
                    <>
                      <p className="font-bold text-primary italic">"{analysis.verdict}"</p>
                      
                      {analysis.strengths && (
                        <div className="pt-2">
                          <p className="font-black text-[10px] uppercase text-emerald-600 tracking-wider">Pontos Fortes:</p>
                          <ul className="list-disc list-inside space-y-1 mt-1">
                            {formatAnalysisList(analysis.strengths).map((item, i) => (
                              <li key={i} className="text-on-surface-variant font-medium leading-relaxed">{item}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                      
                      {analysis.gaps && (
                        <div className="pt-2">
                          <p className="font-black text-[10px] uppercase text-amber-600 tracking-wider">Lacunas Técnicas:</p>
                          <ul className="list-disc list-inside space-y-1 mt-1">
                            {formatAnalysisList(analysis.gaps).map((item, i) => (
                              <li key={i} className="text-on-surface-variant font-medium leading-relaxed">{item}</li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {analysis.interviewQuestion && (
                        <div className="pt-4 p-4 bg-primary/5 rounded-xl border border-primary/10">
                          <p className="font-black text-[10px] uppercase text-primary tracking-widest mb-2 flex items-center gap-2">
                            <span className="material-symbols-outlined text-xs">quiz</span> Sugestão de Pergunta
                          </p>
                          <p className="text-sm font-bold text-primary leading-relaxed italic">
                            "{Array.isArray(analysis.interviewQuestion) ? analysis.interviewQuestion[0] : analysis.interviewQuestion}"
                          </p>
                        </div>
                      )}
                    </>
                  )}
                </div>
              </div>
            </section>

            <section className="space-y-4">
              <div className="flex items-center justify-between">
                <h4 className="text-[11px] font-black uppercase tracking-[0.2em] text-outline">Dados do Currículo (Texto Original)</h4>
                <span className="material-symbols-outlined text-outline/40">description</span>
              </div>
              <div className="bg-surface-container-low/20 p-4 rounded-xl border border-outline-variant/10 max-h-64 overflow-y-auto custom-scrollbar">
                 <pre className="text-[11px] text-on-surface-variant whitespace-pre-wrap font-sans leading-relaxed">
                   {selectedCandidate.original_text || "Texto indisponível."}
                 </pre>
              </div>
            </section>

            <div className="grid grid-cols-2 gap-4">
              <button 
                onClick={() => toast("Abrindo Currículo", "Visualizando documento original...", "info")}
                className="flex flex-col items-center gap-3 p-5 border-2 border-outline-variant/20 rounded-2xl hover:border-primary/30 hover:bg-surface-container-low transition-all group"
              >
                <span className="material-symbols-outlined text-outline group-hover:text-primary transition-colors">description</span>
                <span className="text-[10px] font-black uppercase tracking-widest text-outline group-hover:text-primary">Ver Currículo</span>
              </button>
              <button 
                onClick={() => toast("Contato", "Iniciando fluxo de contato...", "success")}
                className="flex flex-col items-center gap-3 p-5 bg-primary rounded-2xl shadow-lg shadow-primary/10 hover:bg-primary-container transition-all"
              >
                <span className="material-symbols-outlined text-white">mail</span>
                <span className="text-[10px] font-black uppercase tracking-widest text-white">Enviar E-mail</span>
              </button>
            </div>

            <div className="pt-4 border-t border-red-500/10 mt-4">
              <button 
                onClick={async () => {
                  try {
                    await deleteTalentResult(selectedCandidate.id);
                    toast("Candidato Excluído", "Registro removido com sucesso.", "success");
                    setSelectedCandidate(null);
                    setTimeout(() => window.location.reload(), 500); 
                  } catch(e) {
                     toast("Erro", "Não foi possível excluir o resultado.", "error");
                  }
                }}
                className="w-full flex items-center justify-center gap-3 p-4 border-2 border-red-500/20 bg-red-50/50 rounded-2xl hover:bg-red-50 transition-all group"
              >
                <span className="material-symbols-outlined text-red-500 group-hover:text-red-700 transition-colors">delete</span>
                <span className="text-[10px] font-black uppercase tracking-widest text-red-500 group-hover:text-red-700">Excluir Resultado</span>
              </button>
            </div>
          </div>
        )}
      </Drawer>
    </div>
  );
}

export default function TalentPage() {
  return (
    <Suspense fallback={<div>Carregando Filtros...</div>}>
      <TalentContent />
    </Suspense>
  );
}
