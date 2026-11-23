
from pathlib import Path

import pymupdf
import pandas as pd


import re

def extract_tables_from_pdf(file_path: str) -> list:
    """Extract tables from a PDF and convert them into Pandas DataFrames."""

    path = Path(file_path)

    if not path.is_file():
        raise ValueError("PDF file not found.")

    extracted_tables = []

    try:
        with pymupdf.open(path) as pdf_document:
            for page_number, page in enumerate(pdf_document, start=1):

                tables = page.find_tables()

                for table_index, table in enumerate(tables.tables):
                    rows = table.extract()
                    rows = [
                        [clean_cell_value(cell) for cell in row]
                        for row in rows
                    ]

                    if not rows:
                        continue

                    # Use the first row as column headers
                    headers = [
                        str(cell).strip() if cell is not None else f"column_{i}"
                        for i, cell in enumerate(rows[0])
                    ]

                    df = pd.DataFrame(rows[1:], columns=headers)

                    # Remove completely empty rows and columns
                    df = df.dropna(how="all")
                    df = df.dropna(axis=1, how="all")

                    if df.empty:
                        continue

                    extracted_tables.append({
                        "page_number": page_number,
                        "table_index": table_index,
                        "dataframe": df,
                    })

    except ValueError:
        raise
    except Exception:
        raise ValueError("Unable to extract tables from this PDF.") from None

    return extracted_tables


def clean_cell_value(value):
    if value is None:
        return None

    value = str(value)
    value = re.sub(r"\s+", " ", value).strip()

    if not value:
        return None

    value = re.sub(r"[\s,.-]+$", "", value)

    return value.strip() or None