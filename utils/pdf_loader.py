import fitz  # PyMuPDF
import re
from typing import List, Dict, Tuple
import tiktoken

class PDFLoader:
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.encoding = tiktoken.get_encoding("cl100k_base")
    
    def load_pdf(self, pdf_file) -> List[Dict[str, any]]:
        """
        Load PDF and extract text with page information
        Returns list of chunks with metadata
        """
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
        chunks = []
        
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text()
            
            # Clean text
            text = self._clean_text(text)
            
            if text.strip():
                # Split into chunks
                page_chunks = self._split_text(text, page_num + 1)
                chunks.extend(page_chunks)
        
        doc.close()
        return chunks
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove page numbers and headers/footers
        text = re.sub(r'^\d+\s*$', '', text, flags=re.MULTILINE)
        return text.strip()
    
    def _split_text(self, text: str, page_num: int) -> List[Dict[str, any]]:
        """Split text into overlapping chunks"""
        # Tokenize text
        tokens = self.encoding.encode(text)
        chunks = []
        
        i = 0
        while i < len(tokens):
            # Get chunk tokens
            chunk_tokens = tokens[i:i + self.chunk_size]
            chunk_text = self.encoding.decode(chunk_tokens)
            
            if chunk_text.strip():
                chunks.append({
                    'text': chunk_text,
                    'page': page_num,
                    'start_token': i,
                    'end_token': min(i + self.chunk_size, len(tokens))
                })
            
            # Move to next chunk with overlap
            i += self.chunk_size - self.chunk_overlap
        
        return chunks
    
    def get_chunk_source(self, chunk: Dict[str, any]) -> str:
        """Format source citation for a chunk"""
        return f"Page {chunk['page']}" 