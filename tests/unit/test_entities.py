from src.core.entities.candidate import Candidate
from src.core.entities.candidate import Experience

def test_candidate_creation():
    candidate = Candidate(
        name="Alice Smith",
        email="alice@example.com",
        skills=["Python", "Java"],
        experience=[
            Experience(company="Tech Corp", role="Dev", duration="2 years")
        ]
    )
    assert candidate.name == "Alice Smith"
    assert len(candidate.skills) == 2
    assert candidate.experience[0].role == "Dev"

def test_candidate_types():
    # Apenas verifica se os atributos estão acessíveis
    candidate = Candidate(name="Bob", email="bob@example.com")
    assert isinstance(candidate.skills, list)
    assert candidate.phone is None
