import os
import google.generativeai as genai
from typing import Tuple, List, Dict
from utils.pdf_loader import PDFLoader
import streamlit as st
import openai
import cohere
import groq

class RAGEngine:
    def __init__(self):
        # Load API keys from environment
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.cohere_api_key = os.getenv('COHERE_API_KEY')
        self.groq_api_key = os.getenv('GROQ_API_KEY')
        
        # Initialize models with fallback logic
        self.models = self._initialize_models()
        
        self.pdf_loader = PDFLoader()
        self.chunks = []
        self.embeddings = []
    
    def _initialize_models(self) -> Dict[str, any]:
        """Initialize available models with fallback priority"""
        models = {}
        
        # Try Gemini first
        if self.gemini_api_key:
            try:
                genai.configure(api_key=self.gemini_api_key)
                models['gemini'] = genai.GenerativeModel('gemini-2.0-flash')
                st.success("✅ Using Google Gemini for enhanced search")
            except Exception as e:
                st.warning(f"⚠️ Gemini initialization failed: {e}")
        
        # Try OpenAI as fallback
        if self.openai_api_key and 'gemini' not in models:
            try:
                openai.api_key = self.openai_api_key
                models['openai'] = 'gpt-3.5-turbo'
                st.success("✅ Using OpenAI GPT-3.5 for enhanced search")
            except Exception as e:
                st.warning(f"⚠️ OpenAI initialization failed: {e}")
        
        # Try Groq as fallback
        if self.groq_api_key and 'gemini' not in models and 'openai' not in models:
            try:
                models['groq'] = groq.Groq(api_key=self.groq_api_key)
                st.success("✅ Using Groq for enhanced search")
            except Exception as e:
                st.warning(f"⚠️ Groq initialization failed: {e}")
        
        # Try Cohere as fallback
        if self.cohere_api_key and len(models) == 0:
            try:
                models['cohere'] = cohere.Client(self.cohere_api_key)
                st.success("✅ Using Cohere for enhanced search")
            except Exception as e:
                st.warning(f"⚠️ Cohere initialization failed: {e}")
        
        if not models:
            st.info("ℹ️ No API keys available. Using keyword search only.")
        
        return models
    
    def load_and_query(self, pdf_file, question: str) -> Tuple[str, str]:
        """
        Main function: Load PDF and answer question
        Returns: (answer, source_citation)
        """
        # Load and chunk PDF
        if not self.chunks:
            self.chunks = self.pdf_loader.load_pdf(pdf_file)
        
        # Find most relevant chunk
        best_chunk = self._find_best_chunk(question)
        
        if not best_chunk:
            return "I couldn't find relevant information in the document.", "No source found"
        
        # Generate answer using available LLM
        answer = self._generate_answer(question, best_chunk['text'])
        source = self.pdf_loader.get_chunk_source(best_chunk)
        
        return answer, source
    
    def _find_best_chunk(self, question: str) -> Dict[str, any]:
        """Find the most relevant chunk using semantic similarity"""
        if not self.chunks:
            return None
        
        if self.models:
            # Use LLM for semantic similarity
            return self._semantic_search(question)
        else:
            # Fallback to keyword matching
            return self._keyword_search(question)
    
    def _semantic_search(self, question: str) -> Dict[str, any]:
        """Use available LLM to find most relevant chunk"""
        try:
            # Create a prompt to find the most relevant chunk
            chunks_text = "\n\n".join([
                f"Chunk {i+1} (Page {chunk['page']}): {chunk['text'][:200]}..."
                for i, chunk in enumerate(self.chunks[:10])  # Limit to first 10 chunks for speed
            ])
            
            prompt = f"""
            Given this question: "{question}"
            
            And these document chunks:
            {chunks_text}
            
            Which chunk (1-{min(10, len(self.chunks))}) is most relevant to answering the question?
            Respond with only the chunk number.
            """
            
            # Try each model in order
            for model_name, model in self.models.items():
                try:
                    if model_name == 'gemini':
                        response = model.generate_content(prompt)
                        chunk_num = int(response.text.strip()) - 1
                    elif model_name == 'openai':
                        response = openai.ChatCompletion.create(
                            model=model,
                            messages=[{"role": "user", "content": prompt}]
                        )
                        chunk_num = int(response.choices[0].message.content.strip()) - 1
                    elif model_name == 'groq':
                        response = model.chat.completions.create(
                            model="llama3-8b-8192",
                            messages=[{"role": "user", "content": prompt}]
                        )
                        chunk_num = int(response.choices[0].message.content.strip()) - 1
                    elif model_name == 'cohere':
                        response = model.generate(
                            model='command',
                            prompt=prompt,
                            max_tokens=10
                        )
                        chunk_num = int(response.generations[0].text.strip()) - 1
                    
                    if 0 <= chunk_num < len(self.chunks):
                        return self.chunks[chunk_num]
                        
                except Exception as e:
                    st.warning(f"⚠️ {model_name} search failed: {e}")
                    continue
            
        except Exception as e:
            st.warning(f"⚠️ Semantic search failed: {e}")
        
        return self._keyword_search(question)
    
    def _keyword_search(self, question: str) -> Dict[str, any]:
        """Simple keyword-based search as fallback"""
        question_lower = question.lower()
        keywords = question_lower.split()
        
        best_score = 0
        best_chunk = None
        
        for chunk in self.chunks:
            chunk_text_lower = chunk['text'].lower()
            score = sum(1 for keyword in keywords if keyword in chunk_text_lower)
            
            if score > best_score:
                best_score = score
                best_chunk = chunk
        
        return best_chunk
    
    def _generate_answer(self, question: str, context: str) -> str:
        """Generate answer using available LLM with context"""
        if not self.models:
            # Fallback: return context with some formatting
            return f"Based on the document: {context[:300]}..."
        
        try:
            prompt = f"""
            Context from security policy document:
            {context}
            
            Question: {question}
            
            Please provide a clear, concise answer based on the context above. 
            If the context doesn't contain enough information to answer the question, 
            say "The document doesn't contain enough information to answer this question."
            """
            
            # Try each model in order
            for model_name, model in self.models.items():
                try:
                    if model_name == 'gemini':
                        response = model.generate_content(prompt)
                        return response.text.strip()
                    elif model_name == 'openai':
                        response = openai.ChatCompletion.create(
                            model=model,
                            messages=[{"role": "user", "content": prompt}]
                        )
                        return response.choices[0].message.content.strip()
                    elif model_name == 'groq':
                        response = model.chat.completions.create(
                            model="llama3-8b-8192",
                            messages=[{"role": "user", "content": prompt}]
                        )
                        return response.choices[0].message.content.strip()
                    elif model_name == 'cohere':
                        response = model.generate(
                            model='command',
                            prompt=prompt,
                            max_tokens=200
                        )
                        return response.generations[0].text.strip()
                        
                except Exception as e:
                    st.warning(f"⚠️ {model_name} answer generation failed: {e}")
                    continue
            
        except Exception as e:
            return f"Error generating answer: {e}. Here's the relevant context: {context[:200]}..."
        
        # If all models fail, return context
        return f"Based on the document: {context[:300]}..."
    
    def get_coverage_confidence(self, question: str) -> float:
        """Estimate confidence in answer coverage (0-100%)"""
        if not self.chunks:
            return 0.0
        
        # Simple heuristic: longer chunks and more keyword matches = higher confidence
        best_chunk = self._find_best_chunk(question)
        if not best_chunk:
            return 0.0
        
        # Calculate confidence based on chunk length and keyword density
        chunk_text = best_chunk['text'].lower()
        question_keywords = question.lower().split()
        
        keyword_matches = sum(1 for keyword in question_keywords if keyword in chunk_text)
        keyword_density = keyword_matches / len(question_keywords) if question_keywords else 0
        
        # Base confidence on keyword density and chunk length
        confidence = min(100, (keyword_density * 60) + (len(chunk_text) / 1000 * 40))
        
        return round(confidence, 1)

# Global RAG engine instance
_rag_engine = None

def load_and_query(pdf_file, question: str) -> Tuple[str, str]:
    """Convenience function for the main app"""
    global _rag_engine
    if _rag_engine is None:
        _rag_engine = RAGEngine()
    
    return _rag_engine.load_and_query(pdf_file, question)

def get_coverage_confidence(question: str) -> float:
    """Get confidence score for a question"""
    global _rag_engine
    if _rag_engine is None:
        return 0.0
    
    return _rag_engine.get_coverage_confidence(question) 