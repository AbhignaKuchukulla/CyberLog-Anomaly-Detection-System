from typing import Tuple
import pandas as pd


def build_features(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Build ML-ready numeric features per event.

    Returns (features_df, reference_df) where reference_df carries user_id and timestamp.
    """
    # Hour of day
    hour_of_day = df["timestamp"].dt.hour.fillna(0).astype(int)

    # Per-user aggregates
    counts_per_user = df.groupby("user_id").size().rename("login_frequency_per_user")
    failed_ratio = (
        (df["status"].eq("failure")).groupby(df["user_id"]).mean().rename("failed_login_ratio")
    )
    unique_ips = df.groupby("user_id")["ip_address"].nunique().rename("unique_ip_count")

    # Map aggregates back to each event
    features = pd.DataFrame({
        "hour_of_day": hour_of_day,
        "login_frequency_per_user": df["user_id"].map(counts_per_user).fillna(0).astype(float),
        "failed_login_ratio": df["user_id"].map(failed_ratio).fillna(0.0).astype(float),
        "unique_ip_count": df["user_id"].map(unique_ips).fillna(0).astype(float),
    })

    reference = df[["user_id", "timestamp", "status", "ip_address", "device", "location"]].copy()
    return features, reference