

from pathlib import Path
import pandas as pd


def read_sources_csv(csv_path):

    path = Path(csv_path)

    if not path.exists():
        raise FileNotFoundError(f"Sources CSV not found: {csv_path}")

    df = pd.read_csv(path)

    required_columns = {"platform", "source_name", "url"}
    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(f"Missing required columns in sources CSV: {missing_columns}")

    sources = []

    for _, row in df.iterrows():
        platform = str(row["platform"]).strip()
        source_name = str(row["source_name"]).strip()
        url = str(row["url"]).strip()

        if platform and source_name and url:
            sources.append({
                "platform": platform,
                "source_name": source_name,
                "url": url,
            })

    return sources


def read_text_file(file_path):

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    return path.read_text(encoding="utf-8", errors="ignore")


def save_text_file(file_path, text):

    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def save_results(results, csv_path, excel_path=None):

    output_csv = Path(csv_path)
    output_csv.parent.mkdir(parents=True, exist_ok=True)

    df = pd.DataFrame(results)

    if df.empty:
        df.to_csv(output_csv, index=False)
    else:
        df.to_csv(output_csv, index=False)

    if excel_path:
        output_excel = Path(excel_path)
        output_excel.parent.mkdir(parents=True, exist_ok=True)
        df.to_excel(output_excel, index=False)

    return df


def save_summary(df, csv_path, excel_path=None):

    output_csv = Path(csv_path)
    output_csv.parent.mkdir(parents=True, exist_ok=True)

    if df.empty:
        summary_df = pd.DataFrame()
    else:
        summary_df = (
            df.groupby(["platform", "source_name", "data_category"])
            .size()
            .reset_index(name="match_count")
            .sort_values(by=["platform", "source_name", "match_count"], ascending=[True, True, False])
        )

    summary_df.to_csv(output_csv, index=False)

    if excel_path:
        output_excel = Path(excel_path)
        output_excel.parent.mkdir(parents=True, exist_ok=True)
        summary_df.to_excel(output_excel, index=False)

    return summary_df