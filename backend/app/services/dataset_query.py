import pandas as pd

def get_column_info(dataframe: pd.DataFrame, column_name: str) -> dict:
    """Return basic information about a specific column."""

    if column_name not in dataframe.columns:
        raise ValueError(f"Column '{column_name}' does not exist.")

    column = dataframe[column_name]

    return {
        "column_name": column_name,
        "data_type": str(column.dtype),
        "total_values": int(column.count()),
        "missing_values": int(column.isnull().sum()),
        "unique_values": int(column.nunique()),
    }



def get_column_statistics(dataframe: pd.DataFrame, column_name: str) -> dict:
    """Calculate statistical values for a numerical column."""

    if column_name not in dataframe.columns:
        raise ValueError(f"Column '{column_name}' does not exist.")

    column = dataframe[column_name]

    if not pd.api.types.is_numeric_dtype(column):
        raise ValueError(f"Column '{column_name}' is not numerical.")

    return {
        "column_name": column_name,
        "mean": float(column.mean()),
        "median": float(column.median()),
        "minimum": float(column.min()),
        "maximum": float(column.max()),
        "standard_deviation": float(column.std()),
    }


def get_value_counts(
    dataframe: pd.DataFrame,
    column_name: str,
) -> dict:
    """Count how frequently each value appears in a column."""

    if column_name not in dataframe.columns:
        raise ValueError(f"Column '{column_name}' does not exist.")

    counts = dataframe[column_name].value_counts(dropna=False)

    return {
        "column_name": column_name,
        "value_counts": {
            str(value): int(count)
            for value, count in counts.items()
        },
    }


def filter_dataset(
    dataframe: pd.DataFrame,
    column_name: str,
    operator: str,
    value,
) -> pd.DataFrame:
    """Filter dataset rows using a comparison operator."""

    if column_name not in dataframe.columns:
        raise ValueError(f"Column '{column_name}' does not exist.")

    operations = {
        "==": lambda column: column == value,
        "!=": lambda column: column != value,
        ">": lambda column: column > value,
        "<": lambda column: column < value,
        ">=": lambda column: column >= value,
        "<=": lambda column: column <= value,
    }

    if operator not in operations:
        raise ValueError("Unsupported comparison operator.")

    try:
        mask = operations[operator](dataframe[column_name])
        return dataframe[mask].copy()
    except (TypeError, ValueError):
        raise ValueError("The value is incompatible with this column.") from None



def get_correlation(
    dataframe: pd.DataFrame,
    column1: str,
    column2: str,
) -> dict:
    """Calculate correlation between two numerical columns."""

    for column_name in [column1, column2]:
        if column_name not in dataframe.columns:
            raise ValueError(
                f"Column '{column_name}' does not exist."
            )

        if not pd.api.types.is_numeric_dtype(dataframe[column_name]):
            raise ValueError(
                f"Column '{column_name}' must be numerical."
            )

    correlation = dataframe[column1].corr(dataframe[column2])

    return {
        "column1": column1,
        "column2": column2,
        "correlation": (
            float(correlation)
            if pd.notna(correlation)
            else None
        ),
    }
