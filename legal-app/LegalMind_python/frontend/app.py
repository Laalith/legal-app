# frontend/app.py

import streamlit as st
import requests
import io
import json

# API URLs
BACKEND_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Legal Clause Analyzer with Grantie", layout="wide")

# Custom CSS for better styling
st.markdown("""
<style>
    .warranty-box {
        background-color: #f0f8ff;
        padding: 10px;
        border-radius: 5px;
        border-left: 4px solid #1f77b4;
        margin: 10px 0;
    }
    .risk-high {
        background-color: #ffe6e6;
        border-left-color: #ff4444;
    }
    .risk-medium {
        background-color: #fff8e1;
        border-left-color: #ff9800;
    }
    .risk-low {
        background-color: #e8f5e8;
        border-left-color: #4caf50;
    }
    .compliance-issue {
        background-color: #fff3cd;
        padding: 8px;
        border-radius: 4px;
        border-left: 3px solid #ffc107;
        margin: 5px 0;
    }
</style>
""", unsafe_allow_html=True)

# Define all functions first
def play_audio(text):
    """Play text-to-speech audio."""
    with st.spinner("🔊 Generating audio..."):
        tts_response = requests.post(
            f"{BACKEND_URL}/speak/",
            json={"text": text[:500]}  # Limit text length for TTS
        )
        if tts_response.status_code == 200:
            audio_bytes = tts_response.content
            st.audio(io.BytesIO(audio_bytes), format="audio/mp3")
        else:
            st.error("❌ Text-to-speech failed.")

def generate_summary(clauses):
    """Generate document summary."""
    with st.spinner("🧠 Generating summary..."):
        all_text = "\n".join([c['clause'] for c in clauses])
        response = requests.post(f"{BACKEND_URL}/summarize/", json={"text": all_text})
        
        if response.status_code == 200:
            summary = response.json().get("summary", "")
            st.markdown("### 🧾 Document Summary")
            st.markdown(summary)
        else:
            st.error("❌ Failed to generate summary.")

def display_document_statistics(data):
    """Display document statistics."""
    st.markdown("### 📊 Document Statistics")
    
    col1, col2, col3 = st.columns(3)
    
    total_clauses = len(data.get("clauses", []))
    warranty_clauses = sum(1 for clause in data.get("clauses", []) if clause.get("has_warranty_terms", False))
    
    with col1:
        st.metric("Total Clauses", total_clauses)
    with col2:
        st.metric("Warranty Clauses", warranty_clauses)
    with col3:
        warranty_percentage = round((warranty_clauses / total_clauses) * 100, 1) if total_clauses > 0 else 0
        st.metric("Warranty %", f"{warranty_percentage}%")

def display_compliance_overview(compliance_data):
    """Display compliance overview."""
    st.markdown("### ⚠️ Compliance Overview")
    
    issues = compliance_data.get("compliance_issues", [])
    recommendations = compliance_data.get("recommendations", [])
    
    if issues:
        st.markdown("**🚨 Compliance Issues Found:**")
        for issue in issues:
            st.markdown(f'<div class="compliance-issue">⚠️ {issue}</div>', unsafe_allow_html=True)
    
    if recommendations:
        st.markdown("**💡 Recommendations:**")
        for rec in recommendations:
            st.info(f"💡 {rec}")
    
    if not issues and not recommendations:
        st.success("✅ No major compliance issues detected.")

def display_warranty_summary(warranty_data):
    """Display warranty analysis summary."""
    st.markdown("### 🛡️ Warranty Analysis Summary")
    
    if "analysis" in warranty_data:
        st.markdown(warranty_data["analysis"])
    
    summary = warranty_data.get("summary", {})
    if summary:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            status = "✅" if summary.get("has_warranties", False) else "❌"
            st.markdown(f"**Warranties:** {status}")
        
        with col2:
            status = "✅" if summary.get("has_guarantees", False) else "❌"
            st.markdown(f"**Guarantees:** {status}")
        
        with col3:
            risk_level = summary.get("risk_level", "Unknown")
            risk_color = {"High": "red", "Medium": "orange", "Low": "green", "Unknown": "gray"}
            st.markdown(f"**Risk Level:** :{risk_color.get(risk_level, 'gray')}[{risk_level}]")

def display_standard_clause(clause_info, index):
    """Display a standard clause."""
    with st.expander(f"📄 Clause {index+1}"):
        st.markdown("**📝 Original Text:**")
        st.text_area("", clause_info['clause'], height=80, key=f"std_original_{index}", disabled=True)
        
        st.markdown("**🔍 Analysis:**")
        st.markdown(clause_info['analysis'])

def display_warranty_clause(clause_info, index, include_tts, mode):
    """Display a warranty clause with special formatting."""
    risk_class = ""
    if "grantie_analysis" in clause_info:
        analysis_text = clause_info["grantie_analysis"].upper()
        if "HIGH" in analysis_text:
            risk_class = "risk-high"
        elif "MEDIUM" in analysis_text:
            risk_class = "risk-medium"
        elif "LOW" in analysis_text:
            risk_class = "risk-low"
    
    with st.expander(f"⚖️ Warranty Clause {index+1} {'🔴 HIGH RISK' if risk_class == 'risk-high' else ''}"):
        st.markdown(f'<div class="warranty-box {risk_class}">', unsafe_allow_html=True)
        
        st.markdown("**📝 Original Text:**")
        st.text_area("", clause_info['clause'], height=100, key=f"warranty_original_{index}", disabled=True)
        
        st.markdown("**🔍 General Analysis:**")
        st.markdown(clause_info['analysis'])
        
        if "grantie_analysis" in clause_info:
            st.markdown("**⚖️ Warranty/Guarantee Analysis:**")
            st.markdown(clause_info['grantie_analysis'])
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # TTS functionality
        if include_tts:
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"🔊 Listen to General Analysis", key=f"tts_gen_{index}"):
                    play_audio(clause_info["analysis"])
            with col2:
                if "grantie_analysis" in clause_info and st.button(f"🔊 Listen to Warranty Analysis", key=f"tts_war_{index}"):
                    play_audio(clause_info["grantie_analysis"])

def display_standard_analysis(data, include_tts):
    """Display standard clause analysis."""
    st.success("✅ Standard Analysis Complete!")
    
    # Summary button
    if st.button("🧠 Generate Document Summary"):
        generate_summary(data["clauses"])
    
    st.markdown("---")
    
    # Display clauses
    for i, clause_info in enumerate(data["clauses"]):
        with st.expander(f"📄 Clause {i+1}", expanded=i < 3):  # Expand first 3 clauses
            st.markdown(f"**📝 Original Text:**")
            st.text_area("", clause_info['clause'], height=100, key=f"original_{i}", disabled=True)
            
            st.markdown(f"**🔍 Analysis:**")
            st.markdown(clause_info['analysis'])
            
            # TTS functionality
            if include_tts and st.button(f"🔊 Listen to Analysis", key=f"tts_standard_{i}"):
                play_audio(clause_info["analysis"])

def display_grantie_analysis(data, include_tts, show_statistics):
    """Display Grantie-specific warranty analysis."""
    st.success("✅ Grantie (Warranty) Analysis Complete!")
    
    # Statistics
    if show_statistics:
        display_document_statistics(data)
    
    # Compliance Overview
    if "compliance" in data:
        display_compliance_overview(data["compliance"])
    
    # Warranty Analysis Summary
    if "warranty_analysis" in data:
        display_warranty_summary(data["warranty_analysis"])
    
    st.markdown("---")
    st.markdown("## 📋 Detailed Clause Analysis")
    
    # Display clauses with Grantie analysis
    warranty_clauses = [clause for clause in data["clauses"] if clause.get("has_warranty_terms", False)]
    other_clauses = [clause for clause in data["clauses"] if not clause.get("has_warranty_terms", False)]
    
    # Show warranty clauses first
    if warranty_clauses:
        st.markdown("### ⚖️ Warranty & Guarantee Clauses")
        for i, clause_info in enumerate(warranty_clauses):
            display_warranty_clause(clause_info, i, include_tts, "warranty")
    
    # Show other clauses
    if other_clauses:
        with st.expander(f"📄 Other Clauses ({len(other_clauses)} clauses)", expanded=False):
            for i, clause_info in enumerate(other_clauses):
                display_standard_clause(clause_info, i + len(warranty_clauses))

def display_full_analysis(data, include_tts, show_statistics):
    """Display complete analysis with all features."""
    st.success("✅ Complete Analysis Finished!")
    
    # Create tabs for organized display
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "⚖️ Warranties", "📋 All Clauses", "🧠 Summary"])
    
    with tab1:
        if show_statistics:
            display_document_statistics(data)
        if "compliance" in data:
            display_compliance_overview(data["compliance"])
    
    with tab2:
        if "warranty_analysis" in data:
            display_warranty_summary(data["warranty_analysis"])
        
        warranty_clauses = [clause for clause in data["clauses"] if clause.get("has_warranty_terms", False)]
        if warranty_clauses:
            st.markdown("### Detailed Warranty Clauses")
            for i, clause_info in enumerate(warranty_clauses):
                display_warranty_clause(clause_info, i, include_tts, "full")
        else:
            st.info("No warranty or guarantee clauses detected in this document.")
    
    with tab3:
        for i, clause_info in enumerate(data["clauses"]):
            if clause_info.get("has_warranty_terms", False):
                display_warranty_clause(clause_info, i, include_tts, "full")
            else:
                display_standard_clause(clause_info, i)
    
    with tab4:
        if st.button("🧠 Generate Document Summary"):
            generate_summary(data["clauses"])

# Main app layout
# Sidebar for navigation
st.sidebar.title("🏛️ Legal Document Analyzer")
analysis_mode = st.sidebar.selectbox(
    "Choose Analysis Mode:",
    ["Standard Analysis", "Grantie (Warranty) Analysis", "Full Analysis"]
)

st.title("📜 Legal Document Analyzer with Grantie")
st.markdown("Upload a legal document to analyze clauses, warranties, and guarantees")

# File uploader
uploaded_file = st.file_uploader("Upload a .docx legal document", type=["docx"])

if uploaded_file:
    # Create columns for better layout
    col1, col2 = st.columns([2, 1])
    
    with col2:
        st.info("📊 Analysis Options")
        include_tts = st.checkbox("🔊 Enable Text-to-Speech", value=False)
        show_statistics = st.checkbox("📈 Show Document Statistics", value=True)
    
    with col1:
        st.info("🔄 Processing document...")

    # Choose analysis based on mode
    if analysis_mode == "Standard Analysis":
        # Standard analysis
        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
        response = requests.post(f"{BACKEND_URL}/analyze/", files=files)
        
        if response.status_code == 200:
            data = response.json()
            display_standard_analysis(data, include_tts)
        else:
            st.error("❌ Error processing the document.")
    
    elif analysis_mode == "Grantie (Warranty) Analysis":
        # Grantie-specific analysis
        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
        response = requests.post(f"{BACKEND_URL}/grantie/full-analysis/", files=files)
        
        if response.status_code == 200:
            data = response.json()
            display_grantie_analysis(data, include_tts, show_statistics)
        else:
            st.error("❌ Error processing the document for Grantie analysis.")
    
    else:  # Full Analysis
        # Both standard and Grantie analysis
        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
        response = requests.post(f"{BACKEND_URL}/grantie/full-analysis/", files=files)
        
        if response.status_code == 200:
            data = response.json()
            display_full_analysis(data, include_tts, show_statistics)
        else:
            st.error("❌ Error processing the document for full analysis.")

# Sidebar information
st.sidebar.markdown("---")
st.sidebar.markdown("### ℹ️ About")
st.sidebar.markdown("""
**Standard Analysis**: Basic clause interpretation

**Grantie Analysis**: Focus on warranties and guarantees

**Full Analysis**: Complete analysis with all features
""")

st.sidebar.markdown("### 🔧 Features")
st.sidebar.markdown("""
- 📄 Clause-by-clause analysis
- ⚖️ Warranty & guarantee detection
- 🚨 Compliance checking
- 📊 Document statistics
- 🔊 Text-to-speech support
- 🧠 Document summarization
""")

