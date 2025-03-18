import pytest
import os
import tempfile
from pathlib import Path

@pytest.fixture(scope="session")
def test_data_dir():
    """Create a temporary directory for test data."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)

@pytest.fixture(scope="session")
def sample_files(test_data_dir):
    """Create sample files for testing."""
    # Create sample PDF
    pdf_path = test_data_dir / "sample.pdf"
    with open(pdf_path, "wb") as f:
        f.write(b"%PDF-1.7\n%\x93\x8C\x8B\x9E\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF")
    
    # Create sample DOCX
    from docx import Document
    doc = Document()
    doc.add_paragraph("Sample resume content")
    docx_path = test_data_dir / "sample.docx"
    doc.save(str(docx_path))
    
    return {
        "pdf": str(pdf_path),
        "docx": str(docx_path)
    }

@pytest.fixture(scope="session")
def sample_resume_text():
    """Sample resume text for testing."""
    return """
    John Doe
    Software Engineer
    
    Contact:
    Email: john@example.com
    Phone: (123) 456-7890
    
    Summary:
    Experienced software engineer with expertise in Python and cloud technologies.
    
    Skills:
    - Python, JavaScript, TypeScript
    - AWS, Docker, Kubernetes
    - React, Node.js, FastAPI
    - CI/CD, Git, Agile
    
    Experience:
    Senior Software Engineer | Tech Corp | 2020-Present
    - Led development of microservices architecture
    - Managed team of 5 developers
    - Implemented CI/CD pipelines
    
    Software Engineer | StartUp Inc | 2018-2020
    - Developed React applications
    - Optimized database performance
    
    Education:
    Master of Computer Science
    University of Technology
    2018
    
    Bachelor of Computer Science
    State University
    2016
    """

@pytest.fixture(scope="session")
def sample_job_description():
    """Sample job description for testing."""
    return """
    Senior Software Engineer
    
    About Us:
    Tech Corp is seeking a Senior Software Engineer to join our Cloud Platform team.
    
    Required Skills:
    - Expert in Python and JavaScript
    - Strong experience with AWS and cloud infrastructure
    - Knowledge of microservices architecture
    - Experience with Docker and Kubernetes
    
    Responsibilities:
    - Design and implement scalable microservices
    - Lead technical projects and mentor junior developers
    - Collaborate with cross-functional teams
    - Optimize system performance
    
    Requirements:
    - 5+ years of software development experience
    - Bachelor's degree in Computer Science or related field
    - Previous experience leading technical teams
    
    Industry: Technology
    Location: Remote
    """ 