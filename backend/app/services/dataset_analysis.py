
from pathlib import Path

import pandas as pd
from sqlalchemy.orm import Session

from app.models.dataset import Dataset
from app.models.data_source import DataSource


def get_user_dataset(
    db: Session,
    dataset_id: int,
    user_id: int,
) -> tuple[Dataset, DataSource]:

    dataset = (
        db.query(Dataset)
        .filter(
            Dataset.id == dataset_id,
            Dataset.user_id == user_id,
        )
        .first()
    )

    if dataset is None:
        raise ValueError("Dataset not found.")

    data_source = (
        db.query(DataSource)
        .filter(
            DataSource.id == dataset.data_source_id,
            DataSource.user_id == user_id,
        )
        .first()
    )

    if data_source is None:
        raise ValueError("Data source not found.")

    return dataset, data_source


def load_dataset(data_source: DataSource) -> pd.DataFrame:
    """Load an uploaded dataset into a Pandas DataFrame."""

    if data_source.source_type != "file":
        raise ValueError("This data source is not an uploaded file.")

    if not data_source.file_path:
        raise ValueError("Dataset file path is missing.")

    file_path = Path(data_source.file_path).resolve()

    project_root = Path(__file__).resolve().parents[2]
    storage_root = (project_root / "storage" / "uploads").resolve()

    # Ensure the file belongs to the managed upload directory.
    if not file_path.is_relative_to(storage_root):
        raise ValueError("Invalid dataset file location.")

    if not file_path.is_file():
        raise ValueError("Dataset file not found in storage.")

    extension = file_path.suffix.lower()

    try:
        if extension == ".csv":
            dataframe = pd.read_csv(file_path)

        elif extension == ".xlsx":
            dataframe = pd.read_excel(
                file_path,
                engine="openpyxl"
            )

        elif extension == ".json":
            dataframe = pd.read_json(file_path)

        else:
            raise ValueError("Unsupported dataset file type.")

    except ValueError:
        raise

    except Exception:
        raise ValueError(
            "Unable to read the stored dataset."
        ) from None

    if dataframe.empty:
        raise ValueError("Dataset contains no rows.")

    return dataframe


def generate_dataset_overview(dataframe: pd.DataFrame) -> dict:
    """Generate a basic overview of a dataset."""

    columns = []

    for column in dataframe.columns:
        columns.append({
            "name": str(column),
            "data_type": str(dataframe[column].dtype),
            "missing_values": int(dataframe[column].isnull().sum()),
            "unique_values": int(dataframe[column].nunique()),
        })

    overview = {
        "row_count": int(dataframe.shape[0]),
        "column_count": int(dataframe.shape[1]),
        "columns": columns,
        "memory_usage_bytes": int(
            dataframe.memory_usage(deep=True).sum()
        ),
    }

    return overview



def generate_statistical_summary(dataframe: pd.DataFrame) -> dict:
    """Generate statistical summaries for numerical columns."""

    numerical_data = dataframe.select_dtypes(
        include="number"
    )

    if numerical_data.empty:
        return {}

    summary = numerical_data.describe().round(2)

    return {
        column: {
            statistic: float(value)
            for statistic, value in summary[column].items()
        }
        for column in summary.columns
    }


def analyze_user_dataset(
    db: Session,
    dataset_id: int,
    user_id: int,
) -> dict:
    """Analyze an authenticated user's uploaded dataset."""

    # 1. Retrieve dataset and verify ownership
    dataset, data_source = get_user_dataset(
        db=db,
        dataset_id=dataset_id,
        user_id=user_id,
    )

    # 2. Load the actual file into Pandas
    dataframe = load_dataset(data_source)

    # 3. Generate dataset overview
    overview = generate_dataset_overview(dataframe)

    # 4. Generate statistical summary
    statistics = generate_statistical_summary(dataframe)

    # 5. Return combined results
    return {
        "dataset_id": dataset.id,
        "dataset_name": dataset.dataset_name,
        "overview": overview,
        "statistics": statistics,
    }
