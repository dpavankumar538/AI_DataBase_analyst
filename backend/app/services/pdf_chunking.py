
import re

from langchain_text_splitters import RecursiveCharacterTextSplitter

def clean_text(text: str) -> str:
    """Clean extracted PDF text."""

    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()

def chunk_pdf_pages(
    pages: list,
    chunk_size: int = 3000,
    chunk_overlap: int = 400,
) -> list:
    """Split PDF pages into overlapping text chunks."""

    if chunk_size <= 0:
        raise ValueError("Chunk size must be positive.")

    if chunk_overlap < 0 or chunk_overlap >= chunk_size:
        raise ValueError("Overlap must be smaller than chunk size.")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""],
    )

    chunks = []

    for page in pages:
        page_number = page["page_number"]
        text = clean_text(page["text"])

        if not text:
            continue

        page_chunks = splitter.split_text(text)

        for chunk_index, chunk_text in enumerate(page_chunks):
            chunks.append({
                "page_number": page_number,
                "chunk_index": chunk_index,
                "text": chunk_text,
            })

    return chunks
