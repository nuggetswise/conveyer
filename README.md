# 🔐 Security Intake Assistant

A prototype RAG (Retrieval-Augmented Generation) application that helps security teams quickly answer questions from security policy documents with source citations.

## 🎯 Problem & Solution

**Problem**: Filling out vendor security questionnaires is repetitive and time-consuming. Security teams spend hours manually searching through policy documents to find specific answers.

**Solution**: An AI-powered assistant that:
- Ingests security policy PDFs (SOC2, ISO27001, etc.)
- Allows natural language questions
- Returns answers with source citations
- Provides confidence scores

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)
```bash
# Clone or download the project
cd security-intake-assistant

# Run the setup script
./setup.sh
```

### Option 2: Manual Setup
```bash
# 1. Install Dependencies
pip install -r requirements.txt

# 2. Set up environment variables
cp env_template.txt .env
# Edit .env to add your Google API key if needed

# 3. Create sample PDF (optional)
python create_sample_pdf.py
```

### 3. Run the Application
```bash
streamlit run app.py
```

The app will open at `http://localhost:8502`

## 🔧 Environment Configuration

### Google Gemini API (Optional)
For enhanced semantic search, get a free API key from [Google AI Studio](https://makersuite.google.com/app/apikey):

1. Copy `env_template.txt` to `.env`
2. Add your API key: `GOOGLE_API_KEY=your_api_key_here`
3. The app will work without the API key (using keyword search)

## 📁 Project Structure

```
security-intake-assistant/
├── app.py                     # Streamlit frontend
├── rag_engine.py             # RAG engine with LLM integration
├── utils/
│   └── pdf_loader.py         # PDF processing and chunking
├── requirements.txt          # Python dependencies
├── setup.sh                  # Automated setup script
├── env_template.txt          # Environment variables template
├── .gitignore               # Git ignore rules
├── create_sample_pdf.py     # Sample PDF generator
├── test_rag.py              # RAG functionality test
└── README.md                # This file
```

## 🛠️ Features

### Core Features
- **PDF Upload**: Drag & drop security policy documents
- **Natural Language Q&A**: Ask questions in plain English
- **Source Citations**: See exactly which page/section contains the answer
- **Confidence Scoring**: Get an estimate of answer reliability

### Technical Features
- **Smart Chunking**: Intelligent text segmentation (500 tokens with 50 token overlap)
- **Semantic Search**: Uses Google Gemini for understanding question intent
- **Fallback Search**: Keyword matching when LLM is unavailable
- **Modern UI**: Clean, professional interface with Streamlit

## 🔧 How It Works

1. **Document Processing**: PDF is loaded and split into semantic chunks
2. **Question Analysis**: User question is processed for intent
3. **Retrieval**: Most relevant document chunk is found using semantic similarity
4. **Answer Generation**: LLM generates answer based on retrieved context
5. **Citation**: Source page/section is provided for verification

## 📊 Example Usage

### Sample Questions
- "Do you encrypt data at rest?"
- "What is your incident response process?"
- "How do you handle access controls?"
- "What are your backup procedures?"
- "Do you have a disaster recovery plan?"

### Sample Output
```
Answer: Yes, we encrypt all data at rest using AES-256 encryption. 
Data is encrypted before being stored in our databases and cloud storage.

Source: Page 15

Confidence: 87%
```

## 🎨 UI Features

- **Responsive Design**: Works on desktop and mobile
- **Example Questions**: Quick-start buttons for common queries
- **Real-time Processing**: Live search with progress indicators
- **Error Handling**: Graceful fallbacks and helpful error messages
- **API Key Management**: Secure sidebar configuration

## 🔒 Security & Privacy

- **Local Processing**: PDFs are processed in memory, not stored
- **No Data Persistence**: Documents are not saved to disk
- **Optional API**: Can work without external API calls
- **Secure Input**: API keys are handled securely

## 🚧 Limitations (MVP)

- Single document processing (no multi-doc comparison)
- In-memory storage (no persistence across sessions)
- Basic confidence scoring (heuristic-based)
- Limited to PDF format

## 🔮 Future Enhancements

- Multi-document support
- Persistent document storage
- Advanced confidence scoring
- Export functionality
- Integration with security frameworks
- Batch question processing

## 🛠️ Development

### Testing
```bash
# Test the RAG functionality
python test_rag.py

# Test individual components
python -c "from utils.pdf_loader import PDFLoader; print('✅ PDF loader ready')"
python -c "from rag_engine import RAGEngine; print('✅ RAG engine ready')"
```

### Adding New Features
1. **Backend**: Extend `RAGEngine` class in `rag_engine.py`
2. **Frontend**: Modify Streamlit components in `app.py`
3. **Processing**: Update PDF handling in `utils/pdf_loader.py`

## 🐛 Troubleshooting

### Common Issues
1. **Import Errors**: Make sure you're in the virtual environment (`source .venv/bin/activate`)
2. **PDF Processing Errors**: Check if PyMuPDF is installed correctly
3. **API Key Issues**: Verify your Google API key in the `.env` file
4. **Port Conflicts**: Change the port in `.env` if 8502 is in use

### Dependencies
If you encounter dependency conflicts, try:
```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

## 📝 License

This is a prototype built for demonstration purposes.

## 🤝 Contributing

This is a demo project, but feedback and suggestions are welcome!

---

**Built with ❤️ for Conveyor-style product development** 