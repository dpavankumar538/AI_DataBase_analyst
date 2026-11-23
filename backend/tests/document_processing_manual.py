from app.services.document_processing import process_pdf_document


def test_document_processing():

    pdf_path = input("Enter PDF file path: ").strip().strip('"')

    result = process_pdf_document(
        file_path=pdf_path,
        user_id=1,
        document_id=1001,
    )

    print("\nPDF processing successful!")
    print("Total pages:", result["page_count"])
    print("Total chunks:", result["chunk_count"])
    print("Extraction methods:", result["extraction_methods"])


if __name__ == "__main__":
    test_document_processing()