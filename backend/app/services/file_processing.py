
from io import BytesIO
from pathlib import Path

import pandas as pd


SUPPORTED_EXTENSIONS = {".csv", ".xlsx", ".json"}


def process_uploaded_file(filename: str, content: bytes):
    """Read an uploaded file and extract its dataset metadata."""

    extension = Path(filename).suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            "Unsupported file type. Upload CSV, XLSX, or JSON."
        )

    if not content:
        raise ValueError("Uploaded file is empty.")

    file_buffer = BytesIO(content)

    try:
        if extension == ".csv":
            dataframe = pd.read_csv(file_buffer)

        elif extension == ".xlsx":
            dataframe = pd.read_excel(file_buffer, engine="openpyxl")

        elif extension == ".json":
            dataframe = pd.read_json(file_buffer)

    except Exception:
        raise ValueError(
            "Unable to read the uploaded file. "
            "Please check its format and contents."
        ) from None

    if dataframe.empty:
        raise ValueError("The uploaded dataset contains no rows.")

    if len(dataframe.columns) == 0:
        raise ValueError("The uploaded dataset contains no columns.")

    columns = [
        {
            "name": str(column),
            "data_type": str(dataframe[column].dtype)
        }
        for column in dataframe.columns
    ]

    metadata = {
        "row_count": len(dataframe),
        "column_count": len(dataframe.columns),
        "columns": columns
    }

    return dataframe, metadata
