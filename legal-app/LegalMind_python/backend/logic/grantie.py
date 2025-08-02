# backend/logic/grantie.py - Fixed to use GPT-3.5-turbo

import openai
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def analyze_warranties_and_guarantees(text: str) -> dict:
    """
    Analyze document text for warranties and guarantees using OpenAI.
    """
    prompt = f"""
    Analyze the following legal document text for warranties, guarantees, and related terms:

    {text}

    Please provide:
    1. Summary of all warranties found
    2. Summary of all guarantees found
    3. Any disclaimers or limitations
    4. Overall risk assessment (High/Medium/Low)
    5. Key recommendations for the document recipient

    Format your response as a detailed analysis.
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Changed from gpt-4 to gpt-3.5-turbo
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=500
        )
        
        analysis_text = response.choices[0].message.content.strip()
        
        # Extract key information for structured response
        has_warranties = any(keyword in text.lower() for keyword in ['warrant', 'warranty', 'guaranteed'])
        has_guarantees = any(keyword in text.lower() for keyword in ['guarantee', 'assure', 'promise'])
        
        # Simple risk assessment based on keywords
        high_risk_keywords = ['disclaim', 'as-is', 'no warranty', 'liability', 'limitation']
        medium_risk_keywords = ['limited warranty', 'conditional', 'subject to']
        
        risk_level = "Low"
        if any(keyword in text.lower() for keyword in high_risk_keywords):
            risk_level = "High"
        elif any(keyword in text.lower() for keyword in medium_risk_keywords):
            risk_level = "Medium"
        
        return {
            "analysis": analysis_text,
            "summary": {
                "has_warranties": has_warranties,
                "has_guarantees": has_guarantees,
                "risk_level": risk_level
            }
        }
        
    except Exception as e:
        return {
            "analysis": f"Error analyzing warranties and guarantees: {str(e)}",
            "summary": {
                "has_warranties": False,
                "has_guarantees": False,
                "risk_level": "Unknown"
            }
        }

def check_warranty_compliance(clauses: list) -> dict:
    """
    Check warranty compliance for analyzed clauses.
    """
    compliance_issues = []
    recommendations = []
    
    warranty_clauses = [clause for clause in clauses if clause.get("has_warranty_terms", False)]
    
    if not warranty_clauses:
        return {
            "compliance_issues": [],
            "recommendations": ["Consider adding clear warranty terms for transparency"],
            "total_issues": 0
        }
    
    # Check for common compliance issues
    for clause in warranty_clauses:
        clause_text = clause.get("clause", "").lower()
        
        # Check for vague warranty terms
        if any(vague_term in clause_text for vague_term in ['reasonable', 'satisfactory', 'appropriate']):
            compliance_issues.append("Vague warranty terms found - consider more specific language")
        
        # Check for disclaimer without proper notice
        if 'disclaim' in clause_text and 'notice' not in clause_text:
            compliance_issues.append("Warranty disclaimer may lack proper notice requirements")
        
        # Check for time limitations
        if 'warranty' in clause_text and not any(time_word in clause_text for time_word in ['days', 'months', 'years', 'period']):
            recommendations.append("Consider adding specific time limits for warranty coverage")
    
    # Add general recommendations
    if len(warranty_clauses) > 3:
        recommendations.append("Multiple warranty clauses found - ensure consistency across all terms")
    
    return {
        "compliance_issues": compliance_issues,
        "recommendations": recommendations,
        "total_issues": len(compliance_issues)
    }