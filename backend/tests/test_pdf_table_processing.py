
import pytest

from app.services.pdf_table_processing import (
    clean_cell_value,
    extract_tables_from_pdf,
)


@pytest.mark.parametrize(
    "input_value, expected",
    [
        ("259200 ,", "259200"),
        ("125000 ,", "125000"),
        ("ORD 1001\n-", "ORD 1001"),
        ("  Corporate  ", "Corporate"),
        (None, None),
    ],
)
def test_clean_cell_value(input_value, expected):
    assert clean_cell_value(input_value) == expected


def test_extract_tables_file_not_found(tmp_path):
    missing_file = tmp_path / "missing.pdf"

    with pytest.raises(ValueError, match="PDF file not found."):
        extract_tables_from_pdf(str(missing_file))


def test_extract_tables_success(tmp_path):
    import pymupdf

    pdf_path = tmp_path / "sample_table.pdf"

    # Create a temporary PDF containing a simple table.
    with pymupdf.open() as pdf:
        page = pdf.new_page()
        page.insert_text((50, 50), "Sample PDF Table")

        page.draw_line((50, 80), (350, 80))
        page.draw_line((50, 110), (350, 110))
        page.draw_line((50, 140), (350, 140))
        page.draw_line((50, 80), (50, 140))
        page.draw_line((200, 80), (200, 140))
        page.draw_line((350, 80), (350, 140))

        page.insert_text((60, 100), "Name")
        page.insert_text((210, 100), "Age")
        page.insert_text((60, 130), "Pavan")
        page.insert_text((210, 130), "23")

        pdf.save(pdf_path)

    tables = extract_tables_from_pdf(str(pdf_path))
    assert len(tables) >= 1

    df = tables[0]["dataframe"]

    assert list(df.columns) == ["Name", "Age"]
    assert len(df) == 1
    assert df.iloc[0]["Name"] == "Pavan"
    assert str(df.iloc[0]["Age"]) == "23"
