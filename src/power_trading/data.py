"""Illustrative deterministic sample data; NOT live EPEX/EEX/ICE settlements."""
import numpy as np
import pandas as pd


def synthetic_power_market(n_days: int = 180, seed: int = 21) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    t = np.arange(n_days)
    gas = 37 + 7 * np.cos(2 * np.pi * t / 180) + rng.normal(0, 2, n_days)
    eua = 74 + 4 * np.sin(2 * np.pi * t / 120) + rng.normal(0, 1.8, n_days)
    forecast = gas / 0.55 + eua * 0.202 / 0.55 + 3 + 7 * np.sin(2 * np.pi * t / 21) + rng.normal(0, 10, n_days)
    return pd.DataFrame({
        "date": pd.date_range("2025-01-01", periods=n_days).strftime("%Y-%m-%d"),
        "forecast_power": np.round(forecast, 2),
        "forward_gas": np.round(gas, 2),
        "forward_eua": np.round(eua, 2),
        "realized_power": np.round(forecast + rng.normal(0, 8, n_days), 2),
        "realized_gas": np.round(gas + rng.normal(0, 1.5, n_days), 2),
        "realized_eua": np.round(eua + rng.normal(0, 0.8, n_days), 2),
        "hours": np.full(n_days, 12),
    })
