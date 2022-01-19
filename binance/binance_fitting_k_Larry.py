import ccxt
import pandas as pd
import math
import os.path
import time
from datetime import datetime, timedelta
from binance.client import Client
import numpy as np


binance = ccxt.binance({
    'apiKey': 'DciiuE72NLhLb4gGqXdZBrFJinKrAucg9SgIEM4rW1XqSW5me7N8nm4M6Nv3TRmP',
    'secret': 'MJkWmqeSmOPI6CXWFPReMM6uhX8ng3KhvNoAYQoZmsiVbitZmJSJPZWfV4T186Cg',
})

ticker = str.upper(input("which k value of the coin would you like to fit? : "))
money = str.upper(input("which coin are you going to use to buy the coin?"))

ticker = ticker + '/' + money



def get_ror(k=0.5):
    ohlcvs = binance.fetch_ohlcv(ticker, '1d', binance.parse8601('2021-04-01 00:00:00'))
    df = pd.DataFrame(ohlcvs, columns = ['time', 'open', 'high', 'low', 'close', 'volume'])
    df['time'] = pd.to_datetime(df['time'], unit='ms')
    df = df.set_index('time')
    df['range'] = (df['high'] - df['low']) * k         # df['range'] -> (yesterday high - yesterday low)*0.5
    df['target'] = df['open'] + df['range'].shift(1)   # x.shift(1) -> shift whole column 1 down

    fee = 0.0032
    df['ror'] = np.where(df['high'] > df['target'],          # numpy.where(condition[, x=when condition is True, y=when condition False])
                         df['close'] / df['target'] - fee,   # condition is when df[high]>df[target]
                         1)                                  # False -> didn't buy
    #df.to_excel('BTCFBP_ror.xlsx')
    ror = df['ror'].cumprod()         # cumprod -> cumulative product
    ror = ror.iloc[-2]
    return ror                            # 96 ->no of days from 1/jan/2021 to 8/Mar/2021


print("ror     k")
k_list = []
for k in np.arange(0.01, 1.0, 0.001):
    k2_list = []
    ror = get_ror(k)
    print("%.5f %.3f" % (ror, k))

    k2_list.append(ror)
    k2_list.append(k)

    k_list.append(k2_list)

print(max(k_list))
print(f"the best k value is {max(k_list)[1]}")
