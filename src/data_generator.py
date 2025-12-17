from pathlib import Path
from typing import List, Dict
import numpy as np
import pandas as pd


def _random_ip(rng: np.random.Generator) -> str:
    return ".".join(str(rng.integers(1, 255)) for _ in range(4))


def generate_logs(output_path: Path,
                  seed: int = 42,
                  n_users: int = 50,
                  days: int = 14,
                  base_events_per_user: int = 80) -> pd.DataFrame:
    """Generate synthetic authentication logs with injected anomalies and save to CSV.

    Columns: user_id, timestamp, event_type, status, ip_address, device, location.
    """
    rng = np.random.default_rng(seed)

    devices = ["Windows", "macOS", "Linux", "Android", "iOS", "ChromeOS"]
    locations = [
        "New York", "San Francisco", "London", "Berlin", "Singapore",
        "Sydney", "Toronto", "Tokyo", "Paris", "Bengaluru"
    ]

    users = [f"user_{i:03d}" for i in range(1, n_users + 1)]

    start = pd.Timestamp.today().normalize() - pd.Timedelta(days=days)
    end = pd.Timestamp.today().normalize() + pd.Timedelta(days=1)

    records: List[Dict] = []

    # Normal behavior profiles
    user_profiles = {}
    for u in users:
        typical_hours = rng.integers(7, 20, size=3)  # morning/afternoon/evening
        user_devices = rng.choice(devices, size=rng.integers(1, 3), replace=False).tolist()
        user_ips = [_random_ip(rng) for _ in range(rng.integers(1, 3))]
        location = rng.choice(locations)
        user_profiles[u] = {
            "hours": typical_hours,
            "devices": user_devices,
            "ips": user_ips,
            "location": location,
        }

    # Generate baseline events
    for u in users:
        count = int(rng.poisson(lam=base_events_per_user))
        prof = user_profiles[u]
        for _ in range(count):
            day_offset = rng.uniform(0, (end - start).days)
            base_day = start + pd.Timedelta(days=int(day_offset))
            hour = int(rng.choice(prof["hours"]))
            minute = int(rng.integers(0, 60))
            second = int(rng.integers(0, 60))
            ts = base_day + pd.Timedelta(hours=hour, minutes=minute, seconds=second)
            status = "success" if rng.random() < 0.94 else "failure"
            device = rng.choice(prof["devices"])
            ip = rng.choice(prof["ips"])
            records.append({
                "user_id": u,
                "timestamp": ts.isoformat(),
                "event_type": "login",
                "status": status,
                "ip_address": ip,
                "device": device,
                "location": prof["location"],
            })

    # Inject anomalies
    # 1) Excessive failed logins
    for u in rng.choice(users, size=max(1, n_users // 10), replace=False):
        base = start + pd.Timedelta(days=int(rng.uniform(0, days)))
        for i in range(rng.integers(15, 35)):
            ts = base + pd.Timedelta(minutes=int(i))
            records.append({
                "user_id": u,
                "timestamp": ts.isoformat(),
                "event_type": "login",
                "status": "failure",
                "ip_address": _random_ip(rng),
                "device": rng.choice(devices),
                "location": user_profiles[u]["location"],
            })

    # 2) Logins at unusual hours (e.g., 02:00-04:00)
    for u in rng.choice(users, size=max(1, n_users // 10), replace=False):
        base = start + pd.Timedelta(days=int(rng.uniform(0, days)))
        for _ in range(rng.integers(20, 40)):
            hour = int(rng.integers(2, 5))
            minute = int(rng.integers(0, 60))
            ts = base + pd.Timedelta(hours=hour, minutes=minute)
            records.append({
                "user_id": u,
                "timestamp": ts.isoformat(),
                "event_type": "login",
                "status": "success" if rng.random() < 0.7 else "failure",
                "ip_address": rng.choice(user_profiles[u]["ips"]),
                "device": rng.choice(user_profiles[u]["devices"]),
                "location": user_profiles[u]["location"],
            })

    # 3) Sudden spikes in activity
    for u in rng.choice(users, size=max(1, n_users // 10), replace=False):
        base = start + pd.Timedelta(days=int(rng.uniform(0, days)))
        spike_size = int(rng.integers(100, 200))
        for i in range(spike_size):
            ts = base + pd.Timedelta(seconds=int(i))
            records.append({
                "user_id": u,
                "timestamp": ts.isoformat(),
                "event_type": "login",
                "status": "success" if rng.random() < 0.9 else "failure",
                "ip_address": rng.choice(user_profiles[u]["ips"]),
                "device": rng.choice(user_profiles[u]["devices"]),
                "location": user_profiles[u]["location"],
            })

    # 4) New IP/device usage
    for u in rng.choice(users, size=max(1, n_users // 10), replace=False):
        base = start + pd.Timedelta(days=int(rng.uniform(0, days)))
        for _ in range(rng.integers(10, 25)):
            hour = int(rng.integers(0, 24))
            ts = base + pd.Timedelta(hours=hour)
            records.append({
                "user_id": u,
                "timestamp": ts.isoformat(),
                "event_type": "login",
                "status": "success",
                "ip_address": _random_ip(rng),
                "device": rng.choice(devices),
                "location": rng.choice(locations),
            })

    df = pd.DataFrame.from_records(records)
    df = df.sample(frac=1.0, random_state=seed).reset_index(drop=True)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    return df


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[1]
    out = project_root / "data" / "raw_logs.csv"
    generate_logs(out)
    print(f"Synthetic logs written to: {out}")