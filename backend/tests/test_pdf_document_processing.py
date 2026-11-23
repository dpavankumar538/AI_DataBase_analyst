
from app.services import pdf_document_processing

import pymupdf
import pandas as pd



def test_process_pdf_document(monkeypatch):
    # Mock the text extraction result
    def mock_extract_text(file_path):
        return {
            "page_count": 2,
            "pages": [
                {
                    "page_number": 1,
                    "text": "Sample PDF text",
                    "extraction_method": "text_extraction",
                },
                {
                    "page_number": 2,
                    "text": "Another page",
                    "extraction_method": "ocr",
                },
            ],
            "full_text": "Sample PDF text\n\nAnother page",
        }

    # Mock the table extraction result
    sample_tables = [
        {
            "page_number": 1,
            "table_index": 0,
            "dataframe": "sample_dataframe",
        }
    ]

    def mock_extract_tables(file_path):
        return sample_tables

    # Replace the actual functions with our mock functions
    monkeypatch.setattr(
        pdf_document_processing,
        "extract_text_from_pdf",
        mock_extract_text,
    )

    monkeypatch.setattr(
        pdf_document_processing,
        "extract_tables_from_pdf",
        mock_extract_tables,
    )

    # Call the unified service
    result = pdf_document_processing.process_pdf_document("sample.pdf")

    # Verify the result
    assert result["page_count"] == 2
    assert len(result["pages"]) == 2
    assert result["full_text"] == "Sample PDF text\n\nAnother page"
    assert result["tables"] == sample_tables
    assert result["table_count"] == 1


def test_process_real_pdf(tmp_path):
    # Create a sample PDF
    pdf_path = tmp_path / "sample_document.pdf"

    with pymupdf.open() as pdf:
        page = pdf.new_page()

        # Add normal text
        page.insert_text(
            (50, 50),
            "Employee Information",
            fontsize=16,
        )

        page.insert_text(
            (50, 70),
            "This document contains employee details.",
        )

        # Draw a table
        page.draw_line((50, 100), (350, 100))
        page.draw_line((50, 130), (350, 130))
        page.draw_line((50, 160), (350, 160))

        page.draw_line((50, 100), (50, 160))
        page.draw_line((200, 100), (200, 160))
        page.draw_line((350, 100), (350, 160))

        page.insert_text((60, 120), "Name")
        page.insert_text((210, 120), "Age")

        page.insert_text((60, 150), "Pavan")
        page.insert_text((210, 150), "23")

        pdf.save(pdf_path)

    # Process the actual PDF
    result = pdf_document_processing.process_pdf_document(
        str(pdf_path)
    )

    # Verify text extraction
    assert result["page_count"] == 1
    assert "Employee Information" in result["full_text"]
    assert "employee details" in result["full_text"]

    # Verify table extraction
    assert result["table_count"] >= 1

    df = result["tables"][0]["dataframe"]

    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == ["Name", "Age"]
    assert df.iloc[0]["Name"] == "Pavan"
    assert str(df.iloc[0]["Age"]) == "23"
