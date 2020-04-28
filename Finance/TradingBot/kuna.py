import json, requests
from timeloop import Timeloop
from datetime import timedelta
import dateutil.parser
from datetime import datetime

tl = Timeloop()

# Three White Candles Strategy
# https://www.investopedia.com/terms/t/three_white_soldiers.asp

# global vars - will be used by multiple threads
# We use minute to aggregate each seconds data to OHLC format

# contains OHLC objects for each minute
minute_candlesticks = []
# contains the current minute candlestick OHLC
current_min_candlestick = {}
# last minute and price processed info - used to detect changes
last_tick_min = None
last_tick_price = None
# If True means that order was placed
in_position = False

@tl.job(interval=timedelta(seconds=1))
def watch_btc_price():
    r = requests.get("https://kuna.io/api/v2/tickers/btcuah")
    tick = json.loads(r.content)

    # Example of tick
    # {
    #   "at": server time milliseconds,
    #   "ticker": {
    #       "buy": цена биткоина на покупку ,
    #       "sell": цена биткоина на продажу,
    #       "low": наименьшая цена сделки за 24 часа,
    #       "high": наибольшая цена сделки за 24 часа,
    #       "last": цена последней сделки,
    #       "vol": объём торгов в базовой валюте за 24 часа,
    #       "amount": общая стоимость торгов в котируемое валюте за 24 часа
    #   }
    # }
    # It appears that the thing we need is only `last` which is the current price to buy and last order price
    # We can calc Open High Low Close by pulling ticks for 1 Min and then reduce this data to OHLC format using `last` price

    tick_minute = datetime.utcfromtimestamp(tick['at']).strftime('%Y-%m-%d %H:%M')
    tick_price = tick["ticker"]["last"]

    #print("tick, minute: {0}, price: {1} UAH".format(tick_minute, tick_price))

    # since it's multithreading, we need to mark these vars as global so that python will use shared state across threads
    global last_tick_min, last_tick_price, current_min_candlestick, minute_candlesticks, in_position

    if (last_tick_min == tick_minute and last_tick_price == tick_price):
        #print("nothing changed")
        return

    # If price and minute was changed - prio new minute start over price change, new minute will have a new price anyway
    # 
    # aggregate data per minute OHLC in minute_candlesticks array
    if not (last_tick_min == tick_minute):
        # New minute started - create a new candlestick
        current_min_candlestick = {
             "at": tick_minute,
           "open": tick_price,
           "high": tick_price,
            "low": tick_price,
          "close": tick_price
        }
        # python can do update by ref
        minute_candlesticks.append(current_min_candlestick)
        print("New minute started\n{0}".format(current_min_candlestick))
    elif not (last_tick_price == tick_price):
        # Price changed - update current candlestick
        current_min_candlestick["high"] = max(current_min_candlestick["high"], tick_price)
        current_min_candlestick["low"] = min(current_min_candlestick["low"], tick_price)
        current_min_candlestick["close"] = tick_price
        print("Current minute updated\n{0}".format(current_min_candlestick))

    # Update last tracked values
    last_tick_min = tick_minute
    last_tick_price = tick_price

    # checking for patters - the actual strategy

    if len(minute_candlesticks) > 3:
        print("== there are more than 3 candlesticks, checking for pattern ==")
        last_candle = minute_candlesticks[-2]
        previous_candle = minute_candlesticks[-3]
        first_candle = minute_candlesticks[-4]

        print("== let's compare the last 3 candle closes ==")
        if last_candle['close'] > previous_candle['close'] and previous_candle['close'] > first_candle['close']:
            print("=== Three green candlesticks in a row, let's make a trade! ===")
            distance = last_candle['close'] - first_candle['open']
            print("Distance is {}".format(distance))
            profit_price = last_candle['close'] + (distance * 2)
            print("I will take profit at {}".format(profit_price))
            loss_price = first_candle['open']
            print("I will sell for a loss at {}".format(loss_price))

            if not in_position:
                print("== Placing order and setting in position to true ==")
                in_position = True
                #place_order(profit_price, loss_price)
                #sys.exit()
        else:
            print("No go")

#watch_btc_price()
tl.start(block=True)
