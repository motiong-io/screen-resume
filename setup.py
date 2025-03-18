from setuptools import setup, find_packages

setup(
    name="resume-screening",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.100.0",
        "uvicorn>=0.23.0",
        "pydantic>=2.0.0",
        "python-multipart>=0.0.6",
        "langchain>=0.1.0",
        "python-dotenv>=1.0.0",
        "openai>=1.0.0",
        "pypdf2>=3.0.0",
        "python-docx>=0.8.11",
        "spacy>=3.7.2",
        "pandas>=2.0.0",
        "scikit-learn>=1.3.0",
        "sqlalchemy>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.1.0",
            "httpx>=0.24.0",
        ],
    },
) 