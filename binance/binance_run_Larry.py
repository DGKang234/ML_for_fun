import os
import sys
import pandas as pd
import math
import os.path
from time import sleep
from datetime import datetime, timedelta, time
import traceback
from binance.client import Client
import ccxt

##############
# Parameters #
##############
buy_with = "USDT"
sell_with = input("What Coin do you want to buy? : ")
sell_with = str.upper(sell_with)
ticker = sell_with + "/" + buy_with
ticker_2 = sell_with + buy_with

decimal = input("what is the maximum decimal point of unit of the coin you can buy? : ")
dec_point = {"0":1, "1":10, "2":100, "3":1000, "4":10000, "5":100000, "6":1000000, "7":10000000, "8":100000000}
decimal_point = int(dec_point[decimal])

#print("The default Safety 'Bumper' is -6 %")
print("There is no safety 'Bumper'")

k = 0.334
bumper = 6
fee = 0.003


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
    unit = math.floor(unit*decimal_point)/decimal_point                                                         ## Decimal point
    print(f"Attempt to BUY {unit} amount of {ticker}")
    buy_market = binance_client.order_limit_buy(symbol = ticker, quantity = unit, price = lowest_ask_price)      # executing the trade
    print(buy_market)
    price_bought = float(buy_market['price'])
    print(price_bought)
    print(f"### BUYing '{unit}' of '{ticker}' coin at '{lowest_ask_price} USDT' ### ")
    return price_bought


def sell_crypto_currency(ticker):
    unit = binance_client.get_asset_balance(asset = sell_with)['free']
    unit = math.floor(float(unit)*decimal_point)/decimal_point                                                                          ## Decimal point
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

    #today = df.iloc[-1]
    #today_close = float(today['close'])
    #today_high = float(today['high'])
    #today_low = float(today['low'])
    return yesterday_close, yesterday_high, yesterday_low    #, today_high, today_low  #today_close


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
mid = datetime(now.year, now.month, now.day) + timedelta(days = 1, hours = 1)
list_profit = []

while True:
    try:

        now = datetime.now()

        get_yesterday_ma5(ticker)
        get_yesterday_price(ticker)
        get_current_price(ticker)
        get_target_price(ticker, k)

        most_recent_order = binance_client.get_my_trades(symbol=ticker_2, limit=1)[0]
        price_bought = float(most_recent_order["price"])
        profit = round((current/price_bought - 0.003) * 100, 2)

        #tomorrow_target = current + (today_high + today_low) * k

        print('\n')
        print("Block : A")
        print(now)
        print(f'           [MA5] price is : {ma5}')
        print(f'        [target] price is : {target}')
        print(f'The lowest [ask] price is : {current}')
        print(f"If you manually bought the coin recently the current profit is [{profit}] %")
        print(f'All of {ticker} will be sold automatically at {mid}')
        #print(f"The predicted target value for tomorrow is {tomorrow_target}")



        # If profit lose {bumper} % profit sell the coin #
        #if profit <= int(100-bumper):
        #    sell_crypto_currency(ticker_2)
        #    print("### Losing 6 % profit - Closing the position ###")
        #    print("Turning off the automation trading system -- OFF")





        # Currnet price is not matching with the target/MA5 price #
        if mid < now < mid + timedelta(seconds = 10):
            mid = datetime(now.year, now.month, now.day) + timedelta(days = 1, hours = 1)      # Selling point (sell at 5 pm)
            sell_crypto_currency(ticker_2)                                          # SELL


#############################################
########### After bought the coin ###########
#############################################

        if (current > target): #and (current > ma5):
            try:
                buy_crypto_currency(ticker_2)                                       # BUY
            except: #Exception as exception:
                #traceback.print_exc()
                print("=========================================================================================")
                print("== Error from : Already bought the coin with all available balance or Invalid quantity ==")
                print("=========================================================================================")






            # Price was mathching with the target/MA5 price and bought them at target/MA5 #
            while now < mid:
                try:
                    get_current_price(ticker)
                    now = datetime.now()

                    most_recent_order = binance_client.get_my_trades(symbol=ticker_2, limit=1)[0]    #.get_all_orders(symbol='XRPUSDT', limit=1)
                    price_bought = float(most_recent_order["price"])                                    #*float(most_recent_order["qty"])
                    profit = round((current/price_bought - fee) * 100, 2)


                    print('\n')
                    print(now)
                    #print(f'           [MA5] price is : {ma5}')
                    print(f"Bought the coin at        : {price_bought}")
                    print(f'        [target] price is : {target}')
                    print(f'The lowest [ask] price is : {current}')
                    print(f"Current profit is : {profit} %")
                    print(f'All of {ticker} will be sold at {mid} automatically')
                    #print(f'All of {ticker} will be sold if {profit} is less than -5 % point {max_profit}')




                    # If profit lose {bumper} % profit sell the coin #
                    if profit <= int(100-bumper):
                        sell_crypto_currency(ticker_2)
                        print("### Losing 6 % profit - Closing the position ###")
                        print("Turning off the automation trading system -- OFF")




                    # If current profit is {bumper} % less than max profit sell the coin #
                    #list_profit.append(profit)
                    #list_profit.sort(reverse = True)
                    #list_profit = list_profit[:5]
                    #max_profit = max(list_profit)
                    #print(f'All of {ticker} will be sold if {profit} is less than -5 % point {max_profit}')
                    #diff = math.floor((max_profit - profit)*100)/100
                    #unit = math.floor(unit*10)/10
                    #print(f'Current difference : {diff}')
                    #if profit <= max_profit - bumper:
                    #    sell_crypto_currency(ticker_2)
                    #    print("### Gained {profit} which is -5 % from max profit (max_profit) ###")
                    #    print("Turning off the automation trading system -- OFF")




                    # If coin gains 30 % profit sell the coin #
                    if profit >= 130:
                        sell_crypto_currency(ticker_2)
                        print("### Gaining 30 % profit - Closing the position ###")
                        print("Turning off the automation trading system -- OFF")


############################################
############################################
############################################



                except Exception as exception:
                    traceback.print_exc()
                    print("======================================")
                    print("== Error from : Block [B], [C], [D] ==")
                    print("======================================")
                    raise
                sleep(1)



    except Exception as exception:
        traceback.print_exc()
        print("===============================================")
        print("== Error from : Selling process at mid night ==")
        print("===============================================")
        sys.exit()
    sleep(1)
