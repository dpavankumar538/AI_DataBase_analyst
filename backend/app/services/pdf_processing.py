
from pathlib import Path
from io import BytesIO

import pymupdf
import pytesseract
from PIL import Image

from app.core.config import TESSERACT_CMD


# Configure the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD


def extract_text_from_pdf(file_path: str) -> dict:
    """Extract text from digital and scanned PDF pages."""

    path = Path(file_path)

    if not path.is_file():
        raise ValueError("PDF file not found.")

    pages = []
    extracted_text = []

    try:
        with pymupdf.open(path) as pdf_document:

            for page_number, page in enumerate(pdf_document, start=1):

                # First, attempt normal text extraction
                text = page.get_text("text").strip()

                if text:
                    extraction_method = "text_extraction"

                else:
                    # If no text exists, use OCR
                    matrix = pymupdf.Matrix(200 / 72, 200 / 72)
                    pixmap = page.get_pixmap(matrix=matrix)

                    image_bytes = pixmap.tobytes("png")
                    image = Image.open(BytesIO(image_bytes))

                    text = pytesseract.image_to_string(
                        image,
                        lang="eng"
                    ).strip()

                    extraction_method = "ocr"

                pages.append({
                    "page_number": page_number,
                    "text": text,
                    "extraction_method": extraction_method,
                })

                extracted_text.append(text)

    except ValueError:
        raise
    except Exception:
        raise ValueError(
            "Unable to process this PDF file."
        ) from None

    full_text = "\n\n".join(extracted_text)

    if not full_text.strip():
        raise ValueError("No readable text found in the PDF.")

    return {
        "page_count": len(pages),
        "pages": pages,
        "full_text": full_text,
    }
