import asyncio
import os
import tempfile
from typing import Dict, Any, List
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from docx import Document
from pdf2docx import Converter
import PyPDF2
import io
import logging
import json
from datetime import datetime
import shutil

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# WebSocket connections store
active_connections: List[WebSocket] = []

# Define asset directories
ASSETS_DIR = "assets"
JD_DIR = os.path.join(ASSETS_DIR, "job")
RESUME_DIR = os.path.join(ASSETS_DIR, "resume")
LOGS_DIR = os.path.join(ASSETS_DIR, "logs")
RESULTS_DIR = os.path.join(ASSETS_DIR, "results")  # New directory for results

# Create directories if they don't exist
os.makedirs(JD_DIR, exist_ok=True)
os.makedirs(RESUME_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)  # Create results directory

class WebSocketLogger:
    def __init__(self):
        self.connections = active_connections
        self.current_log_file = None
        self.start_new_log_file()

    def start_new_log_file(self):
        """Start a new log file with timestamp."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.current_log_file = os.path.join(LOGS_DIR, f"screening_{timestamp}.log")
        # Write header to log file
        with open(self.current_log_file, 'w', encoding='utf-8') as f:
            f.write(f"=== Screening Session Started at {datetime.now().isoformat()} ===\n\n")

    async def log(self, message: str, level: str = "info"):
        """Log message to both WebSocket and file."""
        timestamp = datetime.now().isoformat()
        log_entry = {
            "message": message,
            "level": level,
            "timestamp": timestamp
        }

        # Send to WebSocket
        for connection in self.connections:
            try:
                await connection.send_json(log_entry)
            except Exception as e:
                logger.error(f"Error sending log to WebSocket: {str(e)}")

        # Write to file
        try:
            with open(self.current_log_file, 'a', encoding='utf-8') as f:
                f.write(f"[{timestamp}] [{level.upper()}] {message}\n")
        except Exception as e:
            logger.error(f"Error writing to log file: {str(e)}")

    def get_log_files(self) -> List[str]:
        """Get list of all log files."""
        try:
            return [f for f in os.listdir(LOGS_DIR) if f.endswith('.log')]
        except Exception as e:
            logger.error(f"Error listing log files: {str(e)}")
            return []

    def get_log_content(self, filename: str) -> str:
        """Get content of a specific log file."""
        try:
            file_path = os.path.join(LOGS_DIR, filename)
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            return "Log file not found"
        except Exception as e:
            logger.error(f"Error reading log file: {str(e)}")
            return f"Error reading log file: {str(e)}"

ws_logger = WebSocketLogger()

from agents.document_converter import DocumentConverterAgent
from agents.knowledge_extractor import KnowledgeExtractorAgent
from agents.decision_maker import DecisionMakerAgent
from agents.jd_analyzer import JDAnalyzerAgent
from agents.pdf_parser import PDFParserAgent

app = FastAPI(title="Resume Screening System")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React app's address
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Initialize agents
document_converter = DocumentConverterAgent()
knowledge_extractor = KnowledgeExtractorAgent()
decision_maker = DecisionMakerAgent()
jd_analyzer = JDAnalyzerAgent()
pdf_parser = PDFParserAgent()

async def convert_docx_to_pdf(file_content: bytes) -> str:
    """Convert DOCX content to text directly."""
    docx_file = io.BytesIO(file_content)
    doc = Document(docx_file)
    return "\n".join([paragraph.text for paragraph in doc.paragraphs])

async def extract_text_from_pdf(pdf_content: bytes) -> str:
    """Extract text from PDF content."""
    try:
        # First try to use the external API parser
        result = await pdf_parser.parse_pdf(pdf_content)
        if isinstance(result, dict) and "text" in result:
            return result["text"]
        # If the API doesn't return text in expected format, log and fall back to PyPDF2
        logger.info("External PDF parser didn't return text field, falling back to PyPDF2")
    except Exception as e:
        # Log the error and fall back to PyPDF2
        logger.warning(f"Error using external PDF parser: {str(e)}. Falling back to PyPDF2")
    
    # Fall back to original PyPDF2 method
    pdf_file = io.BytesIO(pdf_content)
    reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

async def process_file(file: UploadFile) -> str:
    """Process uploaded file: convert if needed and extract text."""
    content = await file.read()
    
    if file.filename.lower().endswith('.docx'):
        # Convert DOCX directly to text
        return await convert_docx_to_pdf(content)
    
    if file.filename.lower().endswith('.pdf'):
        # Extract text from PDF
        return await extract_text_from_pdf(content)
    
    raise ValueError(f"Unsupported file type: {file.filename}")

@app.post("/screen")
async def screen_resumes(
    jd_file: UploadFile = File(...),
    resume_files: List[UploadFile] = File(...)
) -> Dict[str, Any]:
    """Screen resumes against a job description."""
    
    try:
        # Validate file types
        allowed_types = ['.pdf', '.docx']
        if not any(jd_file.filename.lower().endswith(ext) for ext in allowed_types):
            raise HTTPException(status_code=400, detail=f"Job description file must be one of: {allowed_types}")
        
        for resume in resume_files:
            if not any(resume.filename.lower().endswith(ext) for ext in allowed_types):
                raise HTTPException(status_code=400, detail=f"Resume file {resume.filename} must be one of: {allowed_types}")

        # Log incoming files
        logger.info(f"Processing JD file: {jd_file.filename}")
        logger.info(f"Processing {len(resume_files)} resume files")

        # Process job description
        jd_text = await process_file(jd_file)
        if not jd_text:
            raise HTTPException(status_code=400, detail="Could not extract text from job description file")
            
        job_requirements = await jd_analyzer.process({"text": jd_text})
        
        # Process resumes
        candidates = []
        for resume_file in resume_files:
            try:
                logger.info(f"Processing resume: {resume_file.filename}")
                # Convert and extract text from resume
                resume_text = await process_file(resume_file)
                if not resume_text:
                    logger.warning(f"Could not extract text from {resume_file.filename}")
                    continue
                
                # Extract information from resume
                candidate_info = await knowledge_extractor.process({"text": resume_text})
                
                # Evaluate candidate
                evaluation = await decision_maker.process({
                    "candidate_info": candidate_info,
                    "job_requirements": job_requirements
                })
                
                candidates.append({
                    "file_name": resume_file.filename,
                    "candidate_info": candidate_info,
                    "evaluation": evaluation
                })
            except Exception as e:
                logger.error(f"Error processing {resume_file.filename}: {str(e)}")
                continue
        
        if not candidates:
            raise HTTPException(status_code=400, detail="No valid resumes could be processed")

        # Sort candidates by overall score
        candidates.sort(key=lambda x: x["evaluation"]["overall_score"], reverse=True)
        
        return {
            "candidates": candidates,
            "job_requirements": job_requirements
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error in screen_resumes: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/list-files")
async def list_files():
    """List all JD and resume files from assets directories."""
    try:
        # Get JD files
        jd_files = [f for f in os.listdir(JD_DIR) 
                   if f.lower().endswith(('.pdf', '.docx'))]
        
        # Get resume files
        resume_files = [f for f in os.listdir(RESUME_DIR) 
                       if f.lower().endswith(('.pdf', '.docx'))]
        
        return {
            "jd_files": jd_files,
            "resume_files": resume_files
        }
    except Exception as e:
        logger.error(f"Error listing files: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

class ScreeningRequest(BaseModel):
    jd_filename: str
    resume_filenames: List[str]

class RenameRequest(BaseModel):
    new_name: str

class ScreeningResult:
    def __init__(self):
        self.current_result_file = None

    def save_result(self, result: Dict[str, Any], jd_filename: str) -> str:
        """Save screening result to a JSON file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result_filename = f"screening_{timestamp}_{os.path.splitext(jd_filename)[0]}.json"
        result_path = os.path.join(RESULTS_DIR, result_filename)
        
        # Add metadata to result
        result_with_metadata = {
            "timestamp": datetime.now().isoformat(),
            "jd_file": jd_filename,
            "result": result
        }
        
        with open(result_path, 'w', encoding='utf-8') as f:
            json.dump(result_with_metadata, f, ensure_ascii=False, indent=2)
        
        self.current_result_file = result_filename
        return result_filename

    def get_result(self, filename: str) -> Dict[str, Any]:
        """Get a specific screening result."""
        result_path = os.path.join(RESULTS_DIR, filename)
        if not os.path.exists(result_path):
            raise FileNotFoundError(f"Result file not found: {filename}")
            
        with open(result_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def list_results(self) -> List[Dict[str, Any]]:
        """List all screening results with metadata."""
        results = []
        for filename in os.listdir(RESULTS_DIR):
            if filename.endswith('.json'):
                try:
                    result = self.get_result(filename)
                    results.append({
                        "filename": filename,
                        "timestamp": result["timestamp"],
                        "jd_file": result["jd_file"]
                    })
                except Exception as e:
                    logger.error(f"Error reading result file {filename}: {str(e)}")
        
        # Sort by timestamp, newest first
        results.sort(key=lambda x: x["timestamp"], reverse=True)
        return results

screening_result = ScreeningResult()

@app.post("/screen-from-assets")
async def screen_resumes_from_assets(request: ScreeningRequest) -> Dict[str, Any]:
    """Screen resumes using files from assets directories."""
    try:
        await ws_logger.log(f"Starting screening process...")
        await ws_logger.log(f"Processing JD: {request.jd_filename}")
        await ws_logger.log(f"Processing Resumes: {', '.join(request.resume_filenames)}")
        
        # Validate JD file
        jd_path = os.path.join(JD_DIR, request.jd_filename)
        if not os.path.exists(jd_path):
            await ws_logger.log(f"JD file not found: {request.jd_filename}", "error")
            raise HTTPException(status_code=404, detail=f"JD file not found: {request.jd_filename}")
        
        # Validate resume files
        resume_paths = [os.path.join(RESUME_DIR, fname) for fname in request.resume_filenames]
        for path in resume_paths:
            if not os.path.exists(path):
                await ws_logger.log(f"Resume file not found: {os.path.basename(path)}", "error")
                raise HTTPException(status_code=404, detail=f"Resume file not found: {os.path.basename(path)}")
        
        # Process JD
        try:
            with open(jd_path, 'rb') as f:
                jd_content = f.read()
                await ws_logger.log(f"Reading JD file: {request.jd_filename}")
                jd_text = await process_file_content(jd_content, request.jd_filename)
                await ws_logger.log("Analyzing job requirements...")
                job_requirements = await jd_analyzer.process({"text": jd_text})
                await ws_logger.log("Successfully analyzed job requirements", "success")
                await ws_logger.log(f"Job Requirements:\n{json.dumps(job_requirements, indent=2, ensure_ascii=False)}")
        except Exception as e:
            await ws_logger.log(f"Error processing JD file: {str(e)}", "error")
            raise HTTPException(status_code=500, detail=f"Error processing JD file: {str(e)}")
        
        # Process resumes
        candidates = []
        for resume_path in resume_paths:
            try:
                await ws_logger.log(f"Processing resume: {os.path.basename(resume_path)}")
                with open(resume_path, 'rb') as f:
                    resume_content = f.read()
                    resume_text = await process_file_content(resume_content, os.path.basename(resume_path))
                
                await ws_logger.log(f"Extracting information from resume...")
                candidate_info = await knowledge_extractor.process({"text": resume_text})
                await ws_logger.log(f"Successfully extracted candidate information", "success")
                await ws_logger.log(f"Candidate Information:\n{json.dumps(candidate_info, indent=2, ensure_ascii=False)}")
                
                await ws_logger.log(f"Evaluating candidate...")
                evaluation = await decision_maker.process({
                    "candidate_info": candidate_info,
                    "job_requirements": job_requirements
                })
                await ws_logger.log(f"Successfully evaluated candidate", "success")
                await ws_logger.log(f"Evaluation Results:\n{json.dumps(evaluation, indent=2, ensure_ascii=False)}")
                
                candidates.append({
                    "file_name": os.path.basename(resume_path),
                    "candidate_info": candidate_info,
                    "evaluation": evaluation
                })
            except Exception as e:
                await ws_logger.log(f"Error processing resume {os.path.basename(resume_path)}: {str(e)}", "error")
                continue
        
        if not candidates:
            await ws_logger.log("No valid resumes could be processed", "error")
            raise HTTPException(status_code=400, detail="No valid resumes could be processed")
        
        candidates.sort(key=lambda x: x["evaluation"]["overall_score"], reverse=True)
        await ws_logger.log("Successfully completed screening process", "success")
        
        result = {
            "candidates": candidates,
            "job_requirements": job_requirements
        }
        
        # Save the result
        result_filename = screening_result.save_result(result, request.jd_filename)
        await ws_logger.log(f"Saved screening result to: {result_filename}", "success")
        
        return result
    except HTTPException as he:
        raise he
    except Exception as e:
        await ws_logger.log(f"Error in screening process: {str(e)}", "error")
        raise HTTPException(status_code=500, detail=str(e))

async def process_file_content(content: bytes, filename: str) -> str:
    """Process file content based on file extension."""
    try:
        await ws_logger.log(f"Processing file content for: {filename}")
        if filename.lower().endswith('.docx'):
            text = await convert_docx_to_pdf(content)
        elif filename.lower().endswith('.pdf'):
            text = await extract_text_from_pdf(content)
        else:
            raise ValueError(f"Unsupported file type: {filename}")
        
        if not text:
            await ws_logger.log(f"Failed to extract text from {filename}", "error")
            raise ValueError(f"Failed to extract text from {filename}")
            
        await ws_logger.log(f"Successfully processed file content for: {filename}", "success")
        # Log the first 200 characters of extracted text
        preview = text#[:200] + "..." if len(text) > 200 else text
        await ws_logger.log(f"Extracted text preview:\n{preview}")
        return text
    except Exception as e:
        await ws_logger.log(f"Error processing file content for {filename}: {str(e)}", "error")
        raise

@app.post("/upload-jd")
async def upload_jd(file: UploadFile = File(...)):
    """Upload a job description file to assets/job directory."""
    return await upload_file(file, JD_DIR)

@app.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    """Upload a resume file to assets/resume directory."""
    return await upload_file(file, RESUME_DIR)

async def upload_file(file: UploadFile, directory: str):
    """Helper function to handle file uploads."""
    if not file.filename.lower().endswith(('.pdf', '.docx')):
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are allowed")
    
    try:
        file_path = os.path.join(directory, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return {"filename": file.filename}
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/delete-file/{type}/{filename}")
async def delete_file(type: str, filename: str):
    """Delete a file from the assets directory."""
    if type not in ['jd', 'resume']:
        raise HTTPException(status_code=400, detail="Invalid file type")
    
    directory = JD_DIR if type == 'jd' else RESUME_DIR
    file_path = os.path.join(directory, filename)
    
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return {"message": "File deleted successfully"}
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        logger.error(f"Error deleting file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/rename-file/{type}/{old_name}")
async def rename_file(type: str, old_name: str, request: RenameRequest):
    """Rename a file in the assets directory."""
    if type not in ['jd', 'resume']:
        raise HTTPException(status_code=400, detail="Invalid file type")
    
    directory = JD_DIR if type == 'jd' else RESUME_DIR
    old_path = os.path.join(directory, old_name)
    new_path = os.path.join(directory, request.new_name)
    
    if not os.path.exists(old_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    if os.path.exists(new_path):
        raise HTTPException(status_code=400, detail="A file with this name already exists")
    
    try:
        os.rename(old_path, new_path)
        return {"message": "File renamed successfully"}
    except Exception as e:
        logger.error(f"Error renaming file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            # Keep the connection alive
            await websocket.receive_text()
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
    finally:
        active_connections.remove(websocket)

@app.post("/parse-pdf")
async def parse_pdf(file: UploadFile = File(...)) -> Dict[str, Any]:
    """Parse PDF file using external API."""
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    try:
        content = await file.read()
        result = await pdf_parser.parse_pdf(content)
        return result
    except Exception as e:
        logger.error(f"Error parsing PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/preview-file/{type}/{filename}")
async def preview_file(type: str, filename: str):
    """Preview file content."""
    if type not in ['jd', 'resume']:
        raise HTTPException(status_code=400, detail="Invalid file type")
    
    directory = JD_DIR if type == 'jd' else RESUME_DIR
    file_path = os.path.join(directory, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        content = await process_file(UploadFile(filename=filename, file=open(file_path, 'rb')))
        return content
    except Exception as e:
        logger.error(f"Error previewing file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/list-logs")
async def list_logs():
    """List all log files."""
    try:
        log_files = ws_logger.get_log_files()
        return {"log_files": log_files}
    except Exception as e:
        logger.error(f"Error listing logs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get-log/{filename}")
async def get_log(filename: str):
    """Get content of a specific log file."""
    try:
        content = ws_logger.get_log_content(filename)
        return {"content": content}
    except Exception as e:
        logger.error(f"Error getting log content: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/list-results")
async def list_results():
    """List all screening results."""
    try:
        results = screening_result.list_results()
        return {"results": results}
    except Exception as e:
        logger.error(f"Error listing results: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get-result/{filename}")
async def get_result(filename: str):
    """Get a specific screening result."""
    try:
        result = screening_result.get_result(filename)
        return result
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Result not found")
    except Exception as e:
        logger.error(f"Error getting result: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 