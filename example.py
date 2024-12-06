import json
import websocket
import numpy as np
from collections import deque
from datetime import datetime
import time
from main import MorpherTrading  #TODO use local package

# simple scalping strategy: open when price is outside the band and close when it crosses the band on the other side
# stop loss is 2x the threshold so risk/reward is 1:2

# BTC market
MARKET_ID = "0x0bc89e95f9fdaab7e8a11719155f2fd638cb0f665623f3d12aab71d1a125daf9"
LEVERAGE = 10.0
MPH_TOKENS = 5
MOVING_AVERAGE_PERIOD = 5 # 5 minutes
THRESHOLD_PERCENTAGE = 0.1 # Open position if price is over / under 0.1% of moving average

trading = MorpherTrading(private_key="your_private_key")

minute_prices = deque(maxlen=MOVING_AVERAGE_PERIOD)
current_minute = None
last_price = None

last_print = time.time()

current_position = None

def calculate_moving_average(prices):
    return np.mean(prices)

def process_price(price):
    global current_minute, last_price

    now = datetime.now()
    current_min = now.replace(second=0, microsecond=0)

    if current_minute is None:
        current_minute = current_min

    # save the close price of the minute before in the 1 minute array
    if current_min > current_minute:
        if last_price is not None:
            minute_prices.append(last_price)
            print(f"[{datetime.now()}] Minute closed: {current_minute}, Price: {last_price}")
        current_minute = current_min
    last_price = price

def open_long_position(price, ma):
    order_id = trading.openPosition(
        market_id=MARKET_ID,
        mph_token_amount=MPH_TOKENS,
        direction=True, # True for long, False for short
        leverage=LEVERAGE,
    )
    print(f"[{datetime.now()}] Opened long position at price {price} (MA: {ma}). Order ID: {order_id}")

def open_short_position(price, ma):
    order_id = trading.openPosition(
        market_id=MARKET_ID,
        mph_token_amount=MPH_TOKENS,
        direction=False,
        leverage=LEVERAGE,
    )
    print(f"[{datetime.now()}] Opened short position at price {price} (MA: {ma}). Order ID: {order_id}")

def close_position(price, ma):
    order_id = trading.closePosition(
        market_id=MARKET_ID,
        percentage=1, # fully close the position for this strategy
    )
    print(f"[{datetime.now()}] Closed position at price {price} (MA: {ma}). Order ID: {order_id}")

def on_message(ws, message):
    global current_position 
    global last_print
    data = json.loads(message)
    price = float(data['p'])

    process_price(price)

    moving_average = calculate_moving_average(minute_prices) if len(minute_prices) == MOVING_AVERAGE_PERIOD else 0
    lower_threshold = moving_average * (1 - THRESHOLD_PERCENTAGE / 100)
    upper_threshold = moving_average * (1 + THRESHOLD_PERCENTAGE / 100)

    if time.time() > last_print + 5:
        last_print = time.time()
        if len(minute_prices) < MOVING_AVERAGE_PERIOD:
            print(f"[{datetime.now()}] Collecting minute prices... ({len(minute_prices)}/{MOVING_AVERAGE_PERIOD})")
        elif current_position is not None:
            sl = current_position["stop_loss"]
            tp = current_position["take_profit"]
            pv = trading.getPositionValue(MARKET_ID, price)
            print(f"[{datetime.now()}] Price: {price}, Position value: {pv:.2f}, SL: {sl:.2f}, TP: {tp:.2f}")
        else:
            print(f"[{datetime.now()}] Price: {price}, MA: {moving_average:.2f}, Lower: {lower_threshold:.2f}, Upper: {upper_threshold:.2f}")

    # wait until we have the correct number of minutely prices
    if len(minute_prices) < MOVING_AVERAGE_PERIOD:
        return
    
    # triggers
    if current_position is not None:
        # check stop loss / take profit (you can execute istant closePositions as stop loss and take
        # profit or you can closePosition by specifying only_if_price_below and only_if_price_above)
        if current_position["is_long"]:
            if price < current_position["stop_loss"] or price > current_position["take_profit"]:
                close_position(price, moving_average)
                time.sleep(10) # wait a bit after closing a position before opening a new one
                current_position = None
        else:
            if price > current_position["stop_loss"] or price < current_position["take_profit"]:
                close_position(price, moving_average)
                time.sleep(10) # wait a bit after closing a position before opening a new one
                current_position = None

    else:
        if price < lower_threshold:
            current_position = {
                "is_long": True,
                "stop_loss": moving_average * (1 - 2 * THRESHOLD_PERCENTAGE / 100),
                "take_profit": upper_threshold
            }
            open_long_position(price, moving_average)
        elif price > upper_threshold:
            current_position = {
                "is_long": False,
                "stop_loss": moving_average * (1 + 2 * THRESHOLD_PERCENTAGE / 100),
                "take_profit": lower_threshold 
            }
            open_short_position(price, moving_average)
   

def on_error(ws, error):
    print(f"WebSocket error: {error}")

def on_close(ws, close_status_code, close_msg):
    print("WebSocket closed")

def start_trading():
    url = "wss://stream.binance.com:9443/ws/btcusdt@trade"
    ws = websocket.WebSocketApp(
        url,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
    )
    print("Starting WebSocket stream...")
    ws.run_forever()

if __name__ == "__main__":
    start_trading()
