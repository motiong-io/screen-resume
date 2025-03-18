import pytest
from fastapi.testclient import TestClient
from main import app

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def sample_request_data(sample_files):
    """Sample request data for testing the screening endpoint."""
    return {
        "jd_file": sample_files["pdf"],
        "resume_files": [sample_files["pdf"], sample_files["docx"]]
    }

def test_read_root(client):
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 404  # No root endpoint defined

def test_screen_resumes_valid_input(client, sample_request_data):
    """Test the resume screening endpoint with valid input."""
    response = client.post("/screen", json=sample_request_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "candidates" in data
    assert "job_requirements" in data
    
    # Validate candidates structure
    assert isinstance(data["candidates"], list)
    if data["candidates"]:
        candidate = data["candidates"][0]
        assert "file_name" in candidate
        assert "candidate_info" in candidate
        assert "evaluation" in candidate
        
        # Validate evaluation structure
        evaluation = candidate["evaluation"]
        assert "scores" in evaluation
        assert "overall_score" in evaluation
        assert "recommendation" in evaluation
        assert "analysis" in evaluation

def test_screen_resumes_invalid_input(client):
    """Test the resume screening endpoint with invalid input."""
    invalid_inputs = [
        {},
        {"jd_file": "test.pdf"},
        {"resume_files": ["test.pdf"]},
        {"jd_file": "test.pdf", "resume_files": "not_a_list"},
        {"jd_file": "test.txt", "resume_files": ["test.pdf"]},  # Unsupported format
    ]
    
    for invalid_input in invalid_inputs:
        response = client.post("/screen", json=invalid_input)
        assert response.status_code in (422, 400)  # Validation error or bad request

def test_screen_resumes_file_not_found(client):
    """Test the resume screening endpoint with non-existent files."""
    data = {
        "jd_file": "nonexistent.pdf",
        "resume_files": ["nonexistent.pdf"]
    }
    response = client.post("/screen", json=data)
    assert response.status_code == 400  # Bad request

def test_screen_resumes_sorting(client, sample_request_data):
    """Test that candidates are sorted by overall score."""
    response = client.post("/screen", json=sample_request_data)
    assert response.status_code == 200
    
    data = response.json()
    candidates = data["candidates"]
    
    if len(candidates) > 1:
        scores = [c["evaluation"]["overall_score"] for c in candidates]
        assert scores == sorted(scores, reverse=True)  # Check if scores are sorted in descending order 