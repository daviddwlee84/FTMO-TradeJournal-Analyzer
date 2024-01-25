# FTMO Trading Journal Analyzer

Analysis portfolio and risk on FTMO trades export from FTMO Trade Journal using Streamlit

## Getting Started

1. Open this tool at [https://ftmo-trading-journal-analyzer.streamlit.app/](https://ftmo-trading-journal-analyzer.streamlit.app/) or run locally using `streamlit run Overview.py`
2. Open [Client Area | FTMO](https://trader.ftmo.com/client-area)
3. Goto one of your account's MatriX like `https://trader.ftmo.com/metrix/xxxxxxxxxx`
4. Scroll down to "Trading Journal" section and export to either csv or excel format
5. Upload file and start analysis

## Todo

- [ ] Single time analysis
- [ ] Able to calculate same statistics like MetriX page
  - [X] Show raw data DataFrame
  - [ ] Balance versus Number of trades
  - [ ] Statistics
  - [ ] Daily Summary
  - [ ] Visualize trades on candlestick charts
- [ ] Additional usage
  - [ ] Option to show TP/SL in percentage
  - [X] Able to filter date
- [ ] Analysis and persistent result (for each strategy)
- [ ] Support general trades format analysis
