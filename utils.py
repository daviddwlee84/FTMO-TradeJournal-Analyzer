from typing import Union, Tuple
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

    return trading_journal_file, df
