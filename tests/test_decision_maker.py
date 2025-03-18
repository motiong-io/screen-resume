import pytest
from agents.decision_maker import DecisionMakerAgent

@pytest.fixture
def decision_maker():
    return DecisionMakerAgent()

@pytest.fixture
def sample_candidate_info():
    return {
        "skills": ["Python", "JavaScript", "Docker", "AWS", "React"],
        "experience": [
            {
                "title": "Senior Software Engineer",
                "company": "Tech Corp",
                "duration": "2 years",
                "responsibilities": ["Led team", "Developed microservices"]
            }
        ],
        "education": [
            {
                "degree": "Master of Computer Science",
                "institution": "University of Technology",
                "year": "2018"
            }
        ]
    }

@pytest.fixture
def sample_job_requirements():
    return {
        "required_skills": ["Python", "JavaScript", "React", "AWS"],
        "required_experience": {
            "years": 2,
            "level": "Senior",
            "required_roles": ["Software Engineer"]
        },
        "required_education": {
            "minimum_degree": "Bachelor",
            "field": "Computer Science"
        }
    }

@pytest.mark.asyncio
async def test_validate_valid_input(decision_maker, sample_candidate_info, sample_job_requirements):
    """Test validation with valid input."""
    valid_input = {
        "candidate_info": sample_candidate_info,
        "job_requirements": sample_job_requirements
    }
    assert await decision_maker.validate(valid_input)

@pytest.mark.asyncio
async def test_validate_invalid_input(decision_maker):
    """Test validation with invalid input."""
    invalid_inputs = [
        None,
        {},
        {"candidate_info": {}},
        {"job_requirements": {}},
        {"wrong_key": "value"}
    ]
    for invalid_input in invalid_inputs:
        assert not await decision_maker.validate(invalid_input)

@pytest.mark.asyncio
async def test_process_valid_input(decision_maker, sample_candidate_info, sample_job_requirements):
    """Test processing of valid input."""
    result = await decision_maker.process({
        "candidate_info": sample_candidate_info,
        "job_requirements": sample_job_requirements
    })
    
    assert isinstance(result, dict)
    assert "scores" in result
    assert "overall_score" in result
    assert "recommendation" in result
    assert "analysis" in result
    
    # Validate scores
    assert isinstance(result["scores"], dict)
    assert "skills_match" in result["scores"]
    assert "experience_match" in result["scores"]
    assert "education_match" in result["scores"]
    
    # Validate score ranges
    assert 0 <= result["scores"]["skills_match"] <= 1
    assert 0 <= result["scores"]["experience_match"] <= 1
    assert 0 <= result["scores"]["education_match"] <= 1
    assert 0 <= result["overall_score"] <= 1

@pytest.mark.asyncio
async def test_process_invalid_input(decision_maker):
    """Test processing with invalid input."""
    with pytest.raises(ValueError):
        await decision_maker.process({"wrong_key": "value"})

@pytest.mark.asyncio
async def test_evaluate_skills(decision_maker):
    """Test skill evaluation functionality."""
    candidate_skills = ["Python", "JavaScript", "React"]
    required_skills = ["Python", "JavaScript", "AWS"]
    score = await decision_maker._evaluate_skills(candidate_skills, required_skills)
    assert isinstance(score, float)
    assert 0 <= score <= 1

@pytest.mark.asyncio
async def test_evaluate_skills_empty_input(decision_maker):
    """Test skill evaluation with empty input."""
    score = await decision_maker._evaluate_skills([], [])
    assert score == 0.0

@pytest.mark.asyncio
async def test_generate_recommendation(decision_maker):
    """Test recommendation generation for different scores."""
    recommendations = [
        await decision_maker._generate_recommendation(0.9),
        await decision_maker._generate_recommendation(0.7),
        await decision_maker._generate_recommendation(0.5),
        await decision_maker._generate_recommendation(0.3)
    ]
    
    assert all(isinstance(r, str) for r in recommendations)
    assert len(set(recommendations)) > 1  # Different scores should yield different recommendations 