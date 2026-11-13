import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from power_trading.data import synthetic_power_market
from power_trading.model import Plant, dispatch_backtest, summarize

st.set_page_config(page_title="Clean Spark Spread", page_icon="⚡", layout="wide")
st.title("European Power Trading & Clean Spark Spread")
st.caption("Illustrative day-ahead dispatch research · synthetic input data by default · not live trading")
st.info("A scheduling signal uses forecast prices only. Realized prices are used solely to score the decision afterwards.")
with st.sidebar:
    st.header("CCGT plant assumptions")
    eff = st.slider("Thermal efficiency (%)", 35, 65, 55)
    emissions = st.number_input("Emissions (tCO₂/MWh thermal)", 0.0, 1.0, 0.202, step=0.001, format="%.3f")
    vom = st.number_input("Variable O&M (€/MWh electric)", 0.0, 50.0, 3.0)
    capacity = st.number_input("Capacity (MW)", 1, 2000, 250)
    hurdle = st.slider("Dispatch hurdle (€/MWh electric)", -10, 30, 0)
plant = Plant(eff / 100, emissions, vom, capacity, hurdle)
upload = st.file_uploader("Upload custom market file (see README for CSV schema)", type="csv")
input_data = pd.read_csv(upload) if upload is not None else synthetic_power_market()
try:
    out = dispatch_backtest(input_data, plant)
    metrics = summarize(out)
    a, b, c, d = st.columns(4)
    a.metric("Scheduled days", metrics["days_scheduled"])
    b.metric("Generation (MWh)", f'{metrics["mwh_generated"]:,.0f}')
    c.metric("Gross contribution (€)", f'{metrics["gross_pnl_eur"]:,.0f}')
    d.metric("Positive-margin scheduled days", f'{metrics["profitable_dispatch_fraction"]:.1%}')
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=out["date"], y=out["forecast_css"], name="Forecast CSS", mode="lines"))
    fig.add_trace(go.Scatter(x=out["date"], y=out["realized_css"], name="Realized CSS", mode="lines", opacity=0.7))
    fig.add_hline(y=hurdle, line_dash="dash", annotation_text="Decision hurdle")
    fig.update_layout(title="Clean spark spread (€/MWh electric)", yaxis_title="€/MWh electric")
    st.plotly_chart(fig, use_container_width=True)
    st.line_chart(out.set_index("date")["cumulative_gross_pnl_eur"], y_label="EUR")
    st.dataframe(out, hide_index=True, use_container_width=True)
    st.download_button("Download dispatch results", out.to_csv(index=False), "power_dispatch.csv", "text/csv")
except (KeyError, ValueError, TypeError) as exc:
    st.error(f"Input error: {exc}")
st.caption("Excludes availability constraints, ramping, start-up, balancing, capacity payments, transmission and financing costs.")
