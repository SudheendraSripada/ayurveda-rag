import os
import re
from pypdf import PdfReader

def clean_text(text: str) -> str:
    """Normalize whitespace and strip out invalid characters."""
    if not text:
        return ""
    # Strip carriage returns
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    # Replace horizontal whitespace sequences with a single space
    text = re.sub(r'[ \t]+', ' ', text)
    # Remove whitespace before and after newlines
    text = re.sub(r' ?\n ?', '\n', text)
    # Remove multiple consecutive blank lines (limit to 2 newlines)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def chunk_text(text: str, chunk_size: int = 800, overlap: int = 150) -> list[str]:
    """Split text into overlapping chunks of rough chunk_size character length."""
    if not text:
        return []
    
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    stride = max(1, chunk_size - overlap)
    
    while start < len(text):
        end = min(start + chunk_size, len(text))
        if end == len(text):
            chunk = text[start:].strip()
            if chunk:
                chunks.append(chunk)
            break
            
        # Try to find a delimiter near end
        split_index = end
        max_lookback = min(overlap, 100, end - start - 1)
        if max_lookback > 0:
            for diff in range(max_lookback):
                char_pos = end - diff
                if char_pos <= start:
                    break
                if text[char_pos] in ['\n', '.', '!', '?']:
                    split_index = char_pos + 1
                    break
                elif text[char_pos] == ' ' and split_index == end:
                    split_index = char_pos + 1
                    
        chunk = text[start:split_index].strip()
        if chunk:
            chunks.append(chunk)
            
        # Advance start safely with guarantee of forward progression
        next_start = split_index - overlap
        if next_start <= start:
            next_start = start + stride
        start = next_start
        
    return [c for c in chunks if len(c) > 0]

def parse_pdf(file_path: str, chunk_size: int = 800, overlap: int = 150) -> list[dict]:
    """Parse PDF file page by page and return list of overlapping text chunks with metadata."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
        
    reader = PdfReader(file_path)
    filename = os.path.basename(file_path)
    all_chunks = []
    
    for page_idx, page in enumerate(reader.pages):
        page_num = page_idx + 1
        raw_text = page.extract_text() or ""
        cleaned_text = clean_text(raw_text)
        
        if not cleaned_text:
            continue
            
        page_chunks = chunk_text(cleaned_text, chunk_size=chunk_size, overlap=overlap)
        
        for chunk_idx, chunk_text_content in enumerate(page_chunks):
            # Clean up filename for the ID to be alphanumeric + symbols allowed by Pinecone
            safe_filename = re.sub(r'[^a-zA-Z0-9\._-]', '_', filename)
            chunk_id = f"{safe_filename}_p{page_num}_c{chunk_idx}"
            
            all_chunks.append({
                "id": chunk_id,
                "text": chunk_text_content,
                "source_book": filename,
                "page_number": page_num,
                "chunk_index": chunk_idx
            })
            
    return all_chunks

if __name__ == "__main__":
    print("PDF Parser module initialized successfully.")
