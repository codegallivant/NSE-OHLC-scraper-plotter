# NSE-OHLC-chart-plotter
Plots a graph of OHLC values (Open, high, low, close) versus date for an equity/indice registered in the National Stock Exchange of India (NSE).
Requires an internet connection to work.

## :white_check_mark: Completed.

## What is OHLC ?
An OHLC chart is a type of chart that shows open, high, low, and closing prices for each period. OHLC charts are useful since they show the four major data points over a period, with the closing price being considered the most important by many traders. 

## How the program works
It's made using Python. After obtaining input regarding the equity/indice and the date range from the user, the program then scrapes NSE trading data from the internet and goes on to plot the prices against their respective dates. 

## Installing pip libraries
In the terminal,
```
pip install -r requirements.txt
```

## Credits for external libraries and files
- `tkthemes/azure-ttk-theme` (Theme style for tkinter window) - 
  https://github.com/rdbende/Azure-ttk-theme
- `favicon.ico`-
  [Flaticon (afitrose)](https://www.flaticon.com/free-icon/stocks_4946378?related_id=4946378)
