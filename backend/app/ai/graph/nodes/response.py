
from app.ai.graph.state import AnalysisState
from app.ai.llm import get_llm_provider


def response_node(state: AnalysisState) -> dict:
    """Generate the final answer from structured and document analysis."""

    if state.get("error"):
        return {"final_answer": state["error"]}

    question = state.get("question", "").strip()
    structured_result = state.get("structured_result")
    document_context = state.get("document_context", [])

    if not structured_result and not document_context:
        return {
            "final_answer": (
                "I couldn't find any analysis results to answer your question. "
                "Please select a dataset, database, or document."
            )
        }

    # Build a readable document section that preserves page citations and
    # document-id references that were collected during retrieval.
    document_section = ""
    if document_context:
        lines = []
        for entry in document_context:
            doc_id = entry.get("document_id", "?")
            lines.append(f"[Document {doc_id}]")
            for chunk in entry.get("chunks", []):
                lines.append(
                    f"  [Page {chunk.get('page_number', '?')}] {chunk.get('text', '')}"
                )
        document_section = "\n".join(lines)
    else:
        document_section = "None"

    prompt = f"""
You are an AI data analysis assistant.

Answer the user's question using ONLY the supplied analysis results.

USER QUESTION:
{question}

STRUCTURED DATA ANALYSIS:
{structured_result}

DOCUMENT RETRIEVAL RESULTS:
{document_section}

INSTRUCTIONS:

1. Give a direct answer before providing detailed explanations.
2. Use actual calculated values from structured analysis.
3. Explain important patterns, comparisons, and numerical findings.
4. Present relevant tabular results clearly when useful.
5. Distinguish database results from document information.
6. Cite document page numbers when provided in the sources.
7. Never invent numbers, records, citations, or conclusions.
8. If results are insufficient, clearly explain what is missing.
9. Do not claim that an operation was performed unless its results confirm it.
10. Use simple, professional language.

FINAL ANSWER:
"""

    try:
        llm = get_llm_provider()
        answer = llm.generate_response(prompt)

        if not answer or not answer.strip():
            raise ValueError("Empty response from AI provider.")

        return {"final_answer": answer.strip()}

    except Exception:
        return {
            "final_answer": (
                "The analysis was completed, but I couldn't generate "
                "the final explanation. Please try again."
            )
        }
