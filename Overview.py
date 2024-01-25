import streamlit as st
import pandas as pd
import datetime
import re

st.set_page_config(page_title="FTMO Trading Journal Analyzer")
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
