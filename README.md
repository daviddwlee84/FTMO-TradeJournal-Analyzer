# FTMO Trading Journal Analyzer

Analysis portfolio and risk on FTMO trades export from FTMO Trade Journal using Streamlit

## Getting Started

1. Open this tool at [https://ftmo-trading-journal-analyzer.streamlit.app/](https://ftmo-trading-journal-analyzer.streamlit.app/) or run locally using `streamlit run Overview.py`
2. Open [Client Area | FTMO](https://trader.ftmo.com/client-area)
3. Goto one of your account's MatriX like `https://trader.ftmo.com/metrix/xxxxxxxxxx`
4. Scroll down to "Trading Journal" section and export to either csv or excel format
5. Upload file and start analysis

## Todo

- [X] Single time analysis
- [ ] Able to calculate same statistics like MetriX page
  - [X] Show raw data DataFrame
  - [X] Balance versus Number of trades
  - [X] Statistics
  - [X] Daily Summary
  - [ ] Visualize trades on candlestick charts
- [ ] Additional usage
  - [ ] Option to show TP/SL in percentage
  - [X] Able to filter date
  - [X] Symbol filter
  - [ ] Timezone shift
- [ ] Analysis and persistent result (for each strategy)
- [ ] Support general trades format analysis
- [ ] Metric & Form number colors
  - [Change metric color, font, background and style - 🎈 Using Streamlit - Streamlit](https://discuss.streamlit.io/t/change-metric-color-font-background-and-style/25309/4)

## Resources

### Portfolio and Metrics

- [ranaroussi/quantstats: Portfolio analytics for quants, written in Python](https://github.com/ranaroussi/quantstats)
- [quantopian/empyrical: Common financial risk and performance metrics. Used by zipline and pyfolio.](https://github.com/quantopian/empyrical)
- [quantopian/pyfolio: Portfolio and risk analytics in Python](https://github.com/quantopian/pyfolio)

### FTMO

- [Points, pips and ticks - FTMO](https://ftmo.com/en/points-pips-and-ticks/)
