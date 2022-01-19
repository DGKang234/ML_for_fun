import os
import sys
import pandas as pd
import math
import os.path
from time import sleep
from datetime import datetime, timedelta, time
from binance.client import Client
import ccxt

##############
# Parameters #
##############
buy_with = "USDT"
sell_with = "CTXC"
ticker = sell_with + "/" + buy_with
ticker_2 = sell_with + buy_with
k = 0.006



with open("binance_key.txt") as f:    # call the restored api key
    lines = f.readlines()
    key = lines[0].strip()
    secret = lines[1].strip()
    binance_client = Client(api_key = key, api_secret = secret)
    binance = ccxt.binance({'apiKey': key, 'secret': secret})


def buy_crypto_currency(ticker):
    global price_bought
    gbp = binance_client.get_asset_balance(asset = buy_with)["free"]                          # account balance
    #current_market_price = binance_client.get_symbol_ticker(symbol = ticker)["price"]      # last market price
    lowest_ask_price = binance_client.get_order_book(symbol = ticker)["asks"][0][0]         # lowest asking price
    unit = float(gbp)/float(lowest_ask_price)                                               # calculate how many coins I can get with the balance
    unit = math.floor(unit*100)/100                                                         ## Decimal point
    print(f"Attempt to BUY {unit} amount of {ticker}")
    buy_market = binance_client.order_limit_buy(symbol = ticker, quantity = unit, price = lowest_ask_price)      # executing the trade
    print(buy_market)
    price_bought = float(buy_market['price'])
    print(price_bought)
    print(f"### BUYing '{unit}' of '{ticker}' coin at '{lowest_ask_price} USDT' ### ")
    return price_bought


def sell_crypto_currency(ticker):
    unit = binance_client.get_asset_balance(asset = sell_with)['free']
    unit = math.floor(float(unit)*100)/100                                                                          ## Decimal point
    print(f"Attempt to SELL {unit} amount of {ticker}")

    highest_bid_price = binance_client.get_order_book(symbol = ticker)['bids'][0][0]
    #current_market_price = binance_client.get_symbol_ticker(symbol = ticker)["price"]                              # last market price
    sell_market = binance_client.order_limit_sell(symbol = ticker, quantity = unit, price = highest_bid_price)      # executing the trade
    print(sell_market)
    price_sold = sell_market['price']
    print(price_sold)
    print(f"### SELLing '{unit}' of '{ticker}' coin at 'highest bid price : {highest_bid_price} USDT' ###")


def get_yesterday_price(ticker):
    global yesterday_close, yesterday_high, yesterday_low
    ohlcvs = binance.fetch_ohlcv(ticker, '1d', binance.parse8601('2021-01-01 00:00:00'))
    df = pd.DataFrame(ohlcvs, columns = ['time', 'open', 'high', 'low', 'close', 'volume'])
    df['time'] = pd.to_datetime(df['time'], unit='ms')
    df = df.set_index('time')
    yesterday = df.iloc[-2]
    yesterday_close = float(yesterday['close'])
    yesterday_high = float(yesterday['high'])
    yesterday_low = float(yesterday['low'])
    return yesterday_close, yesterday_high, yesterday_low


def get_current_price(ticker):
    global current, current_open
    ohlcvs = binance.fetch_ohlcv(ticker, '1d', binance.parse8601('2021-01-01 00:00:00'))
    df = pd.DataFrame(ohlcvs, columns = ['time', 'open', 'high', 'low', 'close', 'volume'])
    df['time'] = pd.to_datetime(df['time'], unit='ms')
    df = df.set_index('time')
    current = float(df.iloc[-1]['close'])
    current_open = float(df.iloc[-1]['open'])
    return current, current_open


def get_target_price(ticker, k):
    global target
    get_yesterday_price(ticker)
    get_current_price(ticker)
    target = current_open + (yesterday_high - yesterday_low)*k
    return target


def get_yesterday_ma5(ticker, kline_size='1d'):
    global ma5
    ohlcvs = binance.fetch_ohlcv(ticker, '1d', binance.parse8601('2021-01-01 00:00:00'))
    df = pd.DataFrame(ohlcvs, columns = ['time', 'open', 'high', 'low', 'close', 'volume'])
    df['time'] = pd.to_datetime(df['time'], unit='ms')
    df = df.set_index('time')
    close = df['close']
    ma5 = close.rolling(window=5).mean()
    ma5 = ma5.iloc[-2]
    return ma5








now = datetime.now()
mid = datetime(now.year, now.month, now.day) + timedelta(days = 1)
while True:
    try:

        now = datetime.now()

        get_yesterday_ma5(ticker)
        get_yesterday_price(ticker)
        get_current_price(ticker)
        get_target_price(ticker, k)

        print('\n')
        print("Block : A")
        print(now)
        print(mid)
        print(f'           [MA5] price is : {ma5}')
        print(f'        [target] price is : {target}')
        print(f'The lowest [ask] price is : {current}')
        print(f'automatically all {ticker} will be sold at {mid}')




        if mid < now < mid + timedelta(seconds = 10):
            mid = datetime(now.year, now.month, now.day) + timedelta(days = 1)      # Selling point (sell at 5 pm)
            sell_crypto_currency(ticker_2)                                          # SELL



        if (current > target) and (current > ma5):
            try:
                buy_crypto_currency(ticker_2)                                       # BUY
            except:
                print("=========================================================================================")
                print("== Error from : Already bought the coin with all available balance or Invalid quantity ==")
                print("=========================================================================================")
                #os.exit()



            while now < mid:
                try:
                    get_current_price(ticker)
                    now = datetime.now()

                    print('\n')
                    print(now)
                    print(f'           [MA5] price is : {ma5}')
                    print(f'        [target] price is : {target}')
                    print(f'The lowest [ask] price is : {current}')
                    print(f'All of {ticker} will be sold at {mid} automatically')

                    profit = round((current/price_bought-0.0032)*100, 2)
                    print(f"Current profit is : {profit} %")

                    if profit <= 95:     #(current <= price_bought*0.95):  #<= target*0.94) and (current <= ma5*0.94):
                        sell_crypto_currency(ticker_2)
                        print("### Losing 6 % profit - Closing the position ###")
                        print("Turning off the automation trading system -- OFF")
                    print("Block : B")



                    if profit >= 130:                      #(current >= target*1.3) and (current >= target*1.3):
                        sell_crypto_currency(ticker_2)
                        print("### Gaining 30 % profit - Closing the position ###")
                        print("Turning off the automation trading system -- OFF")
                    print("Block : C")



                except:
                    print("====================================")
                    print("== Error from : Block [A], or [B] ==")
                    print("====================================")
                    raise
                sleep(1)


    except:
        print("===============================================")
        print("== Error from : Selling process at mid night ==")
        print("===============================================")
        sys.exit()
    sleep(1)
