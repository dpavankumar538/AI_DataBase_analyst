from app.services.pdf_document_processing import (
    process_pdf_document as extract_pdf_content,
)
from app.services.pdf_chunking import chunk_pdf_pages
from app.ai.embeddings.gemini import GeminiEmbeddingProvider
from app.services.vector_store import store_chunks

def process_pdf_document(
    file_path: str,
    user_id: int,
    document_id: int,
) -> dict:
    """Extract, chunk, embed, and store a PDF document."""

    # 1. Extract text from PDF (OCR is used when necessary)
    extracted = extract_pdf_content(file_path)

    # 2. Split extracted pages into chunks
    chunks = chunk_pdf_pages(extracted["pages"])

    if not chunks:
        raise ValueError("No readable text chunks found in the PDF.")

    # 3. Generate embeddings using Gemini
    embedding_provider = GeminiEmbeddingProvider()

    texts = [chunk["text"] for chunk in chunks]

    embeddings = embedding_provider.embed_documents(texts)

    # 4. Store chunks and embeddings in ChromaDB
    stored_count = store_chunks(
        user_id=user_id,
        document_id=document_id,
        chunks=chunks,
        embeddings=embeddings,
    )

    return {
        "page_count": extracted["page_count"],
        "chunk_count": stored_count,
        "extraction_methods": list({
            page["extraction_method"]
            for page in extracted["pages"]
        }),
    }