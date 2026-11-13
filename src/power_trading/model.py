"""Simplified spark-spread and dispatch model; energy units are explicit."""
from dataclasses import dataclass
import numpy as np
import pandas as pd


@dataclass(frozen=True)
class Plant:
    efficiency: float = 0.55         # MWh_e delivered / MWh_th consumed
    emissions_t_per_mwh_th: float = 0.202  # tonnes of CO2 per MWh_th
    variable_om_eur_mwh_e: float = 3.0
    capacity_mw: float = 250.0
    hurdle_eur_mwh_e: float = 0.0

    def __post_init__(self):
        if not 0 < self.efficiency <= 1 or self.emissions_t_per_mwh_th < 0 or self.variable_om_eur_mwh_e < 0 or self.capacity_mw <= 0:
            raise ValueError("Invalid power-plant parameters")


def clean_spark_spread(power_eur_mwh_e, gas_eur_mwh_th,
                       eua_eur_tco2, plant: Plant = Plant()):
    """€/MWh_e: power − gas/efficiency − EUA*emissions/efficiency − variable O&M."""
    return (power_eur_mwh_e - gas_eur_mwh_th / plant.efficiency
            - eua_eur_tco2 * plant.emissions_t_per_mwh_th / plant.efficiency
            - plant.variable_om_eur_mwh_e)


REQUIRED = {"date", "forecast_power", "forward_gas", "forward_eua", "realized_power",
            "realized_gas", "realized_eua", "hours"}


def dispatch_backtest(frame: pd.DataFrame, plant: Plant = Plant()) -> pd.DataFrame:
    """Forecast-based day-ahead dispatch and realized gross contribution.

    The trading decision uses ONLY forecast/forward columns; realized columns
    affect P&L, never the decision. Assumes 100% availability, no start-up or
    ramp costs, no imbalance penalties, no gas transport or hedge slippage.
    """
    if not REQUIRED.issubset(frame):
        raise ValueError(f"Missing columns: {sorted(REQUIRED - set(frame))}")
    df = frame.copy()
    df["date"] = pd.to_datetime(df["date"], errors="raise")
    df = df.sort_values("date").reset_index(drop=True)
    if df["date"].duplicated().any():
        raise ValueError("Dates must be unique")
    if df[list(REQUIRED - {"date"})].isna().any().any():
        raise ValueError("Missing numerical values")
    if (df["hours"] <= 0).any() or (df["hours"] > 24).any():
        raise ValueError("hours must be between 0 and 24")
    if (df[["forward_gas", "realized_gas", "forward_eua", "realized_eua"]] < 0).any().any():
        raise ValueError("Fuel and EUA prices must be nonnegative")
    df["forecast_css"] = clean_spark_spread(df["forecast_power"], df["forward_gas"], df["forward_eua"], plant)
    df["realized_css"] = clean_spark_spread(df["realized_power"], df["realized_gas"], df["realized_eua"], plant)
    df["dispatch"] = df["forecast_css"] > plant.hurdle_eur_mwh_e
    df["scheduled_mwh"] = np.where(df["dispatch"], df["hours"] * plant.capacity_mw, 0.0)
    df["gross_pnl_eur"] = df["scheduled_mwh"] * df["realized_css"]
    df["cumulative_gross_pnl_eur"] = df["gross_pnl_eur"].cumsum()
    return df


def summarize(df: pd.DataFrame) -> dict:
    days = int(df["dispatch"].sum())
    active = df[df["dispatch"]]
    return {"days_scheduled": days,
            "mwh_generated": float(df["scheduled_mwh"].sum()),
            "gross_pnl_eur": float(df["gross_pnl_eur"].sum()),
            "profitable_dispatch_fraction": float((active["realized_css"] > 0).mean()) if days else 0.0}
