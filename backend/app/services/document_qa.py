from app.services.document_retrieval import retrieve_document_context
from app.ai.llm.gemini import GeminiLLMProvider

def answer_document_question(
    question: str,
    user_id: int,
    document_id: int = None,
    top_k: int = 5,
) -> dict:
    """Answer questions using retrieved PDF context."""

    # 1. Retrieve relevant PDF chunks
    context_chunks = retrieve_document_context(
        question=question,
        user_id=user_id,
        document_id=document_id,
        top_k=top_k,
    )

    if not context_chunks:
        return {
            "answer": "I could not find relevant information in the selected documents.",
            "sources": [],
        }

    # 2. Prepare context with page numbers
    context = "\n\n".join(
        f"[Page {chunk['page_number']}]\n{chunk['text']}"
        for chunk in context_chunks
    )

    # 3. Create the prompt
    prompt = f"""
You are an AI document analysis assistant.

Answer the user's question using ONLY the information
provided in the document context below.

Instructions:
1. Do not invent facts or use outside knowledge.
2. If the context does not contain enough information,
   clearly say so.
3. Give a clear and easy-to-understand answer.
4. Cite the relevant page numbers using [Page N].
5. Do not invent page numbers.

DOCUMENT CONTEXT:
{context}

USER QUESTION:
{question}

ANSWER:
"""

    # 4. Generate the answer using the configured LLM provider
    llm = GeminiLLMProvider()
    answer = llm.generate_response(prompt)

    # 5. Return answer and source information
    sources = [
        {
            "page_number": chunk["page_number"],
            "distance": chunk["distance"],
        }
        for chunk in context_chunks
    ]

    return {
        "answer": answer,
        "sources": sources,
    }