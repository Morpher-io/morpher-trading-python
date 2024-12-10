import json
import websocket
import numpy as np
from collections import deque
from datetime import datetime
import time
from trading import MorpherTrading

# simple scalping strategy: open when price is outside the band and close when it crosses the band on the other side
# stop loss is 2x the threshold so risk/reward is 1:2

class SimpleMovingAverageStrategy:

    def __init__(
            self,
            trading_engine: MorpherTrading,
            market_id: str,
            leverage: float,
            trading_size: float,
            sma_period: int,
            trigger_threshold: float
        ):
        self.trading = trading_engine
        self.market_id = market_id
        self.leverage = leverage
        self.mph_tokens = trading_size
        self.moving_average_period = sma_period
        self.threshold_percentage = trigger_threshold

        self.minute_prices = deque(maxlen=self.moving_average_period)
        self.current_minute = None
        self.last_price = None

        self.last_print = time.time()

        self.current_position = None
        self.executing = False

    @staticmethod
    def _calculate_moving_average(prices):
        return np.mean(prices)

    def _process_price(self, price):

        now = datetime.now()
        current_min = now.replace(second=0, microsecond=0)

        if self.current_minute is None:
            self.current_minute = current_min

        # save the close price of the minute before in the 1 minute array
        if current_min > self.current_minute:
            if self.last_price is not None:
                self.minute_prices.append(self.last_price)
                print(f"[{datetime.now()}] Minute closed: {self.current_minute}, Price: {self.last_price}")
            self.current_minute = current_min
        self.last_price = price

    def _open_long_position(self, price, ma):
        order_id = self.trading.openPosition(
            market_id=self.market_id,
            mph_token_amount=self.mph_tokens,
            direction=True, # True for long, False for short
            leverage=self.leverage,
        )
        print(f"[{datetime.now()}] Opened long position at price {price} (MA: {ma}). Order ID: {order_id}")

    def _open_short_position(self, price, ma):
        order_id = self.trading.openPosition(
            market_id=self.market_id,
            mph_token_amount=self.mph_tokens,
            direction=False,
            leverage=self.leverage,
        )
        print(f"[{datetime.now()}] Opened short position at price {price} (MA: {ma}). Order ID: {order_id}")

    def _close_position(self, price, ma):
        order_id = self.trading.closePosition(
            market_id=self.market_id,
            percentage=1, # fully close the position for this strategy
        )
        print(f"[{datetime.now()}] Closed position at price {price} (MA: {ma}). Order ID: {order_id}")

    def _on_message(self, ws, message):
        data = json.loads(message)
        price = float(data['p'])

        self._process_price(price)

        moving_average = self._calculate_moving_average(self.minute_prices) if len(self.minute_prices) == self.moving_average_period else 0
        lower_threshold = moving_average * (1 - self.threshold_percentage / 100)
        upper_threshold = moving_average * (1 + self.threshold_percentage / 100)

        if time.time() > self.last_print + 5:
            self.last_print = time.time()
            if len(self.minute_prices) < self.moving_average_period:
                print(f"[{datetime.now()}] Collecting minute prices... ({len(self.minute_prices)}/{self.moving_average_period})")
            elif self.executing:
                print("Closing position...")
            elif self.current_position is not None:
                sl = self.current_position["stop_loss"]
                tp = self.current_position["take_profit"]
                pv = self.trading.getPositionValue(self.market_id, price)
                print(f"[{datetime.now()}] Price: {price}, Position value: {pv:.2f}, SL: {sl:.2f}, TP: {tp:.2f}")
            else:
                print(f"[{datetime.now()}] Price: {price}, MA: {moving_average:.2f}, Lower: {lower_threshold:.2f}, Upper: {upper_threshold:.2f}")

        # wait until we have the correct number of minutely prices
        if len(self.minute_prices) < self.moving_average_period:
            return

        # wait until order is confirmed
        if self.executing:
            return

        # triggers
        if self.current_position is not None:
            # check stop loss / take profit (you can execute istant closePositions as stop loss and take
            # profit or you can closePosition by specifying only_if_price_below and only_if_price_above)
            if self.current_position["is_long"]:
                if price < self.current_position["stop_loss"] or price > self.current_position["take_profit"]:
                    self.executing = True
                    self._close_position(price, moving_average)
                    time.sleep(10) # wait a bit after closing a position before opening a new one
                    self.current_position = None
                    self.executing = False
            else:
                if price > self.current_position["stop_loss"] or price < self.current_position["take_profit"]:
                    self.executing = True
                    self._close_position(price, moving_average)
                    time.sleep(10)
                    self.current_position = None
                    self.executing = False

        else:
            if price < lower_threshold:
                self.executing = True
                self._open_long_position(price, moving_average)
                time.sleep(10)
                self.current_position = {
                    "is_long": True,
                    "stop_loss": moving_average * (1 - 2 * self.threshold_percentage / 100),
                    "take_profit": upper_threshold
                }
                self.executing = False
            elif price > upper_threshold:
                self.executing = True
                self._open_short_position(price, moving_average)
                time.sleep(10)
                self.current_position = {
                    "is_long": False,
                    "stop_loss": moving_average * (1 + 2 * self.threshold_percentage / 100),
                    "take_profit": lower_threshold 
                }
                self.executing = False
    
    def _on_error(self, ws, error):
        print(f"WebSocket error: {error}")

    def _on_close(self, ws, close_status_code, close_msg):
        print("WebSocket closed")

    def start_trading(self):
        print("Launching bot...")
        print(f"User balance: {self.trading.getBalance()} MPH")
        url = "wss://stream.binance.com:9443/ws/btcusdt@trade"
        ws = websocket.WebSocketApp(
            url,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close,
        )
        print("Starting WebSocket stream...")
        ws.run_forever()
