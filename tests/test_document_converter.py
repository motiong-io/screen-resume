import pytest
from pathlib import Path
import os
from agents.document_converter import DocumentConverterAgent

@pytest.fixture
def document_converter():
    return DocumentConverterAgent()

@pytest.fixture
def sample_pdf(tmp_path):
    # Create a sample PDF file for testing
    pdf_path = tmp_path / "test.pdf"
    with open(pdf_path, "wb") as f:
        # Create minimal PDF content
        f.write(b"%PDF-1.7\n%\x93\x8C\x8B\x9E\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF")
    return str(pdf_path)

@pytest.fixture
def sample_docx(tmp_path):
    # Create a sample DOCX file for testing
    from docx import Document
    doc = Document()
    doc.add_paragraph("Test content")
    docx_path = tmp_path / "test.docx"
    doc.save(str(docx_path))
    return str(docx_path)

@pytest.mark.asyncio
async def test_validate_pdf(document_converter, sample_pdf):
    """Test validation of PDF files."""
    assert await document_converter.validate(sample_pdf)

@pytest.mark.asyncio
async def test_validate_docx(document_converter, sample_docx):
    """Test validation of DOCX files."""
    assert await document_converter.validate(sample_docx)

@pytest.mark.asyncio
async def test_validate_invalid_format(document_converter, tmp_path):
    """Test validation of unsupported file format."""
    invalid_file = tmp_path / "test.txt"
    invalid_file.write_text("test content")
    assert not await document_converter.validate(str(invalid_file))

@pytest.mark.asyncio
async def test_process_pdf(document_converter, sample_pdf):
    """Test processing of PDF files."""
    result = await document_converter.process(sample_pdf)
    assert isinstance(result, dict)
    assert "text" in result
    assert "format" in result
    assert result["format"] == "pdf"

@pytest.mark.asyncio
async def test_process_docx(document_converter, sample_docx):
    """Test processing of DOCX files."""
    result = await document_converter.process(sample_docx)
    assert isinstance(result, dict)
    assert "text" in result
    assert "format" in result
    assert result["format"] == "docx"
    assert "Test content" in result["text"]

@pytest.mark.asyncio
async def test_process_invalid_format(document_converter, tmp_path):
    """Test processing of unsupported file format."""
    invalid_file = tmp_path / "test.txt"
    invalid_file.write_text("test content")
    with pytest.raises(ValueError):
        await document_converter.process(str(invalid_file)) 