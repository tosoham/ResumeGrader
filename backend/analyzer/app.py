from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import uuid
import aiofiles
from typing import Dict, Any
import logging
from utils.resume_parser import ResumeParser

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

origins = [
    "https://resume-grader-v51v-pi.vercel.app/",  # production
    "http://localhost:5173",             # Vite dev server
]

app = FastAPI(
    title="Resume Grader API",
    description="A FastAPI backend for parsing and grading resumes using Sarvam AI",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


resume_parser = ResumeParser()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Resume Grader API is running", "status": "healthy"}

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "service": "Resume Grader API",
        "version": "1.0.0"
    }

@app.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    """
    Upload and parse a resume PDF file
    """
    try:
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=400, 
                detail="Only PDF files are supported"
            )
        
        file_id = str(uuid.uuid4())
        file_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")
        
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        logger.info(f"File saved: {file_path}")
        
        parsed_data = await resume_parser.parse_resume(file_path)
        
        os.remove(file_path)
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "file_id": file_id,
                "filename": file.filename,
                "parsed_data": parsed_data
            }
        )
        
    except Exception as e:
        logger.error(f"Error processing resume: {str(e)}")
        
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
            
        raise HTTPException(
            status_code=500,
            detail=f"Error processing resume: {str(e)}"
        )

@app.post("/grade-resume")
async def grade_resume(file: UploadFile = File(...)):
    """
    Upload, parse, and grade a resume PDF file
    """
    try:
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=400, 
                detail="Only PDF files are supported"
            )
        
        file_id = str(uuid.uuid4())
        file_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")

        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        logger.info(f"File saved for grading: {file_path}")
        grading_result = await resume_parser.grade_resume(file_path)
        
        os.remove(file_path)
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "file_id": file_id,
                "filename": file.filename,
                "grading_result": grading_result
            }
        )
        
    except Exception as e:
        logger.error(f"Error grading resume: {str(e)}")
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
            
        raise HTTPException(
            status_code=500,
            detail=f"Error grading resume: {str(e)}"
        )

@app.get("/resume/{file_id}")
async def get_resume_analysis(file_id: str):
    """
    Get analysis results for a previously uploaded resume
    """
    return {
        "file_id": file_id,
        "message": "Resume analysis retrieval not implemented yet"
    }

@app.delete("/resume/{file_id}")
async def delete_resume(file_id: str):
    """
    Delete a resume file and its analysis
    """
    try:
        deleted_files = []
        for filename in os.listdir(UPLOAD_DIR):
            if filename.startswith(file_id):
                file_path = os.path.join(UPLOAD_DIR, filename)
                os.remove(file_path)
                deleted_files.append(filename)
        
        if not deleted_files:
            raise HTTPException(
                status_code=404,
                detail="Resume file not found"
            )
        
        return {
            "success": True,
            "message": f"Deleted {len(deleted_files)} file(s)",
            "deleted_files": deleted_files
        }
        
    except Exception as e:
        logger.error(f"Error deleting resume: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting resume: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)