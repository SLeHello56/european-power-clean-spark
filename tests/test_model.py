import pandas as pd
import pytest
from power_trading.model import Plant, clean_spark_spread, dispatch_backtest, summarize


def sample():
    return pd.DataFrame({"date": ["2025-01-01", "2025-01-02"],
      "forecast_power": [110., 10.], "forward_gas": [30., 30.], "forward_eua": [50., 50.],
      "realized_power": [90., 500.], "realized_gas": [30., 30.], "realized_eua": [50., 50.],
      "hours": [10, 10]})


def test_css_unit_conversion():
    plant = Plant(efficiency=0.5, emissions_t_per_mwh_th=0.2, variable_om_eur_mwh_e=3)
    assert clean_spark_spread(120, 30, 50, plant) == pytest.approx(37.0)


def test_realized_does_not_affect_dispatch():
    df = sample()
    out = dispatch_backtest(df)
    assert out.dispatch.tolist() == [True, False]
    df.loc[1, "realized_power"] = 10000
    assert dispatch_backtest(df).dispatch.tolist() == [True, False]


def test_pnl_uses_realized_margin_and_volume():
    out = dispatch_backtest(sample(), Plant(capacity_mw=100.0))
    assert out.loc[0, "scheduled_mwh"] == 1000
    assert out.loc[0, "gross_pnl_eur"] == pytest.approx(out.loc[0, "realized_css"] * 1000)
    assert out.loc[1, "gross_pnl_eur"] == 0
    assert summarize(out)["days_scheduled"] == 1


def test_invalid_efficiency():
    with pytest.raises(ValueError):
        Plant(efficiency=0)
