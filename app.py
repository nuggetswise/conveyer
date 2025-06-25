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
        padding: 0.5rem 1rem;
        border-radius: 20px;
        display: inline-block;
        font-size: 0.9rem;
        color: #856404;
    }
    .upload-section {
        background-color: #f8f9fa;
        padding: 2rem;
        border-radius: 10px;
        border: 2px dashed #dee2e6;
        text-align: center;
        margin-bottom: 2rem;
    }
    .model-status {
        background-color: #d4edda;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        border: 1px solid #c3e6cb;
        margin-bottom: 1rem;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Header
    st.markdown('<h1 class="main-header">🔐 Security Intake Assistant</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Upload your security policy and ask questions to get instant answers with source citations</p>', unsafe_allow_html=True)
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Show API key status
        api_keys = {
            'GEMINI_API_KEY': os.getenv('GEMINI_API_KEY'),
            'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
            'GROQ_API_KEY': os.getenv('GROQ_API_KEY'),
            'COHERE_API_KEY': os.getenv('COHERE_API_KEY')
        }
        
        available_keys = [key for key, value in api_keys.items() if value]
        
        if available_keys:
            st.markdown('<div class="model-status">', unsafe_allow_html=True)
            st.markdown("**🤖 Available AI Models:**")
            for key in available_keys:
                st.markdown(f"• {key.replace('_API_KEY', '')}")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("ℹ️ No API keys found in .env file. Using keyword search only.")
            st.markdown("""
            **To enable AI-powered search, add API keys to your .env file:**
            ```
            GEMINI_API_KEY=your_key_here
            OPENAI_API_KEY=your_key_here
            GROQ_API_KEY=your_key_here
            COHERE_API_KEY=your_key_here
            ```
            """)
        
        st.divider()
        
        # Example questions
        st.header("💡 Example Questions")
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
                    confidence = get_coverage_confidence(question)
                    
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
                    
                    # Confidence score
                    if confidence > 0:
                        st.markdown(f'<div class="confidence-box">🎯 Confidence: {confidence}%</div>', unsafe_allow_html=True)
                    
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