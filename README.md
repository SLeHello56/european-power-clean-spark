# European Power Trading & Clean Spark Spread

Python desk-style European power/gas/carbon analytics: clean spark spread, CCGT dispatch economics, implied profitability and illustrative scenarios. It uses reproducible synthetic samples and accepts licensed real market input CSVs.

## Run

```bash
python -m pip install -e '.[dev]'
python -m pytest -q
python examples/run_demo.py
streamlit run app.py
```

Power, gas and EUA forward data may be licensed; no unlicensed exchange histories are included. Research/educational only; simplified fuel, efficiency, emissions and dispatch assumptions. Not investment advice.
