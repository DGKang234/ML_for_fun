from binance.client import Client
import ccxt
from datetime import datetime, timedelta, time
from time import sleep


with open("binance_key.txt") as f:    # call the restored api key
    lines = f.readlines()
    key = lines[0].strip()
    secret = lines[1].strip()
    binance_client = Client(api_key = key, api_secret = secret)
    binance = ccxt.binance({'apiKey': key, 'secret': secret})



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






coins = ['ETHGBP', 'DOGEUSDT', 'XRPEUR']

while True:
    now = datetime.now()
    mid = datetime(now.year, now.month, now.day) + timedelta(days =1, hours = 1)
    print(now)

    if mid < now < mid + timedelta(seconds = 10):
        for coin in coins:
            mid = datetime(now.year, now.month, now.day) + timedelta(days = 1, hours = 1)
            try:
                sell_crypto_currency(coin)
            except:
                print("You didn't buy one of the coin or all of the coin --> Please check the balance of the coin")
    sleep(1)


