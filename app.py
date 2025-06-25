import streamlit as st
from rag_engine import load_and_query, get_coverage_confidence
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Security Intake Assistant",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .subtitle {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 3rem;
    }
    .answer-box {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
    .source-box {
        background-color: #e8f4fd;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #b3d9ff;
        margin-top: 1rem;
    }
    .confidence-box {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #ffeaa7;
        margin-top: 1rem;
        font-size: 0.9rem;
    }
    .confidence-score {
        background-color: #28a745;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        display: inline-block;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .upload-section {
        background-color: #f8f9fa;
        padding: 2rem;
        border-radius: 10px;
        border: 2px dashed #dee2e6;
        text-align: center;
        margin-bottom: 2rem;
    }
    .value-prop {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 3px solid #28a745;
        margin-bottom: 1rem;
        font-size: 0.85rem;
    }
    .value-prop h4 {
        color: #28a745;
        margin-bottom: 0.5rem;
        font-size: 1rem;
    }
    .value-prop ul {
        margin: 0.5rem 0;
        padding-left: 1.2rem;
    }
    .value-prop li {
        margin: 0.2rem 0;
    }
    .sample-data {
        background-color: #e8f4fd;
        padding: 0.8rem;
        border-radius: 8px;
        border: 1px solid #b3d9ff;
        margin-bottom: 1rem;
        font-size: 0.9rem;
    }
    .search-explanation {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 3px solid #17a2b8;
        margin-bottom: 1rem;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

def load_sample_pdf():
    """Load the sample PDF file"""
    if os.path.exists("sample_security_policy.pdf"):
        with open("sample_security_policy.pdf", "rb") as f:
            return f.read()
    return None

def main():
    # Header
    st.markdown('<h1 class="main-header">🔐 Security Intake Assistant</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Upload your security policy and ask questions to get instant answers with source citations</p>', unsafe_allow_html=True)
    
    # Value proposition for hiring managers (subtle)
    with st.expander("💡 What makes this unique?", expanded=False):
        st.markdown("""
        <div class="value-prop">
        <h4>🔐 Purpose-built for security workflows</h4>
        <ul>
        <li><strong>Compliance-focused:</strong> Prioritizes SOC 2, ISO27001 terminology and coverage confidence</li>
        <li><strong>Signal-oriented:</strong> Surfaces only what's needed for trust evaluation — no hallucinations</li>
        <li><strong>Minimal & embeddable:</strong> Easy to imagine inside Conveyor's UI or as a Chrome extension</li>
        </ul>
        
        <p><em>Designed for teams who want to <strong>answer faster, trust sooner</strong>, and automate the repetitive parts of security review.</em></p>
        </div>
        """, unsafe_allow_html=True)
    
    # Search logic explanation
    with st.expander("🔍 How does the search work?", expanded=False):
        st.markdown("""
        <div class="search-explanation">
        <h4>🧠 AI-Powered Semantic Search</h4>
        <p><strong>Step 1:</strong> Document is split into 500-word chunks with page tracking</p>
        <p><strong>Step 2:</strong> AI analyzes your question and finds the most relevant chunk using:</p>
        <ul>
        <li><strong>Semantic understanding:</strong> "encrypt data at rest" matches "AES-256 secures stored information"</li>
        <li><strong>Compliance terminology:</strong> Understands security and compliance language</li>
        <li><strong>Context relevance:</strong> Prioritizes chunks with detailed, relevant information</li>
        </ul>
        <p><strong>Step 3:</strong> AI generates precise answer from the selected chunk</p>
        <p><strong>Step 4:</strong> Confidence score evaluates answer quality and completeness</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Sidebar for example questions
    with st.sidebar:
        st.header("💡 Example Questions")
        
        # Sample data download section
        st.markdown("""
        <div class="sample-data">
        <strong>📄 Sample Data:</strong> 
        <a href="https://github.com/nuggetswise/conveyer/blob/main/sample_security_policy.pdf" target="_blank">Download sample security policy</a>
        <br><small>Contains SOC 2, ISO27001, and security compliance sections for testing</small>
        </div>
        """, unsafe_allow_html=True)
        
        example_questions = [
            "Do you encrypt data at rest?",
            "What is your incident response process?",
            "How do you handle access controls?",
            "What are your backup procedures?",
            "Do you have a disaster recovery plan?"
        ]
        
        for question in example_questions:
            if st.button(question, key=f"example_{question}"):
                st.session_state.example_question = question
                st.session_state.use_sample_pdf = True
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📄 Upload Security Policy")
        
        # File upload section
        with st.container():
            st.markdown('<div class="upload-section">', unsafe_allow_html=True)
            uploaded_file = st.file_uploader(
                "Choose a PDF file",
                type="pdf",
                help="Upload your security policy, SOC2 report, ISO27001 document, etc."
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Handle sample PDF loading
        if hasattr(st.session_state, 'use_sample_pdf') and st.session_state.use_sample_pdf:
            sample_pdf_data = load_sample_pdf()
            if sample_pdf_data:
                # Create a file-like object for the sample PDF
                import io
                sample_file = io.BytesIO(sample_pdf_data)
                sample_file.name = "sample_security_policy.pdf"
                uploaded_file = sample_file
                st.success("✅ Loaded sample security policy for testing")
                del st.session_state.use_sample_pdf
        
        if uploaded_file:
            st.success(f"✅ Uploaded: {uploaded_file.name}")
            
            # File info
            file_size = len(uploaded_file.getvalue()) / 1024  # KB
            st.info(f"📊 File size: {file_size:.1f} KB")
    
    with col2:
        st.header("❓ Ask Questions")
        
        # Question input
        question = st.text_input(
            "Enter your question:",
            placeholder="e.g., Do you encrypt data at rest?",
            key="question_input"
        )
        
        # Handle example question clicks
        if hasattr(st.session_state, 'example_question'):
            question = st.session_state.example_question
            del st.session_state.example_question
        
        if question and uploaded_file:
            # Process question
            with st.spinner("🔍 Searching your policy..."):
                try:
                    answer, source = load_and_query(uploaded_file, question)
                    confidence, reasoning = get_coverage_confidence(question)
                    
                    # Display results
                    st.markdown('<div class="answer-box">', unsafe_allow_html=True)
                    st.markdown("**Answer:**")
                    st.write(answer)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Source citation
                    st.markdown('<div class="source-box">', unsafe_allow_html=True)
                    st.markdown("**📖 Source:**")
                    st.write(source)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Confidence score with detailed reasoning
                    if confidence > 0:
                        st.markdown('<div class="confidence-box">', unsafe_allow_html=True)
                        st.markdown(f'<div class="confidence-score">🎯 Confidence: {confidence}%</div>', unsafe_allow_html=True)
                        st.markdown("**Evaluation:**")
                        st.write(reasoning)
                        st.markdown("""
                        <small>
                        <strong>What this means:</strong><br>
                        • <strong>90%+:</strong> Excellent match with detailed, relevant information<br>
                        • <strong>70-89%:</strong> Good match with sufficient context<br>
                        • <strong>50-69%:</strong> Moderate match - answer may be limited<br>
                        • <strong>Below 50%:</strong> Weak match - consider rephrasing question
                        </small>
                        """, unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                except Exception as e:
                    st.error(f"❌ Error processing question: {str(e)}")
                    st.info("💡 Try re-uploading the PDF or check if the file is corrupted.")
        
        elif question and not uploaded_file:
            st.warning("⚠️ Please upload a PDF file first!")
    
    # Footer
    st.divider()
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.9rem;">
        <p>🔐 Security Intake Assistant MVP | Built for Conveyor-style product development</p>
        <p>Upload security policies and get instant answers with source citations</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 