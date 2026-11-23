
from app.services.pdf_table_processing import extract_tables_from_pdf
import pandas as pd

def test_pdf_table_extraction():
    pdf_path = input("Enter PDF file path: ").strip().strip('"')
    # pdf_path = "C:/invalid_folder/missing.pdf"

    tables = extract_tables_from_pdf(pdf_path)

    print("\nPDF table extraction successful!")
    print("Total tables extracted:", len(tables))

    for index, result in enumerate(tables, start=1):
        print(f"\n--- Table {index} ---")
        print("Page:", result["page_number"])
        print("Table index:", result["table_index"])
        print("\nExtracted DataFrame:")
        print(result["dataframe"].to_string(index=False))
        print("\nDataFrame information:")
        print(result["dataframe"].info())

        print("\nDataFrame shape:")
        print(result["dataframe"].shape)

        print("\nDataFrame description:")
        print(result["dataframe"].describe(include="all"))
        df = result["dataframe"]

        # Convert columns to numeric wherever possible
        for column in df.columns:
            df[column] = df[column].astype(str).str.replace("\n", "", regex=False)
            df[column] = df[column].str.strip()

            original_non_null = df[column].notna().sum()
            converted = pd.to_numeric(df[column], errors="coerce")

            if converted.notna().sum() == df[column].notna().sum():
                df[column] = converted

        print("\nNumeric analysis:")
        print(df.describe())


if __name__ == "__main__":
    test_pdf_table_extraction()
