import pytest
from agents.jd_analyzer import JDAnalyzerAgent

@pytest.fixture
def jd_analyzer():
    return JDAnalyzerAgent()

@pytest.fixture
def sample_jd_text():
    return """
    Senior Software Engineer
    
    About the Role:
    We are seeking a Senior Software Engineer to join our growing technology team. This role is part of our Cloud Infrastructure division.
    
    Required Skills:
    - Expert in Python and JavaScript
    - Experience with AWS and cloud infrastructure
    - Strong knowledge of microservices architecture
    - Proficient in Docker and Kubernetes
    
    Responsibilities:
    - Design and implement scalable microservices
    - Lead technical projects and mentor junior developers
    - Collaborate with cross-functional teams
    - Optimize system performance and reliability
    
    Requirements:
    - 5+ years of software development experience
    - Bachelor's degree in Computer Science or related field
    - Previous experience leading technical teams
    - Strong problem-solving skills
    
    Industry: Technology/Cloud Computing
    Location: Remote
    """

@pytest.mark.asyncio
async def test_validate_valid_input(jd_analyzer):
    """Test validation with valid input."""
    valid_input = {"text": "Sample job description"}
    assert await jd_analyzer.validate(valid_input)

@pytest.mark.asyncio
async def test_validate_invalid_input(jd_analyzer):
    """Test validation with invalid input."""
    invalid_inputs = [
        None,
        "",
        {},
        {"wrong_key": "text"},
        ["text"]
    ]
    for invalid_input in invalid_inputs:
        assert not await jd_analyzer.validate(invalid_input)

@pytest.mark.asyncio
async def test_process_valid_input(jd_analyzer, sample_jd_text):
    """Test processing of valid job description."""
    result = await jd_analyzer.process({"text": sample_jd_text})
    
    assert isinstance(result, dict)
    assert "job_title" in result
    assert "job_variant" in result
    assert "industry" in result
    assert "job_description" in result
    assert "tasks" in result
    
    # Validate tasks structure
    assert isinstance(result["tasks"], list)
    if result["tasks"]:
        task = result["tasks"][0]
        assert "task_name" in task
        assert "task_description" in task
        assert "related_skills" in task
        assert "required_knowledge" in task
        assert "job_context" in task
        assert "competency_level" in task

@pytest.mark.asyncio
async def test_process_invalid_input(jd_analyzer):
    """Test processing with invalid input."""
    with pytest.raises(ValueError):
        await jd_analyzer.process({"wrong_key": "text"})

@pytest.mark.asyncio
async def test_extract_job_title(jd_analyzer):
    """Test job title extraction."""
    text = "Senior Software Engineer\nWe are seeking..."
    title = await jd_analyzer._extract_job_title(text)
    assert isinstance(title, str)

@pytest.mark.asyncio
async def test_determine_job_variant(jd_analyzer):
    """Test job variant determination."""
    text = "Senior Software Engineer - Cloud Infrastructure"
    variant = await jd_analyzer._determine_job_variant(text)
    assert isinstance(variant, str)

@pytest.mark.asyncio
async def test_determine_industry(jd_analyzer):
    """Test industry determination."""
    text = "Industry: Technology/Cloud Computing"
    industry = await jd_analyzer._determine_industry(text)
    assert isinstance(industry, str)

@pytest.mark.asyncio
async def test_extract_tasks(jd_analyzer):
    """Test task extraction."""
    text = """
    Responsibilities:
    - Design and implement scalable microservices
    - Lead technical projects
    """
    tasks = await jd_analyzer._extract_tasks(text)
    assert isinstance(tasks, list)

@pytest.mark.asyncio
async def test_extract_skills(jd_analyzer):
    """Test skill extraction from task."""
    task_text = "Design and implement scalable microservices using Python and Docker"
    skills = await jd_analyzer._extract_skills(task_text)
    assert isinstance(skills, list) 