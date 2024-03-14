import streamlit as st
from utils import (
    file_uploading_widget,
    flatten_closed_trades_to_orders,
    flatten_df_to_close_size_fixed_fees,
)
import vectorbt as vbt


st.set_page_config(page_title="FTMO Trading Journal Analyzer (VectorBT)", layout="wide")
st.title("FTMO Trading Journal Analyzer (VectorBT)")

trading_journal_file, df = file_uploading_widget()

st.subheader("Data Selection")

flatten_df = flatten_closed_trades_to_orders(df)

symbol = st.selectbox(
    "Symbol",
    flatten_df.index.get_level_values("Symbol").unique(),
    help="Select none means select all.",
)
st.subheader("Account Settings")

account_size = st.number_input(
    "Initial Account Size", min_value=0, value=1_000_000, step=10_000
)

orders = flatten_df_to_close_size_fixed_fees(flatten_df, symbol, series_as_df=False)
# st.json(orders)

with st.spinner("Backtesting..."):
    pf = vbt.Portfolio.from_orders(**orders, init_cash=account_size)


st.subheader("Statistics")

st.dataframe(pf.stats())
# https://vectorbt.dev/api/generic/plotting/
# https://vectorbt.dev/api/portfolio/base/#plots
with st.spinner("Plotting..."):
    st.plotly_chart(
        pf.plot(
            subplots=[
                "orders",
                "trade_pnl",
                "cum_returns",
                "drawdowns",
                "underwater",
                "asset_flow",
                "asset_value",
                "assets",
                "cash",
                "cash_flow",
                "gross_exposure",
                "net_exposure",
                # "position_pnl",
                # "positions",
                "trades",
                "value",
            ]
        )
    )

st.metric("Total Profit", pf.total_profit())
st.metric("Total Return", pf.total_return())
st.metric("Total Benchmark Return", pf.total_benchmark_return())
st.metric("Average Drawdown", pf.drawdowns.avg_drawdown())

st.divider()

st.text("Expected Position")
st.dataframe(df[df['Symbol'] == symbol], use_container_width=True)
# st.dataframe(flatten_df, use_container_width=True)

st.text("Parsed Position")
st.dataframe(pf.positions.records, use_container_width=True)

st.divider()

st.text("Expected Orders")
st.dataframe(flatten_df.loc[symbol], use_container_width=True)

st.text("Parsed Orders")
st.dataframe(pf.orders.records_readable, use_container_width=True)
