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

with st.expander("Trading Journal Downloader"):
    st.caption("Make sure you have logged in your FTMO account.")
    ftmo_metrix_id = st.text_input("MetriX ID", "2100893235")
    download_format = st.selectbox(
        "Download Format",
        ["csv", "xlsx"],
        format_func=lambda x: "CSV" if x == "csv" else "Excel",
    )
    # NOTE: since FTMO require login, we cannot use HTTP GET
    st.link_button(
        "Download",
        f"https://trader.ftmo.com/journal/generate_{download_format}/{ftmo_metrix_id}",
    )
    st.link_button("Go to MatriX", f"https://trader.ftmo.com/metrix/{ftmo_metrix_id}")

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

date_order = st.selectbox(
    "Date Order",
    ["Ascending", "Descending"],
    index=1,
    format_func=lambda x: "Ascending (Oldest First)"
    if x == "Ascending"
    else "Descending (Recent First)",
)

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

df["Net Profit"] = df["Profit"] + df["Commissions"]

st.header("Detail Trades")
st.dataframe(df.sort_values("Open", ascending=(date_order == "Ascending")))

close_time_df = df.set_index("Close", drop=False).rename_axis("time")

# Daily Summary
# https://stackoverflow.com/questions/39400115/python-pandas-group-by-date-using-datetime-data
daily_df = close_time_df.groupby(pd.Grouper(freq="D")).agg(
    {
        "Ticket": "count",
        "Volume": "sum",
        "Profit": "sum",
        "Commissions": "sum",
        "Net Profit": "sum",
    }
)
daily_df.rename_axis("Date", inplace=True)
daily_df.rename(columns={"Ticket": "Trades", "Volume": "Lots"}, inplace=True)
daily_df_new = daily_df.copy().sort_index(ascending=(date_order == "Ascending"))
# https://discuss.streamlit.io/t/date-display-with-pandas/38351
daily_df_new.index = daily_df_new.index.map(lambda x: x.strftime("%d %b %Y"))

st.header("Daily Summary")
st.dataframe(daily_df_new)

# TODO: Consistency Score = (1 – (absolute value of the most profitable or losing day / absolute result of all trading days)) x 100%.

st.header("Portfolio Statistics")
account_size = st.number_input(
    "Initial Account Size", min_value=0, value=100_000, step=10_000
)

start_date = st.date_input(
    "Start date",
    value=min_date,
    max_value=min_date,
    help="Account creation date. Default the first trade date. (Basically used for drawing.)",
)

net_profit = close_time_df["Net Profit"]
net_profit.loc[pd.to_datetime(start_date)] = 0
account_prices = net_profit.sort_index().cumsum() + account_size
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
# NOTE: use mkstemp will have permission issue: PermissionError: [WinError 32] The process cannot access the file because it is being used by another process
temp_file_name = tempfile.mktemp(suffix=".html", dir=os.path.join(curr_dir, "temp"))

report_download = st.empty()
with st.spinner("Generating Detail Report..."):
    # TODO: customize output title, etc.
    qs.reports.html(percent_change_for_qs, output=temp_file_name)
    with open(temp_file_name, "r") as fp:
        html = fp.read()
    components.html(html, scrolling=True, height=800)
report_download.download_button(
    "Download Report HTML",
    html,
    file_name=os.path.splitext(trading_journal_file.name)[0] + "_report.html",
)

os.remove(temp_file_name)
