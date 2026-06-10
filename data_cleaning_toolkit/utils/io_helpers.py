"""I/O helper functions for loading and exporting CSV data."""
import pandas as pd
import io


def load_csv(uploaded_file) -> pd.DataFrame:
    """Load a CSV file with encoding fallback.
    Tries UTF-8 first, falls back to latin-1.
    All columns are loaded as strings (dtype=str).
    """
    try:
        return pd.read_csv(uploaded_file, dtype=str)
    except UnicodeDecodeError:
        uploaded_file.seek(0)
        return pd.read_csv(uploaded_file, dtype=str, encoding="latin-1")


def to_csv_bytes(df: pd.DataFrame) -> bytes:
    """Convert DataFrame to CSV bytes with UTF-8 BOM for Excel compatibility."""
    buffer = io.BytesIO()
    buffer.write(b"\xef\xbb\xbf")  # UTF-8 BOM
    df.to_csv(buffer, index=False, encoding="utf-8")
    return buffer.getvalue()


def generate_summary(tool_name, before_count, after_count, removed_count=0, extra_info=None):
    """Generate a summary dictionary for tool execution results."""
    summary = {
        "Tool": tool_name,
        "Rows before": f"{before_count:,}",
        "Rows after": f"{after_count:,}",
        "Rows removed / changed": f"{removed_count:,}",
    }
    if extra_info:
        summary.update(extra_info)
    return summary
