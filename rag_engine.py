import os
import google.generativeai as genai
from typing import Tuple, List, Dict
from utils.pdf_loader import PDFLoader
import streamlit as st

class RAGEngine:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY')
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-pro')
        else:
            self.model = None
        
        self.pdf_loader = PDFLoader()
        self.chunks = []
        self.embeddings = []
    
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
        
        # Generate answer using LLM
        answer = self._generate_answer(question, best_chunk['text'])
        source = self.pdf_loader.get_chunk_source(best_chunk)
        
        return answer, source
    
    def _find_best_chunk(self, question: str) -> Dict[str, any]:
        """Find the most relevant chunk using semantic similarity"""
        if not self.chunks:
            return None
        
        if self.model:
            # Use LLM for semantic similarity
            return self._semantic_search(question)
        else:
            # Fallback to keyword matching
            return self._keyword_search(question)
    
    def _semantic_search(self, question: str) -> Dict[str, any]:
        """Use LLM to find most relevant chunk"""
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
            
            response = self.model.generate_content(prompt)
            chunk_num = int(response.text.strip()) - 1
            
            if 0 <= chunk_num < len(self.chunks):
                return self.chunks[chunk_num]
            
        except Exception as e:
            st.warning(f"Semantic search failed: {e}. Falling back to keyword search.")
        
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
        """Generate answer using LLM with context"""
        if not self.model:
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
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            return f"Error generating answer: {e}. Here's the relevant context: {context[:200]}..."
    
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