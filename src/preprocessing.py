from pathlib import Path
import pandas as pd


def clean_logs(input_path: Path, output_path: Path) -> pd.DataFrame:
    """Clean raw logs: handle missing values, parse timestamps, remove duplicates."""
    df = pd.read_csv(input_path)

    # Basic missing handling
    df["user_id"] = df["user_id"].fillna("unknown")
    df["event_type"] = df["event_type"].fillna("login")
    df["status"] = df["status"].fillna("failure")
    df["ip_address"] = df["ip_address"].fillna("0.0.0.0")
    df["device"] = df["device"].fillna("unknown")
    df["location"] = df["location"].fillna("unknown")

    # Parse and normalize timestamps
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.dropna(subset=["timestamp", "user_id"])  # drop rows without critical fields

    # Remove exact duplicates
    df = df.drop_duplicates()

    # Sort by time
    df = df.sort_values("timestamp").reset_index(drop=True)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    return df


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[1]
    inp = project_root / "data" / "raw_logs.csv"
    out = project_root / "data" / "processed_logs.csv"
    df = clean_logs(inp, out)
    print(f"Processed logs written to: {out}; rows={len(df)}")