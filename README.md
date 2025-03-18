# Multi-Agent Resume Screening System

A sophisticated resume screening system that uses multiple AI agents to analyze job descriptions and evaluate candidate resumes.

## Features

- Document conversion support for PDF and DOCX formats
- Intelligent job description analysis and breakdown
- Advanced resume information extraction
- ML-based candidate evaluation
- RESTful API interface

## System Architecture

The system consists of four main agents:

1. **Document Converter Agent**: Handles conversion of PDF and DOCX files to text
2. **Knowledge Extractor Agent**: Extracts key information from resumes using NLP
3. **Decision Maker Agent**: Evaluates candidates against job requirements
4. **JD Analyzer Agent**: Breaks down job descriptions into structured criteria

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd resume-screening-system
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Download the required spaCy model:
```bash
python -m spacy download en_core_web_lg
```

## Usage

1. Start the server:
```bash
python main.py
```

2. The API will be available at `http://localhost:8000`

3. Use the `/screen` endpoint to screen resumes:
```bash
curl -X POST "http://localhost:8000/screen" \
     -H "Content-Type: application/json" \
     -d '{"jd_file": "path/to/jd.pdf", "resume_files": ["path/to/resume1.pdf", "path/to/resume2.pdf"]}'
```

## API Documentation

Once the server is running, visit `http://localhost:8000/docs` for the interactive API documentation.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 