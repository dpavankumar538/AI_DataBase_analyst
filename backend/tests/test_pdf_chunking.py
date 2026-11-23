
from app.services.pdf_chunking import (
    clean_text,
    chunk_pdf_pages,
)


def test_clean_text():
    text = "Hello     World\n\n\n\nThis is a test."
    result = clean_text(text)

    assert result == "Hello World\n\nThis is a test."


def test_chunk_pdf_pages():
    pages = [
        {
            "page_number": 1,
            "text": "This is a sample PDF document. " * 100,
        },
        {
            "page_number": 2,
            "text": "This is another PDF page. " * 100,
        },
    ]

    chunks = chunk_pdf_pages(
        pages,
        chunk_size=500,
        chunk_overlap=100,
    )

    assert len(chunks) > 1

    # Verify chunk metadata
    for chunk in chunks:
        assert "page_number" in chunk
        assert "chunk_index" in chunk
        assert "text" in chunk
        assert len(chunk["text"]) <= 500

    # Verify both pages were processed
    page_numbers = {chunk["page_number"] for chunk in chunks}

    assert page_numbers == {1, 2}


def test_empty_pages():
    pages = [
        {"page_number": 1, "text": ""},
        {"page_number": 2, "text": "   "},
    ]

    chunks = chunk_pdf_pages(pages)

    assert chunks == []


def test_invalid_chunk_size():
    import pytest

    with pytest.raises(ValueError):
        chunk_pdf_pages([], chunk_size=0)


def test_invalid_overlap():
    import pytest

    with pytest.raises(ValueError):
        chunk_pdf_pages([], chunk_size=500, chunk_overlap=500)
