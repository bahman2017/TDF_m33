"""Load and save processed M33 CSV tables without altering scientific values."""

from pathlib import Path

import pandas as pd

from tdf_m33.data.schema import REQUIRED_COLUMNS


def load_m33_processed_csv(path: str | Path) -> pd.DataFrame:
    """Load a processed M33 CSV into a DataFrame.

    Does not coerce, fill, or rescale scientific columns. Callers should run
    ``validate_m33_dataframe`` or ``assert_valid_m33_dataframe`` after load.
    """
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"Processed M33 CSV not found: {path}")
    return pd.read_csv(path)


def save_m33_processed_csv(df: pd.DataFrame, path: str | Path) -> None:
    """Write a DataFrame to CSV without modifying in-memory values.

    Ensures required column names are present before writing; does not validate
    row-level constraints (use validation before save in pipelines).
    """
    path = Path(path)
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Cannot save M33 processed CSV: missing columns {missing}")
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
