import streamlit as st
from utils import file_uploading_widget, flatten_closed_trades_to_orders
import vectorbt as vbt
from vectorbt.portfolio.enums import (
    SizeType,
    Direction,
    NoOrder,
    OrderStatus,
    OrderSide,
)

st.set_page_config(page_title="FTMO Trading Journal Analyzer (VectorBT)", layout="wide")
st.title("FTMO Trading Journal Analyzer (VectorBT)")

trading_journal_file, df = file_uploading_widget()

st.subheader("Data Selection")

# symbol = st.selectbox(
#     "Symbol", df["Symbol"].unique(), help="Select none means select all."
# )
# df = df[df["Symbol"] == symbol]

flatten_df = flatten_closed_trades_to_orders(df)

symbol = st.selectbox(
    "Symbol",
    flatten_df.index.get_level_values("Symbol").unique(),
    help="Select none means select all.",
)
st.subheader("Account Settings")

# TODO: move account prices and net worth as well as balance calculation to the front
account_size = st.number_input(
    "Initial Account Size", min_value=0, value=100_000, step=10_000
)

# Make sell volume to be negative
# df.loc[df['Type'] == 'sell', 'Volume'] *= -1

# st.dataframe(df)

st.dataframe(flatten_df, use_container_width=True)
st.dataframe(flatten_df.loc[symbol], use_container_width=True)

# https://vectorbt.dev/api/portfolio/base/#vectorbt.portfolio.base.Portfolio.from_orders
