from pathlib import Path
from typing import Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

# Support running as a script or as a module
try:
    from .features import build_features  # type: ignore
except ImportError:  # pragma: no cover
    from features import build_features  # type: ignore


def run_isolation_forest(features_df: pd.DataFrame, random_state: int = 42) -> Tuple[pd.DataFrame, IsolationForest]:
    """Scale features, fit IsolationForest, return scores and labels per event."""
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(features_df.values)

    iso = IsolationForest(random_state=random_state)
    iso.fit(X_scaled)

    # Higher decision_function => more normal; invert for anomaly_score
    decision = iso.decision_function(X_scaled)
    anomaly_score = -decision
    labels = iso.predict(X_scaled)  # -1 anomalous, 1 normal
    anomaly_label = (labels == -1).astype(int)

    scores_df = pd.DataFrame({
        "anomaly_score": anomaly_score,
        "anomaly_label": anomaly_label,
    })
    return scores_df, iso


def plot_login_activity(processed_df: pd.DataFrame, output_path: Path) -> Path:
    ts = processed_df.set_index("timestamp").sort_index()
    counts = ts.resample("h").size()
    plt.figure(figsize=(10, 4))
    counts.plot()
    plt.title("Login Activity Over Time (Hourly)")
    plt.xlabel("Time")
    plt.ylabel("Count")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    return output_path


def plot_anomaly_score_distribution(scores_df: pd.DataFrame, output_path: Path) -> Path:
    plt.figure(figsize=(8, 4))
    plt.hist(scores_df["anomaly_score"], bins=40, color="steelblue", edgecolor="white")
    plt.title("Anomaly Score Distribution")
    plt.xlabel("Anomaly Score (higher = more anomalous)")
    plt.ylabel("Frequency")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    return output_path


def plot_normal_vs_anomalous(features_df: pd.DataFrame, scores_df: pd.DataFrame, output_path: Path) -> Path:
    plt.figure(figsize=(8, 5))
    labels = scores_df["anomaly_label"].values
    # Simple 2D: hour_of_day vs login_frequency_per_user
    x = features_df["hour_of_day"].values
    y = features_df["login_frequency_per_user"].values
    plt.scatter(x[labels == 0], y[labels == 0], s=16, c="green", alpha=0.6, label="Normal")
    plt.scatter(x[labels == 1], y[labels == 1], s=18, c="red", alpha=0.7, label="Anomalous")
    plt.title("Normal vs Anomalous Behavior")
    plt.xlabel("Hour of Day")
    plt.ylabel("Login Frequency per User")
    plt.legend()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    return output_path


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[1]
    processed_path = project_root / "data" / "processed_logs.csv"
    visuals_dir = project_root / "visuals"

    df = pd.read_csv(processed_path, parse_dates=["timestamp"]) if processed_path.exists() else None
    if df is None:
        raise FileNotFoundError("Processed logs not found. Run preprocessing.py first.")

    features_df, ref_df = build_features(df)
    scores_df, model = run_isolation_forest(features_df)

    # Save visuals
    plot_login_activity(df, visuals_dir / "login_activity_over_time.png")
    plot_anomaly_score_distribution(scores_df, visuals_dir / "anomaly_score_distribution.png")
    plot_normal_vs_anomalous(features_df, scores_df, visuals_dir / "normal_vs_anomalous_behavior.png")

    # Basic summary output
    n_anom = int(scores_df["anomaly_label"].sum())
    print(f"Anomalies detected: {n_anom} / {len(scores_df)} events")