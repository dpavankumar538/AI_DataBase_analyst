
from app.services.pdf_processing import extract_text_from_pdf


def test_pdf_extraction():
    pdf_path = input("Enter the PDF file path: ").strip().strip('"')

    result = extract_text_from_pdf(pdf_path)

    print("\nPDF extraction successful!")
    print("Total pages:", result["page_count"])

    for page in result["pages"]:
        print("\nPage:", page["page_number"])
        print("Method:", page["extraction_method"])
        print("Extracted text:")
        print(page["text"][:500])


if __name__ == "__main__":
    test_pdf_extraction()
