import os
import google.generativeai as genai
from typing import Tuple, List, Dict
from utils.pdf_loader import PDFLoader
import streamlit as st
import openai
import cohere
import groq
import re
from datetime import datetime

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
        
        # Track answer history for confidence improvement
        self.answer_history = []
    
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
        
        # Store answer in history for confidence improvement
        self._store_answer_history(question, answer, source, best_chunk)
        
        return answer, source
    
    def _store_answer_history(self, question: str, answer: str, source: str, chunk: Dict):
        """Store answer in history for confidence improvement"""
        self.answer_history.append({
            'timestamp': datetime.now(),
            'question': question,
            'answer': answer,
            'source': source,
            'chunk_text': chunk['text'][:200],  # Store first 200 chars for analysis
            'chunk_page': chunk['page']
        })
        
        # Keep only last 50 answers to prevent memory bloat
        if len(self.answer_history) > 50:
            self.answer_history = self.answer_history[-50:]
    
    def _find_best_chunk(self, question: str) -> Dict[str, any]:
        """Find the most relevant chunk using semantic similarity"""
        if not self.chunks:
            return None
        
        if self.models:
            # Use LLM for semantic similarity
            return self._semantic_search(question)
        else:
            # Fallback to keyword search
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
            
            IMPORTANT: Respond with ONLY the chunk number (1, 2, 3, etc.) and nothing else.
            Do not provide explanations, reasoning, or additional text.
            """
            
            # Try each model in order
            for model_name, model in self.models.items():
                try:
                    response_text = ""
                    
                    if model_name == 'gemini':
                        response = model.generate_content(prompt)
                        response_text = response.text.strip()
                    elif model_name == 'openai':
                        response = openai.ChatCompletion.create(
                            model=model,
                            messages=[{"role": "user", "content": prompt}]
                        )
                        response_text = response.choices[0].message.content.strip()
                    elif model_name == 'groq':
                        response = model.chat.completions.create(
                            model="llama3-8b-8192",
                            messages=[{"role": "user", "content": prompt}]
                        )
                        response_text = response.choices[0].message.content.strip()
                    elif model_name == 'cohere':
                        response = model.generate(
                            model='command',
                            prompt=prompt,
                            max_tokens=10
                        )
                        response_text = response.generations[0].text.strip()
                    
                    # Extract number from response (handle cases where model adds extra text)
                    import re
                    number_match = re.search(r'\b(\d+)\b', response_text)
                    if number_match:
                        chunk_num = int(number_match.group(1)) - 1
                    else:
                        # Fallback: try to parse the first number found
                        numbers = re.findall(r'\d+', response_text)
                        if numbers:
                            chunk_num = int(numbers[0]) - 1
                        else:
                            # If we can't parse a number, log the issue and continue to next model
                            st.warning(f"⚠️ {model_name} returned unparseable response: '{response_text[:100]}...'")
                            continue
                    
                    # Validate chunk number
                    if 0 <= chunk_num < len(self.chunks):
                        return self.chunks[chunk_num]
                    else:
                        st.warning(f"⚠️ {model_name} returned invalid chunk number: {chunk_num + 1}")
                        continue
                        
                except Exception as e:
                    st.warning(f"⚠️ {model_name} search failed: {e}")
                    continue
            
        except Exception as e:
            st.warning(f"⚠️ Semantic search failed: {e}")
        
        # If all LLM models fail, fall back to keyword search
        st.info("ℹ️ Falling back to keyword search due to LLM issues")
        return self._keyword_search(question)
    
    def _keyword_search(self, question: str) -> Dict[str, any]:
        """Enhanced keyword-based search as fallback"""
        question_lower = question.lower()
        
        # Extract meaningful keywords (remove common words)
        common_words = {'do', 'you', 'what', 'how', 'when', 'where', 'why', 'is', 'are', 'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'your', 'have', 'does', 'can', 'will', 'should', 'would', 'could', 'does', 'has', 'had', 'been', 'being', 'this', 'that', 'these', 'those', 'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves'}
        
        # Extract security-specific keywords
        security_keywords = ['encrypt', 'security', 'access', 'control', 'backup', 'disaster', 'recovery', 'incident', 'response', 'policy', 'procedure', 'compliance', 'audit', 'monitor', 'log', 'authentication', 'authorization', 'confidentiality', 'integrity', 'availability', 'data', 'protection', 'privacy', 'gdpr', 'hipaa', 'soc', 'iso', 'vulnerability', 'patch', 'update', 'firewall', 'network', 'system', 'user', 'password', 'mfa', '2fa', 'multi-factor']
        
        # Get question keywords
        question_words = [word for word in question_lower.split() if word not in common_words and len(word) > 2]
        
        # Add security keywords that match the question
        for sec_keyword in security_keywords:
            if sec_keyword in question_lower and sec_keyword not in question_words:
                question_words.append(sec_keyword)
        
        if not question_words:
            question_words = question_lower.split()
        
        best_score = 0
        best_chunk = None
        
        for chunk in self.chunks:
            chunk_text_lower = chunk['text'].lower()
            
            # Calculate keyword matches
            keyword_matches = sum(1 for keyword in question_words if keyword in chunk_text_lower)
            
            # Bonus for security terminology matches
            security_matches = sum(1 for sec_keyword in security_keywords if sec_keyword in chunk_text_lower)
            security_bonus = security_matches * 0.5
            
            # Bonus for longer, more detailed chunks
            length_bonus = min(0.5, len(chunk_text_lower) / 1000)
            
            total_score = keyword_matches + security_bonus + length_bonus
            
            if total_score > best_score:
                best_score = total_score
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
    
    def get_coverage_confidence(self, question: str) -> Tuple[float, str]:
        """Enhanced confidence scoring with multiple factors"""
        if not self.chunks:
            return 0.0, "No document chunks available"
        
        # Find best chunk
        best_chunk = self._find_best_chunk(question)
        if not best_chunk:
            return 0.0, "No relevant information found in document"
        
        # Enhanced confidence calculation
        confidence_factors = self._calculate_confidence_factors(question, best_chunk)
        final_confidence = self._combine_confidence_factors(confidence_factors)
        
        return final_confidence, self._generate_confidence_reasoning(confidence_factors)
    
    def _calculate_confidence_factors(self, question: str, chunk: Dict) -> Dict[str, float]:
        """Calculate multiple confidence factors"""
        chunk_text = chunk['text'].lower()
        question_lower = question.lower()
        
        # Factor 1: Keyword relevance
        common_words = {'do', 'you', 'what', 'how', 'when', 'where', 'why', 'is', 'are', 'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'your', 'have', 'does', 'can', 'will', 'should', 'would', 'could'}
        question_keywords = [word for word in question_lower.split() if word not in common_words and len(word) > 2]
        
        if not question_keywords:
            question_keywords = question_lower.split()
        
        keyword_matches = [kw for kw in question_keywords if kw in chunk_text]
        keyword_relevance = len(keyword_matches) / len(question_keywords) if question_keywords else 0
        
        # Factor 2: Context richness
        chunk_length = len(chunk_text)
        context_richness = min(1.0, chunk_length / 800)  # Normalize to 0-1
        
        # Factor 3: Security terminology match
        security_terms = ['encrypt', 'security', 'access', 'control', 'backup', 'disaster', 'recovery', 'incident', 'response', 'policy', 'procedure', 'compliance', 'audit', 'monitor', 'log', 'authentication', 'authorization', 'confidentiality', 'integrity', 'availability']
        security_matches = sum(1 for term in security_terms if term in chunk_text)
        security_relevance = min(1.0, security_matches / 5)  # Normalize to 0-1
        
        # Factor 4: Answer completeness (based on question type)
        completeness_score = self._assess_answer_completeness(question_lower, chunk_text)
        
        # Factor 5: Historical consistency
        consistency_score = self._assess_historical_consistency(question, chunk)
        
        return {
            'keyword_relevance': keyword_relevance,
            'context_richness': context_richness,
            'security_relevance': security_relevance,
            'completeness': completeness_score,
            'consistency': consistency_score
        }
    
    def _assess_answer_completeness(self, question: str, chunk_text: str) -> float:
        """Assess how complete the answer is based on question type"""
        # Question type detection
        if any(word in question for word in ['how', 'what', 'describe', 'explain']):
            # Detailed questions need more context
            return min(1.0, len(chunk_text) / 500)
        elif any(word in question for word in ['do', 'does', 'have', 'is', 'are']):
            # Yes/no questions can be shorter
            return min(1.0, len(chunk_text) / 200)
        else:
            return min(1.0, len(chunk_text) / 300)
    
    def _assess_historical_consistency(self, question: str, chunk: Dict) -> float:
        """Assess consistency with previous answers"""
        if not self.answer_history:
            return 0.5  # Neutral score for first answer
        
        # Find similar questions in history
        similar_questions = []
        for hist in self.answer_history:
            # Simple similarity check
            common_words = set(question.lower().split()) & set(hist['question'].lower().split())
            if len(common_words) >= 2:  # At least 2 common words
                similar_questions.append(hist)
        
        if not similar_questions:
            return 0.5  # No similar questions found
        
        # Check if answers come from same page/section
        same_page_answers = [q for q in similar_questions if q['chunk_page'] == chunk['page']]
        consistency = len(same_page_answers) / len(similar_questions)
        
        return consistency
    
    def _combine_confidence_factors(self, factors: Dict[str, float]) -> float:
        """Combine confidence factors with weighted scoring"""
        weights = {
            'keyword_relevance': 0.25,
            'context_richness': 0.20,
            'security_relevance': 0.20,
            'completeness': 0.20,
            'consistency': 0.15
        }
        
        weighted_sum = sum(factors[factor] * weights[factor] for factor in weights)
        final_confidence = weighted_sum * 100  # Convert to percentage
        
        return round(min(100, final_confidence), 1)
    
    def _generate_confidence_reasoning(self, factors: Dict[str, float]) -> str:
        """Generate detailed reasoning for confidence score"""
        reasoning_parts = []
        
        # Keyword relevance
        if factors['keyword_relevance'] > 0.7:
            reasoning_parts.append("✅ High keyword relevance")
        elif factors['keyword_relevance'] > 0.3:
            reasoning_parts.append("⚠️ Moderate keyword relevance")
        else:
            reasoning_parts.append("⚠️ Low keyword relevance")
        
        # Context richness
        if factors['context_richness'] > 0.7:
            reasoning_parts.append("✅ Rich context with detailed information")
        elif factors['context_richness'] > 0.3:
            reasoning_parts.append("⚠️ Moderate context - answer may be limited")
        else:
            reasoning_parts.append("⚠️ Limited context - answer may be incomplete")
        
        # Security relevance
        if factors['security_relevance'] > 0.5:
            reasoning_parts.append("✅ Strong security terminology match")
        else:
            reasoning_parts.append("⚠️ Limited security terminology")
        
        # Completeness
        if factors['completeness'] > 0.7:
            reasoning_parts.append("✅ Comprehensive answer coverage")
        elif factors['completeness'] > 0.3:
            reasoning_parts.append("⚠️ Partial answer coverage")
        else:
            reasoning_parts.append("⚠️ Limited answer coverage")
        
        # Consistency
        if factors['consistency'] > 0.7:
            reasoning_parts.append("✅ Consistent with historical answers")
        elif factors['consistency'] > 0.3:
            reasoning_parts.append("⚠️ Some inconsistency with history")
        else:
            reasoning_parts.append("⚠️ Inconsistent with historical answers")
        
        return " | ".join(reasoning_parts)

# Global RAG engine instance
_rag_engine = None

def load_and_query(pdf_file, question: str) -> Tuple[str, str]:
    """Convenience function for the main app"""
    global _rag_engine
    if _rag_engine is None:
        _rag_engine = RAGEngine()
    
    return _rag_engine.load_and_query(pdf_file, question)

def get_coverage_confidence(question: str) -> Tuple[float, str]:
    """Get confidence score and reasoning for a question"""
    global _rag_engine
    if _rag_engine is None:
        return 0.0, "RAG engine not initialized"
    
    return _rag_engine.get_coverage_confidence(question) 