

import ccxt
import pandas as pd
import math
import os.path
from time import sleep
from datetime import datetime, timedelta, time
from binance.client import Client


with open("binance_key.txt") as f:    # call the restored api key
    lines = f.readlines()
    key = lines[0].strip()
    secret = lines[1].strip()
    binance_client = Client(api_key = key, api_secret = secret)
    binance = ccxt.binance({'apiKey': key, 'secret': secret})



def sell_crypto_currency(ticker):

    unit = binance_client.get_asset_balance(asset = coin)['free']
    unit = math.floor(float(unit)*1)/1                                                                           ## Decimal point
    print(f"Attempt to SELL {unit} amount of {ticker}")

    highest_bid_price = binance_client.get_order_book(symbol = ticker)['bids'][0][0]
    #current_market_price = binance_client.get_symbol_ticker(symbol = ticker)["price"]                              # last market price
    sell_market = binance_client.order_limit_sell(symbol = ticker, quantity = unit, price = highest_bid_price)      # executing the trade
    print(sell_market)
    price_sold = sell_market['price']
    print(price_sold)
    print(f"### SELLing '{unit}' of '{ticker}' coin at 'highest bid price : {highest_bid_price} USDT' ###")

coin = str.upper(input('coin name ? : '))

ticker = coin + "USDT"
sell_crypto_currency(ticker)


