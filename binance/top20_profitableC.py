
'''Filter out the coins that predicted to be the most profitablt coin if the Volatility breakout strategy (k = 0.5)+ Bull market investment strategy was used from 1st Jan 2021 to now'''

import numpy as np
import ccxt
import binance
import time
from datetime import datetime
import pandas as pd
import math

with open("binance_key.txt") as f:    # call the restored api key
    lines = f.readlines()
    key = lines[0].strip()
    secret = lines[1].strip()
    #binance_client = Client(api_key = key, api_secret = secret)
    binance = ccxt.binance({'apiKey': key, 'secret': secret})


def get_hpr(ticker):
    try:
        ohlcvs = binance.fetch_ohlcv(ticker, '1d', binance.parse8601('2021-06-22 00:00:00'))
        df = pd.DataFrame(ohlcvs, columns = ['time', 'open', 'high', 'low', 'close', 'volume'])
        df['time'] = pd.to_datetime(df['time'], unit='ms')
        df = df.set_index('time')
        df['ma5'] = df['close'].rolling(window=5).mean().shift(1)       # window = how many days
        df['range'] = (df['high'] - df['low']) * 0.5                    # k value
        df['target'] = df['open'] + df['range'].shift(1)
        df['bull'] = df['open'] > df['ma5']

        fee = 0.0025
        df['ror'] = np.where((df['high'] > df['target']),
                              df['close'] / df['target'] - fee,
                              1)                # & df['bull']

        df['hpr'] = df['ror'].cumprod()
        df['dd'] = (df['hpr'].cummax() - df['hpr']) / df['hpr'].cummax() * 100

        hpr = float(df['hpr'][-2])
        tidy_hpr = math.floor(hpr*10000)/100
        print(f"Predicted profit of [{ticker}] from [1st Jan 2021] is {tidy_hpr} %")

        return tidy_hpr
    except:
        print(f"== Error : {ticker} does not have historial data ==")
        return 1



markets = binance.load_markets()
tickers = markets.keys()

hprs = []
for ticker in tickers:
    hpr = get_hpr(ticker)
    hprs.append((ticker, hpr))

sorted_hprs = sorted(hprs, key=lambda x:x[1], reverse=True)
print(sorted_hprs[:50])
