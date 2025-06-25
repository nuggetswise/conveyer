import PyPDF2
import io
from typing import List, Dict
import re

class PDFLoader:
    def __init__(self):
        self.chunk_size = 500  # tokens
        self.overlap = 50      # tokens
    
    def load_pdf(self, pdf_file) -> List[Dict[str, any]]:
        """
        Load PDF and split into chunks
        Returns: List of chunks with text, page number, and metadata
        """
        try:
            # Read PDF content
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            chunks = []
            
            for page_num, page in enumerate(pdf_reader.pages, 1):
                # Extract text from page
                text = page.extract_text()
                if not text.strip():
                    continue
                
                # Split text into chunks
                page_chunks = self._split_text_into_chunks(text, page_num)
                chunks.extend(page_chunks)
            
            return chunks
            
        except Exception as e:
            print(f"Error loading PDF: {e}")
            return []
    
    def _split_text_into_chunks(self, text: str, page_num: int) -> List[Dict[str, any]]:
        """
        Split text into overlapping chunks
        """
        # Clean text
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Simple token estimation (roughly 4 characters per token)
        tokens = len(text) // 4
        chunk_size_chars = self.chunk_size * 4
        overlap_chars = self.overlap * 4
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size_chars
            
            # Don't break in the middle of a word
            if end < len(text):
                # Find the last space before the end
                last_space = text.rfind(' ', start, end)
                if last_space > start:
                    end = last_space
            
            chunk_text = text[start:end].strip()
            
            if chunk_text:
                chunks.append({
                    'text': chunk_text,
                    'page': page_num,
                    'start_char': start,
                    'end_char': end,
                    'tokens_estimate': len(chunk_text) // 4
                })
            
            # Move start position with overlap
            start = max(start + 1, end - overlap_chars)
            
            # Prevent infinite loop
            if start >= len(text):
                break
        
        return chunks
    
    def get_chunk_source(self, chunk: Dict[str, any]) -> str:
        """
        Generate source citation for a chunk
        """
        return f"Page {chunk['page']}"
    
    def get_chunk_metadata(self, chunk: Dict[str, any]) -> Dict[str, any]:
        """
        Get metadata for a chunk
        """
        return {
            'page': chunk['page'],
            'tokens': chunk['tokens_estimate'],
            'length': len(chunk['text'])
        } 