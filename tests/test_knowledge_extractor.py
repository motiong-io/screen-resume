import pytest
from agents.knowledge_extractor import KnowledgeExtractorAgent

@pytest.fixture
def knowledge_extractor():
    return KnowledgeExtractorAgent()

@pytest.fixture
def sample_resume_text():
    return """
    John Doe
    Software Engineer
    email: john@example.com
    phone: (123) 456-7890

    Skills:
    Python, JavaScript, React, Docker, AWS
    
    Experience:
    Senior Software Engineer | Tech Corp | 2020-Present
    - Developed microservices using Python and Docker
    - Led team of 5 developers
    
    Software Engineer | StartUp Inc | 2018-2020
    - Built React applications
    - Implemented CI/CD pipelines
    
    Education:
    Master of Computer Science | University of Technology | 2018
    Bachelor of Computer Science | State University | 2016
    """

@pytest.mark.asyncio
async def test_validate_valid_input(knowledge_extractor):
    """Test validation with valid input."""
    valid_input = {"text": "Sample text"}
    assert await knowledge_extractor.validate(valid_input)

@pytest.mark.asyncio
async def test_validate_invalid_input(knowledge_extractor):
    """Test validation with invalid input."""
    invalid_inputs = [
        None,
        "",
        {},
        {"wrong_key": "text"},
        ["text"],
    ]
    for invalid_input in invalid_inputs:
        assert not await knowledge_extractor.validate(invalid_input)

@pytest.mark.asyncio
async def test_process_valid_input(knowledge_extractor, sample_resume_text):
    """Test processing of valid resume text."""
    result = await knowledge_extractor.process({"text": sample_resume_text})
    
    assert isinstance(result, dict)
    assert "skills" in result
    assert "experience" in result
    assert "education" in result
    assert "contact_info" in result
    
    # Validate result structure
    assert isinstance(result["skills"], list)
    assert isinstance(result["experience"], list)
    assert isinstance(result["education"], list)
    assert isinstance(result["contact_info"], dict)

@pytest.mark.asyncio
async def test_process_invalid_input(knowledge_extractor):
    """Test processing with invalid input."""
    with pytest.raises(ValueError):
        await knowledge_extractor.process({"wrong_key": "text"})

@pytest.mark.asyncio
async def test_extract_skills(knowledge_extractor):
    """Test skill extraction functionality."""
    doc = knowledge_extractor.nlp("Experienced in Python, JavaScript, and Docker.")
    skills = await knowledge_extractor._extract_skills(doc)
    assert isinstance(skills, list)

@pytest.mark.asyncio
async def test_extract_experience(knowledge_extractor):
    """Test experience extraction functionality."""
    doc = knowledge_extractor.nlp("Senior Software Engineer at Tech Corp from 2020 to Present")
    experience = await knowledge_extractor._extract_experience(doc)
    assert isinstance(experience, list)

@pytest.mark.asyncio
async def test_extract_education(knowledge_extractor):
    """Test education extraction functionality."""
    doc = knowledge_extractor.nlp("Master of Computer Science from University of Technology")
    education = await knowledge_extractor._extract_education(doc)
    assert isinstance(education, list)

@pytest.mark.asyncio
async def test_extract_contact_info(knowledge_extractor):
    """Test contact information extraction functionality."""
    doc = knowledge_extractor.nlp("Email: john@example.com, Phone: (123) 456-7890")
    contact_info = await knowledge_extractor._extract_contact_info(doc)
    assert isinstance(contact_info, dict) 