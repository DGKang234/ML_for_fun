import os
import sys
import pandas as pd
import math
import numpy as np
from time import sleep
from datetime import datetime, timedelta, time
import traceback
from binance.client import Client
import ccxt

##############
# Parameters #
##############
buy_with = "USDT"
sell_with = "DOGE"
ticker = sell_with + "/" + buy_with
ticker_2 = sell_with + buy_with

#decimal = input("what is the maximum decimal point of unit of the coin you can buy? : ")
dec_point = {"0":1, "1":10, "2":100, "3":1000, "4":10000, "5":100000, "6":1000000, "7":10000000, "8":100000000}
decimal_point = int(dec_point["0"])
#decimal_point = 1

fee = 0.0025
bumper = 10

with open("binance_key.txt") as f:    # call the restored api key
    lines = f.readlines()
    key = lines[0].strip()
    secret = lines[1].strip()
    binance_client = Client(api_key = key, api_secret = secret)
    binance = ccxt.binance({'apiKey': key, 'secret': secret})


def buy_crypto_currency(ticker):
    global price_bought, current_market_price, unit_
    current_market_price = binance_client.get_symbol_ticker(symbol = ticker)["price"]
    usdt = binance_client.get_asset_balance(asset = buy_with)["free"]
    #lowest_ask_price = binance_client.get_order_book(symbol = ticker)["asks"][0][0]
    unit_ = float(usdt)/float(current_market_price)
    unit_ = math.floor(unit_*decimal_point)/decimal_point
    print(f"Attempt to BUY {unit_} amount of {ticker}")
    #buy_market = binance_client.order_limit_buy(symbol = ticker, quantity = unit_, price = lowest_ask_price)
    buy_market = binance_client.order_market_buy(symbol=ticker, quantity = unit_)
    print(buy_market)
    most_recent_order = binance_client.get_my_trades(symbol=ticker_2, limit=1)[0]
    price_bought = float(most_recent_order["price"])
    print(price_bought)
    print(f"### BUYing '{unit_}' of '{ticker}' coin at '{current_market_price} USDT' ### ")
    return price_bought, current_market_price, unit_


def sell_crypto_currency(ticker):
    global unit_
    unit_ = binance_client.get_asset_balance(asset = sell_with)['free']
    unit_ = math.floor(float(unit_)*decimal_point)/decimal_point
    print(f"Attempt to SELL {unit_} amount of {ticker}")
    #highest_bid_price = binance_client.get_order_book(symbol = ticker)['bids'][0][0]
    #current_market_price = binance_client.get_symbol_ticker(symbol = ticker)["price"]
    #sell_market = binance_client.order_limit_sell(symbol = ticker, quantity = unit_, price = highest_bid_price)
    sell_market = binance_client.order_market_sell(symbol=ticker, quantity = unit_)
    print(sell_market)

    most_recent_order = binance_client.get_my_trades(symbol=ticker_2, limit=1)[0]
    price_sold = float(most_recent_order["price"])
    print(price_sold)
    print(f"### SELLing '{unit_}' of '{ticker}' coin at 'market  price : {price_sold} USDT' ###")
    return unit_


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
    ohlcvs = binance.fetch_ohlcv(ticker, '1d', binance.parse8601('2021-04-01 00:00:00'))
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
    print(current_open, yesterday_high, yesterday_low)
    target = math.floor(target*10000000)/10000000
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
    ma5 = math.floor(ma5*10000000)/10000000
    return ma5


def fitting_k_value(ticker, k):
    global max_k
    ohlcvs = binance.fetch_ohlcv(ticker, '1d', binance.parse8601('2021-04-05 00:00:00'))
    df = pd.DataFrame(ohlcvs, columns = ['time', 'open', 'high', 'low', 'close', 'volume'])
    df['time'] = pd.to_datetime(df['time'], unit='ms')
    df = df.set_index('time')
    df['range'] = (df['high'] - df['low']) * k
    df['target'] = df['open'] + df['range'].shift(1)
    fee = 0.0025
    df['ror'] = np.where(df['high'] > df['target'],
                         df['close'] / df['target'] - fee,
                         1)
    #df.to_excel('BTCFBP_ror.xlsx')
    ror = df['ror'].cumprod()
    ror = ror.iloc[-2]
    return ror


'''
print("ror     k")
k_list = []
for k in np.arange(0.001, 1.0, 0.001):
    k2_list = []
    ror = fitting_k_value(ticker, k)
    print("%.5f %.3f" % (ror, k))
    k2_list.append(ror)
    k2_list.append(k)
    k_list.append(k2_list)
    k = int(max(k_list)[1])
print(max(k_list))
k = max(k_list)[1]
print(f"the best 'k' value is {k}")
'''

k = 0.124
get_target_price(ticker, k)

list_profit = []
now = datetime.now()
mid = datetime(now.year, now.month, now.day) + timedelta(days = 1, hours = 1)


while True:
    try:
        now = datetime.now()
        get_yesterday_ma5(ticker)
        get_yesterday_price(ticker)
        get_current_price(ticker)
        most_recent_order = binance_client.get_my_trades(symbol=ticker_2, limit=1)[0]
        price_bought = float(most_recent_order["price"])
        profit = round((current/price_bought - 0.003) * 100, 2)

        print('\n')
        print(now)
        print(f'   The [k] value : {k}')
        print(f'           [MA5] : {ma5}')
        print(f'        [target] : {target}')
        print(f'The lowest [ask] : {current}')
        print(f"If you manually bought the coin recently the current profit is [{profit}] %")
        print(f'All of {ticker} will be sold automatically at {mid}')



        '''Midnight process (selling, fitting k)'''
        if mid < now < mid + timedelta(seconds = 10):
            try:
                mid = datetime(now.year, now.month, now.day) + timedelta(days = 1, hours = 1)
                sell_crypto_currency(ticker_2)
            except:
                print("=========================================")
                print("==  You didn't buy the coin yesterday  ==")
                print("=========================================")


            try:
                print("ror     k")
                k_list = []
                for k in np.arange(0.001, 1.0, 0.001):
                    k2_list = []
                    ror = fitting_k_value(ticker, k)
                    print("%.5f %.3f" % (ror, k))
                    k2_list.append(ror)
                    k2_list.append(k)
                    k_list.append(k2_list)
                print(max(k_list))
                k = max(k_list)[1]
                print(f"the best 'k' value is {k}")

                get_target_price(ticker, k)
            except:
                print("===================================")
                print("== Fitting k value gave an error ==")
                print("===================================")



        '''Buying process'''
        if (current > target):
            try:
                buy_crypto_currency(ticker_2)
            except:
                print("=========================================================================================")
                print("==   You may already bought the coin with all available balance or Invalid quantity   ==")
                print("=========================================================================================")



        '''Takking profit when profit >= 130'''
        if profit >= 101:
            sell_crypto_currency(ticker_2)
            print("====================================================")
            print("==== Gaining 30 % profit - Closing the position ====")
            print("= Turning off the automation trading system -- OFF =")
            print("====================================================")
            sys.exit()



        '''If current profit is {bumper} % less than max profit sell the coin '''
        list_profit.append(profit)
        list_profit.sort(reverse = True)
        list_profit = list_profit[:5]
        max_profit = max(list_profit)
        print(f'All of {ticker} will be sold if {profit} is less than -5 % point {max_profit}')
        diff = math.floor((max_profit - profit)*100)/100
        print(f'Current difference : {diff}')
        if profit <= max_profit - bumper:
            sell_crypto_currency(ticker_2)
            print("===================================================================")
            print("=== Gained {profit} which is -5 % from max profit (max_profit) ===")
            print("====     Turning off the automation trading system -- OFF     ====")
            print("===================================================================")
            sys.exit()



    except Exception as exception:
        traceback.print_exc()
        os.system("python /Users/tonggihkang/Desktop/personal_project/binance/binance_error_email.py")
        print("===============================================")
        print("== Error from : Selling process at mid night ==")
        print("===============================================")
        sys.exit()
    sleep(1)






