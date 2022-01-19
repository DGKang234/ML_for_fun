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


ticker = str.upper(input("what coin would you like to buy? : "))
ticker = ticker + '/USDT'
k = float(input("what is k value? :"))


#df = pd.read_csv('BTCGBP-1d-data.csv')
ohlcvs = binance.fetch_ohlcv(ticker, '1d', binance.parse8601('2021-09-24 00:00:00'))
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
ror = df['ror'].cumprod()
ror = ror.iloc[-2]



df['hpr'] = df['ror'].cumprod()
df['dd'] = (df['hpr'].cummax() - df['hpr']) / df['hpr'].cummax() * 100

print('\n')
print(ticker)
print("MDD (%): ", df['dd'].max())
print("HPR: ", df['hpr'][-2])
print("Yield (%) ", ror*100)
#df.to_excel("larry_ma.xlsx")
