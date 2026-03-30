import uuid
from unittest.mock import MagicMock

from src.application.triage_service import ResumeTriageApp
from src.core.entities.candidate import Candidate, JobProfile


def test_triage_service_ranking():
    unique = uuid.uuid4().hex
    file_a = f"test_cv1_{unique}.txt"
    file_b = f"test_cv2_{unique}.txt"
    with open(file_a, "w", encoding="utf-8") as f:
        f.write("CV A")
    with open(file_b, "w", encoding="utf-8") as f:
        f.write("CV B")

    mock_parser = MagicMock()
    mock_parser.parse.return_value = "Texto do currículo"

    mock_ai = MagicMock()
    mock_ai.extract_candidate_data.side_effect = [
        Candidate(name="Candidate A", email="a@test.com"),
        Candidate(name="Candidate B", email="b@test.com"),
    ]
    mock_ai.analyze_job.return_value = JobProfile(
        title="Engenheiro de Software",
        seniority="Pleno",
        functional_core="Backend",
        requirements={"hard_skills": ["Python"]},
        raw_description="Valores Culturais",
    )

    def perform_triage_side_effect(candidate: Candidate, _job_profile: JobProfile, level: str):
        if level == "basic":
            score = 7.0 if candidate.name == "Candidate A" else 9.5
            return {"score_final": score}
        return {"score_final": 9.5, "details": "full"}

    mock_ai.perform_triage.side_effect = perform_triage_side_effect

    mock_repo = MagicMock()
    mock_repo.get_candidate_by_hash.return_value = None
    mock_repo.create_candidate.return_value = MagicMock(id=1)
    mock_repo.save_triage_result.return_value = MagicMock()
    mock_repo.create_job.return_value = MagicMock(id=1)
    mock_repo.increment_task_progress.return_value = None
    mock_repo.log_triage_error.return_value = None

    app = ResumeTriageApp(parser=mock_parser, ai=mock_ai, repository=mock_repo)

    try:
        results, job_profile = app.process_resumes(
            [file_a, file_b],
            "Valores Culturais",
        )

        assert job_profile.title == "Engenheiro de Software"
        assert len(results) == 2
        assert results[0].name == "Candidate B"
        assert results[0].fit_score > results[1].fit_score
        assert results[1].name == "Candidate A"
        assert results[1].fit_score >= 6.0
        assert results[0].fast_match is not None
        assert results[0].fast_match.get("baixa_confianca") is True
        assert results[0].fast_match.get("status_sugerido") == "revisao_assistida"
        assert results[0].fast_match.get("confidence_score", 0) < 0.6
    finally:
        import os

        for path in (file_a, file_b):
            if os.path.exists(path):
                os.remove(path)
