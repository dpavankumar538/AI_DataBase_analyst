
from app.services.pdf_processing import extract_text_from_pdf
from app.services.pdf_table_processing import extract_tables_from_pdf


def process_pdf_document(file_path: str) -> dict:
    """
    Extract text and tables from a PDF document.

    Text extraction supports both digital and scanned PDFs.
    Table extraction returns Pandas DataFrames.
    """

    # Extract text from all PDF pages
    text_result = extract_text_from_pdf(file_path)

    # Extract tables and convert them into DataFrames
    tables = extract_tables_from_pdf(file_path)

    return {
        "page_count": text_result["page_count"],
        "pages": text_result["pages"],
        "full_text": text_result["full_text"],
        "tables": tables,
        "table_count": len(tables),
    }
