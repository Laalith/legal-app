from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from backend.analyzer import analyze_uploaded_file
from backend.logic.summarizer import summarize_text
from backend.logic.grantie import analyze_warranties_and_guarantees, check_warranty_compliance
from backend.logic.tts import text_to_speech
import uvicorn
import os
import tempfile

app = FastAPI()

# Allow requests from frontend (CORS setup)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this to frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze/")
async def analyze_document(file: UploadFile = File(...)):
    """
    Accepts a file upload (e.g., .docx), analyzes its content,
    and returns clause-wise interpretation using OpenAI.
    """
    content = await file.read()
    result = analyze_uploaded_file(file.filename, content)
    return {"clauses": result}

@app.post("/summarize/")
async def summarize_document(payload: dict):
    """
    Summarize the entire document text.
    """
    full_text = payload.get("text", "")
    summary = summarize_text(full_text)
    return {"summary": summary}

@app.post("/grantie/analyze/")
async def analyze_warranties(payload: dict):
    """
    Analyze warranties and guarantees in the document text.
    """
    text = payload.get("text", "")
    if not text:
        return {"error": "No text provided for analysis"}
    
    result = analyze_warranties_and_guarantees(text)
    return {"grantie_analysis": result}

@app.post("/grantie/compliance/")
async def check_compliance(payload: dict):
    """
    Check warranty compliance for analyzed clauses.
    """
    clauses = payload.get("clauses", [])
    if not clauses:
        return {"error": "No clauses provided for compliance check"}
    
    compliance_result = check_warranty_compliance(clauses)
    return {"compliance": compliance_result}

@app.post("/grantie/full-analysis/")
async def full_grantie_analysis(file: UploadFile = File(...)):
    """
    Complete Grantie analysis: upload file, analyze clauses, check warranties and compliance.
    """
    content = await file.read()
    
    # First, analyze the document clauses
    clauses_result = analyze_uploaded_file(file.filename, content)
    
    # Extract full text for warranty analysis
    full_text = " ".join([clause["clause"] for clause in clauses_result])
    
    # Analyze warranties and guarantees
    warranty_analysis = analyze_warranties_and_guarantees(full_text)
    
    # Check compliance
    compliance_result = check_warranty_compliance(clauses_result)
    
    return {
        "clauses": clauses_result,
        "warranty_analysis": warranty_analysis,
        "compliance": compliance_result,
        "filename": file.filename
    }

@app.post("/speak/")
async def text_to_speech_endpoint(payload: dict):
    """
    Convert text to speech and return audio file.
    """
    text = payload.get("text", "")
    if not text:
        return {"error": "No text provided for TTS"}
    
    try:
        # Generate audio file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_audio:
            audio_path = text_to_speech(text, tmp_audio.name)
            
            # Return the audio file
            return FileResponse(
                audio_path,
                media_type="audio/mpeg",
                filename="speech.mp3",
                background=lambda: os.unlink(audio_path)  # Clean up after sending
            )
    except Exception as e:
        return {"error": f"TTS generation failed: {str(e)}"}

@app.get("/")
async def root():
    """
    Health check endpoint.
    """
    return {"message": "Legal Document Analyzer with Grantie is running!"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)