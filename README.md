# StockScanner
A Stock Scanning tool that searches for stocks with the following criteria:
- Price Under $5
- Highly Volatile
- High Relative Volume
- Low Float

There is a method that loads Tickers into the program. These tickers can be updated how ever you wish in the tickers.py file.

To make the program run faster these tickers can be updated to only contain filtered tickers. For example, instead of filtering the price with the scanner.py file, the price could be filtered manually prior to running so that the tickers list is shorter.

This program makes use of Ray to process the tickers faster than using the default python multithreading.

The criteria is finally averaged into a "rating" which indicates the stock with the "best" criteria. It is then displaying in a GUI made with tkinter.

Feel free to make any changes to better suit your needs.

# Note:
- **This tool should not be fully trusted and used with caution. It does not indicate stocks you should buy, it is just a tool that may make it easier deciding.**
- **Additionally, there are many tools availiable online for free that offer more reliable data such as finviz.**
- **This repository was mainly a project to learn more about stocks and increase my software and programming abilities.**

# Required Modules:
- time
- requests
- beautifulsoup
- yfinance
- pandas
- ray
- statistics
- tkinter
- threading
