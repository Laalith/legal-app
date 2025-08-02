# backend/analyzer_free.py - Alternative using free API (Hugging Face)

import tempfile
from docx import Document
from dotenv import load_dotenv
import os
import logging
import requests
import json

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

def extract_clauses_from_docx(file_path):
    """
    Extract paragraphs (legal clauses) from a DOCX file.
    """
    try:
        doc = Document(file_path)
        clauses = [para.text.strip() for para in doc.paragraphs if para.text.strip()]
        logger.info(f"Extracted {len(clauses)} clauses from document")
        return clauses
    except Exception as e:
        logger.error(f"Error extracting clauses from DOCX: {str(e)}")
        raise Exception(f"Failed to read document: {str(e)}")

def analyze_clause_simple(clause):
    """
    Simple rule-based analysis when AI APIs are not available.
    """
    analysis = "Legal Clause Analysis:\n\n"
    
    # Basic keyword analysis
    clause_lower = clause.lower()
    
    # Identify clause type
    if any(word in clause_lower for word in ['shall', 'must', 'required']):
        analysis += "• This appears to be a mandatory obligation clause.\n"
    
    if any(word in clause_lower for word in ['may', 'can', 'permitted']):
        analysis += "• This clause grants permissions or rights.\n"
    
    if any(word in clause_lower for word in ['terminate', 'end', 'cancel']):
        analysis += "• This relates to termination or cancellation.\n"
    
    if any(word in clause_lower for word in ['payment', 'pay', 'fee', 'cost']):
        analysis += "• This clause involves financial obligations.\n"
    
    if any(word in clause_lower for word in ['liability', 'responsible', 'damages']):
        analysis += "• This clause addresses liability and responsibility.\n"
    
    if any(word in clause_lower for word in ['confidential', 'non-disclosure', 'proprietary']):
        analysis += "• This relates to confidentiality and information protection.\n"
    
    # Risk assessment
    high_risk_terms = ['penalty', 'breach', 'default', 'liability', 'damages', 'terminate']
    medium_risk_terms = ['obligation', 'requirement', 'must', 'shall']
    
    if any(term in clause_lower for term in high_risk_terms):
        analysis += "\n⚠️ HIGH RISK: This clause may have significant consequences if not followed.\n"
    elif any(term in clause_lower for term in medium_risk_terms):
        analysis += "\n⚠️ MEDIUM RISK: This clause creates specific obligations.\n"
    else:
        analysis += "\n✅ LOW RISK: This appears to be an informational or standard clause.\n"
    
    # General advice
    analysis += "\n💡 Recommendation: Consider consulting with a legal professional for detailed interpretation."
    
    return analysis

def analyze_clause_for_grantie_simple(clause):
    """
    Simple warranty/guarantee analysis.
    """
    analysis = "Warranty & Guarantee Analysis:\n\n"
    clause_lower = clause.lower()
    
    # Check for warranties
    if any(word in clause_lower for word in ['warrant', 'warranty']):
        analysis += "• WARRANTY FOUND: This clause contains warranty terms.\n"
        if 'disclaim' in clause_lower or 'no warranty' in clause_lower:
            analysis += "  - Contains warranty disclaimers\n"
            analysis += "  - Risk Level: HIGH - Limited protection\n"
        else:
            analysis += "  - Risk Level: MEDIUM - Review warranty scope\n"
    
    # Check for guarantees
    if any(word in clause_lower for word in ['guarantee', 'assure', 'promise']):
        analysis += "• GUARANTEE FOUND: This clause contains guarantee terms.\n"
    
    # Check for disclaimers
    if any(word in clause_lower for word in ['as-is', 'disclaim', 'limitation']):
        analysis += "• DISCLAIMER FOUND: This clause limits liability or warranties.\n"
        analysis += "  - Risk Level: HIGH - Reduced legal protection\n"
    
    # Check for liability terms
    if any(word in clause_lower for word in ['liable', 'liability', 'responsible']):
        analysis += "• LIABILITY TERMS: This clause addresses responsibility for damages.\n"
    
    if not any(word in clause_lower for word in ['warrant', 'warranty', 'guarantee', 'assure', 'promise', 'disclaim', 'liable']):
        analysis += "• No specific warranty or guarantee terms detected in this clause.\n"
    
    return analysis

def analyze_uploaded_file(filename, file_content):
    """
    Save uploaded file temporarily, extract clauses, analyze them.
    """
    logger.info(f"Starting analysis of file: {filename}")
    
    try:
        # Save file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
            tmp.write(file_content)
            tmp_path = tmp.name
        
        logger.info(f"Temporary file created: {tmp_path}")
        
        # Extract clauses
        clauses = extract_clauses_from_docx(tmp_path)
        
        if not clauses:
            raise Exception("No readable content found in the document")
        
        results = []
        total_clauses = len(clauses)
        
        for i, clause in enumerate(clauses):
            logger.info(f"Processing clause {i+1}/{total_clauses}")
            
            # Skip very short clauses (likely formatting artifacts)
            if len(clause.strip()) < 20:
                continue
            
            # Simple analysis
            analysis = analyze_clause_simple(clause)
            
            # Check if clause might contain warranty/guarantee terms
            warranty_keywords = ['warrant', 'guarantee', 'assure', 'promise', 'liability', 'disclaim', 'as-is']
            has_warranty_terms = any(keyword in clause.lower() for keyword in warranty_keywords)
            
            result = {
                "clause": clause,
                "analysis": analysis,
                "has_warranty_terms": has_warranty_terms
            }
            
            # Add Grantie-specific analysis if warranty terms are detected
            if has_warranty_terms:
                logger.info(f"Warranty terms detected in clause {i+1}, running Grantie analysis")
                result["grantie_analysis"] = analyze_clause_for_grantie_simple(clause)
            
            results.append(result)
        
        # Clean up temporary file
        try:
            os.unlink(tmp_path)
            logger.info("Temporary file cleaned up")
        except:
            pass  # File cleanup not critical
        
        logger.info(f"Analysis complete. Processed {len(results)} clauses")
        return results
        
    except Exception as e:
        logger.error(f"Error in analyze_uploaded_file: {str(e)}")
        # Clean up temporary file if it exists
        try:
            if 'tmp_path' in locals():
                os.unlink(tmp_path)
        except:
            pass
        
        # Return error information
        return [{
            "clause": "Error processing document",
            "analysis": f"Failed to analyze document: {str(e)}",
            "has_warranty_terms": False
        }]

def get_document_statistics(clauses_result):
    """
    Get statistics about the analyzed document.
    """
    total_clauses = len(clauses_result)
    warranty_clauses = sum(1 for clause in clauses_result if clause.get("has_warranty_terms", False))
    
    return {
        "total_clauses": total_clauses,
        "warranty_related_clauses": warranty_clauses,
        "warranty_percentage": round((warranty_clauses / total_clauses) * 100, 2) if total_clauses > 0 else 0
    }