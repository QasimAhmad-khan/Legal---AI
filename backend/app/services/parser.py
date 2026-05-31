import io
import re
from typing import List, Dict, Any
import pdfplumber
from docx import Document

class ChunkResult:
    def __init__(self, text: str, start: int, end: int, clause_type: str = "unknown"):
        self.text = text
        self.char_start = start
        self.char_end = end
        self.clause_type = clause_type

def parse_pdf(file_bytes: bytes) -> str:
    text = ""
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
    return text

def parse_docx(file_bytes: bytes) -> str:
    doc = Document(io.BytesIO(file_bytes))
    return "\n".join([paragraph.text for paragraph in doc.paragraphs])

def extract_text(file_bytes: bytes, filename: str) -> str:
    if filename.lower().endswith('.pdf'):
        return parse_pdf(file_bytes)
    elif filename.lower().endswith('.docx'):
        return parse_docx(file_bytes)
    else:
        # Fallback for text files
        return file_bytes.decode('utf-8')

def segment_clauses(text: str) -> List[ChunkResult]:
    # Simple heuristic: split by double newlines or numbered headings
    # In a real app, this might use an LLM or a more complex regex
    chunks = []
    
    # Very basic regex to find sections like "1.", "1.1", "Article 1"
    # For now, just split by double newline to get paragraphs/clauses
    paragraphs = re.split(r'\n\s*\n', text)
    
    current_pos = 0
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        
        # approximate location in original text
        start_idx = text.find(para, current_pos)
        if start_idx == -1:
            start_idx = current_pos
            
        end_idx = start_idx + len(para)
        
        chunks.append(ChunkResult(
            text=para,
            start=start_idx,
            end=end_idx
        ))
        current_pos = end_idx

    return chunks
