# main_free.py - Temporary version using free analysis

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
# Import the free version instead of OpenAI version
from backend.analyzer_free import analyze_uploaded_file, get_document_statistics
import uvicorn
import os
import tempfile

app = FastAPI()

# Allow requests from frontend (CORS setup)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def simple_summarize(text: str) -> str:
    """Simple text summarization without AI"""
    sentences = text.split('.')
    # Take first few sentences and last few sentences
    if len(sentences) > 10:
        summary_sentences = sentences[:3] + ["..."] + sentences[-2:]
    else:
        summary_sentences = sentences[:5]
    
    summary = '. '.join(s.strip() for s in summary_sentences if s.strip())
    return f"Document Summary (Basic):\n\n{summary}\n\nNote: This is a basic summary. For detailed AI analysis, please add credits to your OpenAI account."

def simple_warranty_analysis(text: str) -> dict:
    """Simple warranty analysis without AI"""
    text_lower = text.lower()
    
    warranties_found = []
    guarantees_found = []
    
    if 'warrant' in text_lower:
        warranties_found.append("Warranty terms detected")
    if 'guarantee' in text_lower:
        guarantees_found.append("Guarantee terms detected")
    
    disclaimers = []
    if 'disclaim' in text_lower:
        disclaimers.append("Disclaimer clauses found")
    if 'as-is' in text_lower:
        disclaimers.append("'As-is' terms found")
    
    # Risk assessment
    high_risk_terms = ['disclaim', 'as-is', 'no warranty', 'limitation of liability']
    risk_level = "Low"
    
    if any(term in text_lower for term in high_risk_terms):
        risk_level = "High"
    elif any(term in text_lower for term in ['limited warranty', 'conditional']):
        risk_level = "Medium"
    
    analysis = f"""
Warranty Analysis (Rule-based):

Warranties Found: {len(warranties_found)} clauses
Guarantees Found: {len(guarantees_found)} clauses
Disclaimers Found: {len(disclaimers)} items
Risk Level: {risk_level}

Note: This is a basic rule-based analysis. For detailed AI analysis, please add credits to your OpenAI account.
"""
    
    return {
        "analysis": analysis,
        "summary": {
            "has_warranties": len(warranties_found) > 0,
            "has_guarantees": len(guarantees_found) > 0,
            "risk_level": risk_level
        }
    }

def simple_compliance_check(clauses: list) -> dict:
    """Simple compliance check without AI"""
    issues = []
    recommendations = []
    
    warranty_clauses = [c for c in clauses if c.get("has_warranty_terms", False)]
    
    if not warranty_clauses:
        recommendations.append("No warranty clauses detected. Consider if warranty terms are needed.")
    else:
        recommendations.append(f"Found {len(warranty_clauses)} warranty-related clauses")
        
        for clause in warranty_clauses:
            text = clause.get("clause", "").lower()
            if 'disclaim' in text and 'notice' not in text:
                issues.append("Potential issue: Disclaimer without proper notice")
    
    return {
        "compliance_issues": issues,
        "recommendations": recommendations,
        "total_issues": len(issues)
    }

@app.post("/analyze/")
async def analyze_document(file: UploadFile = File(...)):
    """Standard document analysis using rule-based approach"""
    content = await file.read()
    result = analyze_uploaded_file(file.filename, content)
    return {"clauses": result}

@app.post("/summarize/")
async def summarize_document(payload: dict):
    """Simple text summarization"""
    full_text = payload.get("text", "")
    summary = simple_summarize(full_text)
    return {"summary": summary}

@app.post("/grantie/analyze/")
async def analyze_warranties(payload: dict):
    """Simple warranty analysis"""
    text = payload.get("text", "")
    if not text:
        return {"error": "No text provided for analysis"}
    
    result = simple_warranty_analysis(text)
    return {"grantie_analysis": result}

@app.post("/grantie/compliance/")
async def check_compliance(payload: dict):
    """Simple compliance check"""
    clauses = payload.get("clauses", [])
    if not clauses:
        return {"error": "No clauses provided for compliance check"}
    
    compliance_result = simple_compliance_check(clauses)
    return {"compliance": compliance_result}

@app.post("/grantie/full-analysis/")
async def full_grantie_analysis(file: UploadFile = File(...)):
    """Complete analysis using rule-based approach"""
    content = await file.read()
    
    # Analyze the document clauses
    clauses_result = analyze_uploaded_file(file.filename, content)
    
    # Extract full text for warranty analysis
    full_text = " ".join([clause["clause"] for clause in clauses_result])
    
    # Analyze warranties and guarantees
    warranty_analysis = simple_warranty_analysis(full_text)
    
    # Check compliance
    compliance_result = simple_compliance_check(clauses_result)
    
    return {
        "clauses": clauses_result,
        "warranty_analysis": warranty_analysis,
        "compliance": compliance_result,
        "filename": file.filename
    }

@app.post("/speak/")
async def text_to_speech_endpoint(payload: dict):
    """Text-to-speech endpoint (disabled in free version)"""
    return {"error": "Text-to-speech requires ElevenLabs API. Please add TTS credits to enable this feature."}

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Legal Document Analyzer (Free Version) is running!"}

if __name__ == "__main__":
    uvicorn.run("main_free:app", host="127.0.0.1", port=8000, reload=True)