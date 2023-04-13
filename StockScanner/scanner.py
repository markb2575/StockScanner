# Things to scan for:
#     High Relative Volume
#     Low Float
#     Low Price

import time
import requests
from bs4 import BeautifulSoup
import yfinance as yf
import pandas as pd, timeit
import ray
import statistics
from tickers import getTickers

def getRating():
    tickers = getTickers()
    print(tickers)
    # tickers=["AEL", "AEM", "AEMD", "AENZ", "AEO", "AEP"]


    # today = str(datetime.date.today())
    #today = "2023-03-17"
    
    # tracking relative volume, volatility, low price,
    # ray.init(ignore_reinit_error=True) #pre-intialize
    # @ray.remote
    # def get_data_ray2(symbol):
    #     print(symbol)
    #     time.sleep(0.001)
    #     try:
    #         data = yf.download(symbol, period="1mo", interval="15m", progress=False)
    #         fiveDay = []
    #         for i in range(-1,-131,-1):
    #             fiveDay.append(data["Close"][i])
    #         stdev = statistics.stdev(fiveDay)
    #         print(stdev)
    #         price = data["Close"][-1]
    #         currentVolume = data["Volume"][-1]
    #         averageVolume = data.sort_values(by=["Volume"])["Volume"].median()
    #         if (averageVolume == 0):
    #             return (symbol, 0, 0)
    #         relativeVolume = round(((currentVolume - averageVolume)/abs(averageVolume)) * 100, 2)
    #         if (relativeVolume == float('inf') or currentVolume < 1000000 or price > 100):
    #             return (symbol, 0, 0)
    #         return (symbol, relativeVolume, stdev)
    #     except:
    #         # print(f"could not download {symbol}")
    #         return (symbol, 0, 0)

    @ray.remote
    def get_data_ray(symbol):
        print(symbol)
        time.sleep(0.001)
        try:
            data = yf.download(symbol, period="5d", interval="5m", progress=False)
            # fiveDay = []
            # weekly = 0
            # high = 0
            # low = 999999999999
            # for i in range(-1,-len(data["Close"]),-1):
            #     if (weekly == 5):
            #         fiveDay.append(int((abs(high - low) * 100) / low))
            #         high = 0
            #         low = 999999999999
            #         weekly = 0
            #     if (data["High"][i] > high):
            #         high = data["High"][i]
            #     if (data["Low"][i] < low):
            #         low = data["Low"][i]
            #     weekly+=1

            stdev = statistics.stdev(data["Close"])

            price = data["Close"][-1]
            currentVolume = (data["Volume"][-1])
            averageVolume = data.sort_values(by=["Volume"])["Volume"].median()

            relativeVolume = round(((currentVolume - averageVolume)/abs(averageVolume)) * 100, 2)

            # print(f'stdev:{stdev} averageVolume:{averageVolume} relativeVolume{relativeVolume} currentVolume:{currentVolume} price:{price} symbol:{symbol}')
            if (averageVolume < 100000 or price > 10):
                return (symbol, 0, 0)
            return (symbol, relativeVolume, stdev)
        except:
            # print(f"could not download {symbol}")
            return (symbol, 0, 0)

    @ray.remote
    def getFloat(ticker):
        try:
            url = f'https://finance.yahoo.com/quote/{ticker}/key-statistics'
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'}
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, 'lxml')
            for line in soup.find_all("span", text="Float" ):
                float = line.find_parent().find_next_sibling().get_text()
            if (float == "N/A"):
                for line in soup.find_all("span", text="Shares Outstanding" ):
                    float = line.find_parent().find_next_sibling().get_text()
            if (float == "N/A"):
                return "0M"
            return float
        except:
            return "0M"

    start_time = timeit.default_timer()
    result_ids = [get_data_ray.remote(s) for s in tickers]
    columns=['Ticker','Relative-Volume', 'Stdev']
    csv = pd.DataFrame(ray.get(result_ids), columns=columns);
    csv['Relative-Volume'] = (csv['Relative-Volume'] - csv['Relative-Volume'].min()) / (csv['Relative-Volume'].max() - csv['Relative-Volume'].min())
    csv['Stdev'] = (csv['Stdev'] - csv['Stdev'].min()) / (csv['Stdev'].max() - csv['Stdev'].min())
    rating = []
    for i in range(0,len(csv.index)):
        rating.append((csv["Stdev"][i] + csv["Relative-Volume"][i])/2)
    csv["Rating"] = rating
    csv.sort_values(["Rating"],axis=0,ascending=[False],inplace=True)
    csv.drop('Relative-Volume', axis=1, inplace=True)
    csv.drop('Stdev', axis=1, inplace=True)
    csv = csv[:500]
    tickers = csv["Ticker"].to_list()
    print(tickers)
    result_ids = [getFloat.remote(s) for s in tickers]
    floatStr = ray.get(result_ids)
    shares = []
    for string in floatStr:
        if (string[-1] == "M"):
            shares.append(float(string[:-1]) * 1000000)
        elif (string[-1] == "k"):
            shares.append(float(string[:-1]) * 1000)
        elif (string[-1] == "B"):
            shares.append(float(string[:-1]) * 1000000000)
    csv["Shares"] = shares
    csv['Shares'] = (((csv['Shares'] - csv['Shares'].min()) / (csv['Shares'].max() - csv['Shares'].min()))*-1)+1
    rating = []
    csv.reset_index(inplace=True)
    for i in range(0,len(csv.index)):
        rating.append(csv['Rating'][i] + (csv["Shares"][i] - csv['Rating'][i])/3)
    csv["Rating"] = rating
    csv.drop('Shares', axis=1, inplace=True)
    csv.drop('index', axis=1, inplace=True)
    csv.sort_values(["Rating"],axis=0,ascending=[False],inplace=True)
    csv.reset_index(inplace=True)
    print(f'Completed in: {timeit.default_timer() - start_time} seconds.')
    return csv
    # 
    # 