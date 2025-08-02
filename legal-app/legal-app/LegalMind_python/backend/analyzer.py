# backend/analyzer.py - Fixed to use GPT-3.5-turbo

import openai
import tempfile
from docx import Document
from dotenv import load_dotenv
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

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

def analyze_clause_with_openai(clause):
    """
    Call OpenAI API to analyze one clause using GPT-3.5-turbo.
    """
    if not openai.api_key:
        raise Exception("OpenAI API key not configured. Please check your .env file.")
    
    prompt = f"Please explain the meaning of this legal clause in simple language:\n\n{clause}"

    try:
        logger.info("Calling OpenAI API for clause analysis...")
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Changed from gpt-4 to gpt-3.5-turbo
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=300
        )
        result = response.choices[0].message.content.strip()
        logger.info("OpenAI API call successful")
        return result
        
    except openai.error.AuthenticationError:
        logger.error("OpenAI Authentication Error - Invalid API key")
        return "Error: Invalid OpenAI API key. Please check your .env file."
        
    except openai.error.RateLimitError:
        logger.error("OpenAI Rate Limit Error")
        return "Error: OpenAI rate limit exceeded. Please try again later or check your account balance."
        
    except openai.error.APIError as e:
        logger.error(f"OpenAI API Error: {str(e)}")
        return f"Error: OpenAI API error - {str(e)}"
        
    except Exception as e:
        logger.error(f"Unexpected error in OpenAI call: {str(e)}")
        return f"Error analyzing clause: {str(e)}"

def analyze_clause_for_grantie(clause):
    """
    Specialized analysis for warranty/guarantee clauses (Grantie feature).
    """
    if not openai.api_key:
        return "Error: OpenAI API key not configured."
    
    prompt = f"""
    Analyze this legal clause specifically for warranties, guarantees, and related terms:
    
    {clause}
    
    Please identify:
    1. Any warranties mentioned (express or implied)
    2. Any guarantees provided
    3. Limitations or disclaimers
    4. Risk level for the recipient (Low/Medium/High)
    5. Key terms to watch out for
    
    Provide a clear, simple explanation suitable for non-lawyers.
    """

    try:
        logger.info("Calling OpenAI API for Grantie analysis...")
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Changed from gpt-4 to gpt-3.5-turbo
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=350
        )
        result = response.choices[0].message.content.strip()
        logger.info("Grantie analysis successful")
        return result
        
    except openai.error.AuthenticationError:
        return "Error: Invalid OpenAI API key for Grantie analysis."
    except openai.error.RateLimitError:
        return "Error: OpenAI rate limit exceeded for Grantie analysis."
    except Exception as e:
        logger.error(f"Error in Grantie analysis: {str(e)}")
        return f"Error analyzing clause for Grantie: {str(e)}"

def analyze_uploaded_file(filename, file_content):
    """
    Save uploaded file temporarily, extract clauses, analyze them with OpenAI.
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
            if len(clause.strip()) < 10:
                continue
            
            # Standard analysis
            analysis = analyze_clause_with_openai(clause)
            
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
                result["grantie_analysis"] = analyze_clause_for_grantie(clause)
            
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