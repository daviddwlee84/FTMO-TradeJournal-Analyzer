from typing import Union, Tuple, Dict, List
import numpy as np
import streamlit as st
import pandas as pd
from streamlit.runtime.uploaded_file_manager import UploadedFile


class MetricFormatter:
    """
    TODO: Auto period for large number
    """

    @staticmethod
    def round(number: Union[int, float], decimals: int = 2) -> str:
        return np.round(number, decimals).astype(str)

    @staticmethod
    def percent(number: Union[int, float], decimals: int = 2) -> str:
        return np.round(number * 100, decimals).astype(str) + "%"

    @staticmethod
    def dollar(
        number: Union[int, float], decimals: int = 2, dollar_sign: str = "$"
    ) -> str:
        return (
            ("" if number >= 0 else "-")
            + dollar_sign
            + np.round(abs(number), decimals).astype(str)
        )


def file_uploading_widget() -> Tuple[UploadedFile, pd.DataFrame]:
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
        # https://docs.streamlit.io/library/api-reference/widgets/st.link_button
        st.link_button(
            "Download",
            f"https://trader.ftmo.com/journal/generate_{download_format}/{ftmo_metrix_id}",
        )
        st.link_button(
            "Go to MatriX", f"https://trader.ftmo.com/metrix/{ftmo_metrix_id}"
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
    elif trading_journal_file.name.endswith(
        ".xlsx"
    ) or trading_journal_file.name.endswith(".xls"):
        df = pd.read_excel(trading_journal_file)
    else:
        st.error(f"Invalid file type: {trading_journal_file.name}")
        st.stop()

    datetime_columns = ["Open", "Close"]
    for column in datetime_columns:
        df[column] = pd.to_datetime(df[column])

    return trading_journal_file, df


def flatten_closed_trades_to_orders(df: pd.DataFrame) -> pd.DataFrame:
    """
    FTMO Symbol Commission
    https://ftmo.com/en/symbols/

    https://pandas.pydata.org/docs/user_guide/advanced.html#hierarchical-indexing-multiindex
    """
    open_df = df[["Open", "Type", "Volume", "Symbol", "Price", "Commissions"]]
    open_df.loc[df["Type"] == "sell", "Volume"] *= -1
    # typically charges commissions on closed positions rather than open positions
    open_df["Commissions"] = 0
    open_df.rename(columns={"Open": "Time"}, inplace=True)
    open_df.set_index(["Symbol", "Time"], inplace=True)
    close_df = df[["Close", "Type", "Volume", "Symbol", "Price.1", "Commissions"]]
    close_df.loc[df["Type"] == "buy", "Volume"] *= -1
    close_df.rename(columns={"Close": "Time", "Price.1": "Price"}, inplace=True)
    close_df.set_index(["Symbol", "Time"], inplace=True)
    return pd.concat([open_df, close_df]).sort_index(ascending=True)[
        ["Volume", "Price", "Commissions"]
    ]


def flatten_df_to_close_size_fixed_fees(
    flatten_df: pd.DataFrame,
    symbols: Union[str, List[str], None] = None,
    series_as_df: bool = False,
) -> Dict[str, pd.DataFrame]:
    """
    https://vectorbt.dev/api/portfolio/base/#vectorbt.portfolio.base.Portfolio.from_orders

    ValueError: cannot reindex on an axis with duplicate labels
    https://stackoverflow.com/questions/27236275/what-does-valueerror-cannot-reindex-from-a-duplicate-axis-mean
    """

    def groupby_symbol(series: pd.Series, symbols: List[str]) -> pd.DataFrame:
        close = {}
        for symbol, symbol_series in series.groupby(level="Symbol"):
            if symbols and symbol not in symbols:
                continue
            symbol_series = symbol_series.droplevel(level="Symbol")
            # Remove potential duplicate index
            symbol_series = symbol_series[~symbol_series.index.duplicated()]
            symbol_series.name = symbol
            close[symbol] = symbol_series
        return pd.concat(close.values(), keys=close.keys(), axis=1)

    # https://stackoverflow.com/questions/21081042/detect-whether-a-dataframe-has-a-multiindex
    if not isinstance(flatten_df.index, pd.MultiIndex):
        return dict(
            close=flatten_df["Price"],
            size=flatten_df["Volume"],
            fixed_fees=flatten_df["Commissions"],
        )

    if isinstance(symbols, str):
        if series_as_df:
            return dict(
                close=flatten_df.loc[symbols][["Price"]].rename(
                    columns={"Price": symbols}
                ),
                size=flatten_df.loc[symbols][["Volume"]].rename(
                    columns={"Volume": symbols}
                ),
                fixed_fees=flatten_df.loc[symbols][["Commissions"]].rename(
                    columns={"Commissions": symbols}
                ),
            )
        else:
            return dict(
                close=flatten_df.loc[symbols]["Price"],
                size=flatten_df.loc[symbols]["Volume"],
                fixed_fees=flatten_df.loc[symbols]["Commissions"],
            )

    return dict(
        close=groupby_symbol(flatten_df["Price"], symbols),
        size=groupby_symbol(flatten_df["Volume"], symbols),
        fixed_fees=groupby_symbol(flatten_df["Commissions"], symbols),
    )


if __name__ == "__main__":

    df = pd.read_csv("demo/export-1706151888.csv", sep=";")

    datetime_columns = ["Open", "Close"]
    for column in datetime_columns:
        df[column] = pd.to_datetime(df[column])

    print(flatten_df := flatten_closed_trades_to_orders(df))

    print(orders := flatten_df_to_close_size_fixed_fees(flatten_df))

    import vectorbt as vbt

    pf = vbt.Portfolio.from_orders(**orders)
    # BUG: somehow some size/volume are wrong
    for symbol_pf in pf:
        print(symbol_pf.orders.records_readable)

    print(pf.columns)

    print(btc_orders := flatten_df_to_close_size_fixed_fees(flatten_df, "BTCUSD"))
    btc_pf = vbt.Portfolio.from_orders(**btc_orders)
    print(btc_pf.orders.records_readable)

    print(eth_orders := flatten_df_to_close_size_fixed_fees(flatten_df.loc["ETHUSD"]))
    eth_pf = vbt.Portfolio.from_orders(**eth_orders)
    print(eth_pf.orders.records_readable)

    import ipdb

    ipdb.set_trace()
