import os
import sys
import pandas as pd
import math
import numpy as np
import os.path
from time import sleep
from datetime import datetime, timedelta, time
import traceback
from binance.client import Client
import ccxt

with open("binance_key.txt") as f:    # call the restored api key
    lines = f.readlines()
    key = lines[0].strip()
    secret = lines[1].strip()
    binance_client = Client(api_key = key, api_secret = secret)
    binance = ccxt.binance({'apiKey': key, 'secret': secret})


dec_point = {"9":1000000000, "8":100000000, "7":10000000, "6":1000000, "5":100000, "4":10000, "3":1000, "2":100, "1":10, "0":1}

fee = 0.0025
bumper = 5
print(f" ==  This code will execute at midnight to calculate which one is profitable tomorrow and buy them immediately at market price - Dong gi == ")




def buy_crypto_currency(ticker, buy_with):
    global current_market_price, unit_
    current_market_price = binance_client.get_symbol_ticker(symbol = ticker)["price"]
    #usdt = binance_client.get_asset_balance(asset = buy_with)["free"]
    #lowest_ask_price = binance_client.get_order_book(symbol = ticker)["asks"][0][0]
    for d in dec_point:
        try:
            decimal_point = dec_point[str(d)]
            unit_ = float(usdt)/float(current_market_price)
            unit_ = math.floor(unit_*decimal_point)/decimal_point
            #buy_market = binance_client.order_limit_buy(symbol = ticker, quantity = unit_, price = lowest_ask_price)
            buy_market = binance_client.order_market_buy(symbol=ticker, quantity = unit_)
            #buy_market = binance_client.create_test_order(symbol=ticker, side='BUY', type='MARKET', quantity=unit_)
            print(buy_market)
            #most_recent_order = binance_client.get_my_trades(symbol=ticker, limit=1)[0]
            #price_bought = float(most_recent_order["price"])
        except: #Exception as exception:
            #traceback.print_exc()
            print("Trying to find the max decimal point of the unit to buy")
            continue
        else:
            print(f"=== Attempt to BUY {unit_} amount of {ticker} ===")
            break
    return current_market_price, unit_

def sell_crypto_currency(ticker, sell_with):
    global unit_
    for d in dec_point:
        try:
            decimal_point = dec_point[str(d)]
            unit_ = binance_client.get_asset_balance(asset = sell_with)['free']
            unit_ = math.floor(float(unit_)*decimal_point)/decimal_point
            #highest_bid_price = binance_client.get_order_book(symbol = ticker)['bids'][0][0]
            #current_market_price = binance_client.get_symbol_ticker(symbol = ticker)["price"]
            #sell_market = binance_client.order_limit_sell(symbol = ticker, quantity = unit_, price = highest_bid_price)
            sell_market = binance_client.order_market_sell(symbol=ticker, quantity = unit_)
            #sell_market = binance_client.create_test_order(symbol=ticker, side='BUY', type='MARKET', quantity=unit_)
            print(sell_market)

            #most_recent_order = binance_client.get_my_trades(symbol=ticker_2, limit=1)[0]
            #price_sold = float(most_recent_order["price"])
            #print(price_sold)
        except: #Exception as exception:
            #traceback.print_exc()
            print("Trying to find the max decimal point of the unit to buy")
            continue
        else:
            print(f"=== SELLing '{unit_}' amount of '{ticker}' coin ===")
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


def get_hpr(ticker):
    try:
        twentyone_days_ago = datetime(now.year, now.month, now.day) - timedelta(days = 21)
        ohlcvs = binance.fetch_ohlcv(ticker, '1d', binance.parse8601(twentyone_days_ago), 21)
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


def buying_n_coins():
    #USDT = USDT[:n_coin]
    global usdt
    for coin in USDT:
        #usdt = binance_client.get_asset_balance(asset = "USDT")["free"]
        #print(usdt)
        #usdt = float(usdt)/n_coin
        #print(usdt)
        print(f'{coin} ---> Buying now')
        coin = coin.replace('/', '')
        buy_crypto_currency(coin, "USDT")
        print("========")
        print("= DONE =")
        print("========\n\n\n")
    return usdt

################################################################################################################################################
################################################################################################################################################

now = datetime.now()
mid = datetime(now.year, now.month, now.day) + timedelta(days = 1, hours = 1)
print(mid)
while True:
    now = datetime.now()
    print(now.strftime("%x %X"))

    if mid < now < mid + timedelta(seconds = 10):
        markets = binance.load_markets()
        tickers = markets.keys()
        fiat = ['/USDT']
        tickers = [s for s in tickers if any(i in s for i in fiat)]

        '''Selling all coins to USDT'''
        asset_avail = []
        for x in binance_client.get_account()['balances']:
            if float(x['free']) > 0:
                asset = x['asset'] + '/USDT'
                asset_avail.append(asset)
        asset_avail.remove("USDT/USDT")
        asset_avail.remove("BNB/USDT")

        print(f'\nYou have these asset [{asset_avail}]\n')

        if len(asset_avail) > 0:
            for ticker in asset_avail:
                tick = ticker.split('/')
                ticker_2 = tick[0]+tick[1]
                print(ticker, ticker_2)

                most_recent_order = binance_client.get_my_trades(symbol=ticker_2, limit=1)[0]
                most_recent_order = float(most_recent_order['price'])
                get_current_price(ticker)

                if float(most_recent_order/current - 0.0025) * 100 > 100:
                    sell_crypto_currency(ticker, tick[1])
                else:
                    print(f"Yet to make profit from selling [{ticker}] coin\n")




        '''Evaluate the tickers to examine to buy or not'''
        coins = []
        for ticker in tickers:
            try:
                two_days_ago = datetime(now.year, now.month, now.day) - timedelta(days = 2)
                ohlcvs = binance.fetch_ohlcv(ticker, '1d', binance.parse8601(two_days_ago), 3)

                df = pd.DataFrame(ohlcvs, columns = ['time', 'open', 'high', 'low', 'close', 'volume'])
                df['time'] = pd.to_datetime(df['time'], unit='ms')
                df = df.set_index('time')
                df = df[:-1]

                close_y = float(df['close'].iloc[:1])
                close_n = float(df['close'].iloc[1:2])
                high_y = float(df['high'].iloc[:1])
                high_n = float(df['high'].iloc[1:2])
                low_y = float(df['low'].iloc[:1])
                low_n = float(df['low'].iloc[1:2])

                range_y = high_y - low_y
                range_n = high_n - low_n

                #IBS = ( close_n - low_n ) / ( high_n - low_n )

                if range_y < range_n and close_y > close_n and high_y < high_n and low_y > low_n:    # and IBS < 0.2:
                    print(f'==== {ticker} - Buy ====')
                    coins.append(ticker)

                else:
                        print(f"{ticker} - Not the day to buy")
            except:
                print(f"== Error : {ticker} does not have historial data ==")
        print(coins)


        hprs = []
        for ticker in coins:
            hpr = get_hpr(ticker)
            hprs.append((ticker, hpr))

        sorted_hprs = sorted(hprs, key=lambda x:x[1], reverse=True)


        tickers = []
        for x in sorted_hprs:
            tickers.append(x[0])

        fiat = ['DOWN/', 'UP/', 'BEAR/', 'BULL/', 'SUSD/', 'AUD/', 'BRL/', 'EUR/', 'GBP/', 'RUB/',
               'TRY/', 'TUSD/', 'USDC/', 'PAX/', 'BIDR/', 'DAI/', 'IDRT/', 'UAH/', 'NGN/', 'VAI/', 'BVND/']
        USDT = [x for x in tickers if '/USDT' in x]
        USDT = [s for s in USDT if not any(i in s for i in fiat)]

        BNB = [x for x in tickers if '/BNB' in x]
        BNB = [s for s in BNB if not any(i in s for i in fiat)]

        BUSD = [x for x in tickers if '/BUSD' in x]
        BUSD = [s for s in BUSD if not any(i in s for i in fiat)]

        print(f'USDT coins:\n {USDT}\n')
        #print(f'BNB coins:\n {BNB}\n')
        #print(f'BUSD coins:\n {BUSD}\n')


        if len(USDT) == 1:
            usdt = binance_client.get_asset_balance(asset = "USDT")["free"]
            print(usdt)
            usdt = float(usdt)/1
            print(usdt)
            buying_n_coins()

        elif len(USDT) == 2:
            usdt = binance_client.get_asset_balance(asset = "USDT")["free"]
            print(usdt)
            usdt = float(usdt)/2
            print(usdt)
            buying_n_coins()

        elif len(USDT) == 3:
            usdt = binance_client.get_asset_balance(asset = "USDT")["free"]
            print(usdt)
            usdt = float(usdt)/3
            print(usdt)
            buying_n_coins()

        elif len(USDT) == 4:
            usdt = binance_client.get_asset_balance(asset = "USDT")["free"]
            print(usdt)
            usdt = float(usdt)/4
            print(usdt)
            buying_n_coins()

        elif len(USDT) == 5:
            usdt = binance_client.get_asset_balance(asset = "USDT")["free"]
            print(usdt)
            usdt = float(usdt)/5
            print(usdt)
            buying_n_coins()

        elif len(USDT) >= 6:
            usdt = binance_client.get_asset_balance(asset = "USDT")["free"]
            print(usdt)
            usdt = float(usdt)/6
            print(usdt)
            buying_n_coins()

        sys.exit()

    sleep(1)


#if len(USDT) >= 1:
#    n_coin = 5
#    USDT = USDT[:n_coin]
#    for coin in USDT:
#        usdt = binance_client.get_asset_balance(asset = "USDT")["free"]
#        usdt = float(usdt)/n_coin
#        print(f'{coin} ---> Buying now')
#        coin = coin.replace('/', '')
#        buy_crypto_currency(coin, "USDT")
#        print("========")
#        print("= DONE =")
#        print("========\n\n\n")
#
#sys.exit()


'''
if len(BNB) >= 1:
    BNB = BNB[:2]
    for coin in BNB:
        print(f'{coin} gave highest profit')
        coin = coin.replace('/', '')
        buy_crypto_currency(coin, "BNB")
        print("========")
        print("= DONE =")
        print("========\n\n\n")

if len(BUSD) >= 1:
    BUSD = BUSD[:2]
    for coin in BUSD:
        print(f'{BUSD[0]} gave highest profit')
        coin = coin.replace('/', '')
        buy_crypto_currency(coin, "BUSD")
        print("========")
        print("= DONE =")
        print("=========\n\n\n")
'''


