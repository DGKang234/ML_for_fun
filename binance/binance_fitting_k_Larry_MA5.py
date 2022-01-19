import ccxt
import pandas as pd
import math
import os.path
import time
from datetime import datetime, timedelta
from binance.client import Client
import numpy as np


with open("binance_key.txt") as f:    # call the restored api key
    lines = f.readlines()
    key = lines[0].strip()
    secret = lines[1].strip()
    #binance_client = Client(api_key = key, api_secret = secret)
    binance = ccxt.binance({'apiKey': key, 'secret': secret})




ticker = 'BTCST/USDT'




def get_ror(k=0.5):
    ohlcvs = binance.fetch_ohlcv(ticker, '1d', binance.parse8601('2021-04-01 00:00:00'))
    df = pd.DataFrame(ohlcvs, columns = ['time', 'open', 'high', 'low', 'close', 'volume'])
    df['time'] = pd.to_datetime(df['time'], unit='ms')
    df = df.set_index('time')

    df['ma5'] = df['close'].rolling(window=5).mean().shift(1)
    df['range'] = (df['high'] - df['low']) * k
    df['target'] = df['open'] + df['range'].shift(1)
    df['bull'] = df['open'] > df['ma5']
    fee = 0.0032
    df['ror'] = np.where((df['high'] > df['target']) & df['bull'],
                      df['close'] / df['target'] - fee,
                      1)

    #df.to_excel('BTCFBP_ror.xlsx')
    ror = df['ror'].cumprod()             # cumprod -> cumulative product -> best gaining
    ror = ror.iloc[-2]
    return ror



print("ror     k")
k_list = []
for k in np.arange(0.001, 1.0, 0.001):
    k2_list = []
    ror = get_ror(k)
    print("%.5f %.3f" % (ror, k))

    k2_list.append(ror)
    k2_list.append(k)

    k_list.append(k2_list)

print(max(k_list))
print(f"the best 'k' value is {max(k_list)[1]}")
