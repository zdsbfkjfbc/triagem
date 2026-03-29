from unittest.mock import MagicMock
from src.core.entities.candidate import Candidate
from src.application.triage_service import ResumeTriageApp

def test_triage_service_ranking():
    # 1. Setup Mocks
    mock_parser = MagicMock()
    mock_parser.parse.return_value = "Texto do currículo"
    
    mock_ai = MagicMock()
    # Mocking extraction
    mock_ai.extract_candidate_data.side_effect = [
        Candidate(name="Candidate A", email="a@test.com"),
        Candidate(name="Candidate B", email="b@test.com"),
    ]
    # Mocking evaluation scores
    mock_ai.evaluate_fit.side_effect = [7.0, 9.5]
    
    # 2. Setup App
    app = ResumeTriageApp(parser=mock_parser, ai=mock_ai)
    
    # 3. Run
    files = ["cv1.txt", "cv2.txt"]
    results = app.process_resumes(files, "Valores Culturais")
    
    # 4. Verify Ranking (B should be first due to higher score)
    assert len(results) == 2
    assert results[0].name == "Candidate B"
    assert results[0].fit_score == 9.5
    assert results[1].name == "Candidate A"
    assert results[1].fit_score == 7.0
