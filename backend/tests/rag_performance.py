
import time

from app.ai.embeddings.gemini import GeminiEmbeddingProvider
from app.ai.llm.gemini import GeminiLLMProvider
from app.services.vector_store import search_chunks


question = "What is the Turing Test in artificial intelligence?"

user_id = 1
document_id = 1001
top_k = 3

print("\n--- RAG Performance Test ---")

# 1. Query embedding
embedding_provider = GeminiEmbeddingProvider()

start = time.perf_counter()
query_embedding = embedding_provider.embed_query(question)
embedding_time = time.perf_counter() - start

print(f"1. Query embedding: {embedding_time:.2f} seconds")

# 2. ChromaDB retrieval
start = time.perf_counter()

results = search_chunks(
    user_id=user_id,
    document_id=document_id,
    query_embedding=query_embedding,
    top_k=top_k,
)

retrieval_time = time.perf_counter() - start

print(f"2. ChromaDB retrieval: {retrieval_time:.2f} seconds")

documents = results["documents"][0]
metadatas = results["metadatas"][0]

if not documents:
    print("\nNo document chunks found. Cannot continue.")
    raise SystemExit

# 3. Context preparation
start = time.perf_counter()

context = "\n\n".join(
    f"[Page {metadata['page_number']}]\n{text}"
    for text, metadata in zip(documents, metadatas)
)

prompt = f"""
Answer using ONLY the document context below.

If the answer is unavailable, say so.
Cite page numbers using [Page N].

DOCUMENT CONTEXT:
{context}

QUESTION:
{question}
"""

context_time = time.perf_counter() - start

print(f"3. Context preparation: {context_time:.2f} seconds")

# 4. Gemini answer generation
llm = GeminiLLMProvider()

start = time.perf_counter()
print("\n--- LLM Prompt Diagnostics ---")
print("Prompt characters:", len(prompt))
print("Prompt words:", len(prompt.split()))
print("------------------------------\n")
answer = llm.generate_response(prompt)
generation_time = time.perf_counter() - start

print(f"4. Gemini answer generation: {generation_time:.2f} seconds")

# Results
total_time = (
    embedding_time
    + retrieval_time
    + context_time
    + generation_time
)

print("\n--- Timing Summary ---")
print(f"Embedding:    {embedding_time:.2f}s")
print(f"Retrieval:    {retrieval_time:.2f}s")
print(f"Context:      {context_time:.2f}s")
print(f"Generation:   {generation_time:.2f}s")
print(f"Total:        {total_time:.2f}s")

print("\n--- Generated Answer ---")
print(answer)
