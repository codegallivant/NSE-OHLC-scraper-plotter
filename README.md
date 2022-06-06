# NSE-OHLC-Plotter
Plots a graph of OHLC (Open, high, low, close) values versus date for an equity/indice registered in the National Stock Exchange of India (NSE).
Requires an internet connection to work.

## How it works
It's made using Python. After obtaining input regarding the equity/indice and the date range from the user, the program then scrapes NSE trading data from the internet and goes on to plot the prices against their respective dates.

## pip libraries required
- os
- datetime
- pandas
- matplotlib
- mplcursors
- time

