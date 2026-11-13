from power_trading.data import synthetic_power_market
from power_trading.model import dispatch_backtest, summarize

if __name__ == "__main__":
    result = dispatch_backtest(synthetic_power_market())
    print(summarize(result))
    print(result[["date", "forecast_css", "realized_css", "dispatch", "gross_pnl_eur"]].head().to_string(index=False))
