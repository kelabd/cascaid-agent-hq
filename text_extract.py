from io import BytesIO
from pypdf import PdfReader

def pdf_bytes_to_text(data: bytes, max_pages: int | None = None) -> str:
    """Basic text extraction; good enough for a smoke test."""
    reader = PdfReader(BytesIO(data))
    pages = reader.pages if max_pages is None else reader.pages[:max_pages]
    chunks = []
    for p in pages:
        try:
            chunks.append(p.extract_text() or "")
        except Exception:
            pass
    return "\n\n".join(chunks).strip()
