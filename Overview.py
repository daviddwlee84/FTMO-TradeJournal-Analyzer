import streamlit as st
import pandas as pd
import datetime
import re
import os
import quantstats as qs
import plotly.graph_objects as go
import tempfile
import streamlit.components.v1 as components

# extend pandas functionality with metrics, etc.
qs.extend_pandas()

st.set_page_config(page_title="FTMO Trading Journal Analyzer", layout="wide")
st.title("FTMO Trading Journal Analyzer")

trading_journal_file = st.file_uploader(
    "Upload FTMO Trading Journal Exports",
    type=["csv", "xlsx"],
    accept_multiple_files=False,
)

if trading_journal_file is None:
    st.markdown(
        """
1. Open [Client Area | FTMO](https://trader.ftmo.com/client-area)
2. Goto one of your account's MatriX like `https://trader.ftmo.com/metrix/xxxxxxxxxx`
3. Scroll down to "Trading Journal" section and export to either csv or excel format
4. Upload your `export-xxxxxxxxxx.csv` or `export-xxxxxxxxxx.xlsx` here
"""
    )
    st.stop()

if trading_journal_file.name.endswith(".csv"):
    df = pd.read_csv(trading_journal_file, sep=";")
elif trading_journal_file.name.endswith(".xlsx") or trading_journal_file.name.endswith(
    ".xls"
):
    df = pd.read_excel(trading_journal_file)
else:
    st.error(f"Invalid file type: {trading_journal_file.name}")
    st.stop()

# Move this to independent file
datetime_columns = ["Open", "Close"]
for column in datetime_columns:
    df[column] = pd.to_datetime(df[column])

min_date = df["Open"].min().date()
max_date = (df["Open"].max()).date()
date_range = st.date_input(
    "Date Range Selector",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
    help="Both start date and end date are included.",
)

if len(date_range) <= 1:
    st.warning("Please select date range.")
    st.stop()

df = df[
    (pd.to_datetime(date_range[0]) <= df["Open"])
    # https://stackoverflow.com/questions/441147/how-to-subtract-a-day-from-a-date
    & (df["Open"] <= pd.to_datetime(date_range[1] + datetime.timedelta(days=1)))
]

symbols = st.multiselect(
    "Symbol Filter", df["Symbol"].unique(), help="Select none means select all."
)
symbols_select_pattern = "|".join(map(re.escape, symbols))
# https://stackoverflow.com/questions/75834122/search-of-a-set-of-strings-in-a-column-containing-strings-in-a-pandas-dataframe
df = df[df["Symbol"].str.contains(rf"\b(?:{symbols_select_pattern})\b")]

st.dataframe(df)

account_size = st.number_input(
    "Initial Account Size", min_value=0, value=100_000, step=10_000
)

start_date = st.date_input(
    "Start date",
    value=min_date,
)

profit = df.set_index("Close", drop=False).rename_axis("time")["Profit"]
profit.loc[pd.to_datetime(start_date)] = 0
account_prices = profit.sort_index().cumsum() + account_size
net_worth = account_prices / account_size

# NOTE: index should be datetime for quantstats
percent_change_for_qs = qs.utils.to_returns(account_prices)

x_axis_mode = st.selectbox("X-Axis", ["close time", "number of trade"], index=1)
if x_axis_mode == "close time":
    x_axis = account_prices.index
else:
    x_axis = pd.RangeIndex(len(account_prices)) + 1

# TODO: another y-axis for percent of balance change
fig = go.Figure(
    data=[
        go.Scatter(
            x=x_axis,
            y=account_prices,
            mode="lines",
            name="Balance",
        )
    ],
    layout=go.Layout(
        title=go.layout.Title(text="Current Results"),
        xaxis=go.layout.XAxis(title=x_axis_mode.title()),
        yaxis=go.layout.YAxis(title="Balance"),
    ),
)
st.plotly_chart(fig)

curr_dir = os.path.dirname(os.path.abspath(__file__))
fd, name = tempfile.mkstemp(suffix=".html", dir=os.path.join(curr_dir, "temp"))

# TODO: customize output title, etc.
qs.reports.html(percent_change_for_qs, output=name)
with open(name, "r") as fp:
    html = fp.read()
components.html(html, scrolling=True, height=800)
st.download_button(
    "Download Report HTML",
    html,
    file_name=os.path.splitext(trading_journal_file.name)[0] + "_report.html",
)
# PermissionError: [WinError 32] The process cannot access the file because it is being used by another process
os.remove(name)
