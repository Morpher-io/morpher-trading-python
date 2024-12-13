import requests
from datetime import datetime, timedelta
import time
from trading import MorpherTrading


# TODO calculate hash for each market when interacting with trading engine
class WeightedMarketRebalancingStrategy:

    def __init__(
            self,
            trading_engine: MorpherTrading,
            weighted_markets: dict,
            rebalance_percentage: float
        ):
        self.trading = trading_engine
        self.weighted_markets = weighted_markets  # e.g., {"BTC": 0.3, "ETH": 0.3, "DOGE": 0.4}
        self.rebalance_percentage = rebalance_percentage  # e.g., 0.5 (50% of total balance)

        self.last_rebalance_time = None

    def _fetch_market_price(self, market):
        """Fetch the latest price for a given market using Binance REST API."""
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={market}USDT"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            return float(data['price'])
        except requests.RequestException as e:
            print(f"Error fetching price for {market}: {e}")
            return None

    def _calculate_target_allocation(self, balance):
        """Calculate the target allocation for each market based on weights."""
        allocation = {}
        for market, weight in self.weighted_markets.items():
            allocation[market] = balance * self.rebalance_percentage * weight
        return allocation

    def _rebalance_positions(self, balance, prices):
        """Rebalance positions according to the target weights."""
        target_allocation = self._calculate_target_allocation(balance)

        for market, target_amount in target_allocation.items():
            current_position = self.trading.getPositionValue(market, prices[market])
            difference = target_amount - current_position

            if difference > 0: # Need to increase position
                self.trading.openPosition(
                    market_id=market,
                    mph_token_amount=difference,
                    direction=True, # Long positions for allocation
                    leverage=1,
                )
                print(f"[{datetime.now()}] Increased position in {market} by {difference:.2f} MPH.")
            elif difference < 0: # Need to decrease position
                self.trading.closePosition(
                    market_id=market,
                    percentage=abs(difference) / current_position,
                )
                print(f"[{datetime.now()}] Decreased position in {market} by {abs(difference):.2f} MPH.")

        print(f"[{datetime.now()}] Rebalancing complete. Target allocation: {target_allocation}")

    def start_trading(self):
        print("Launching weighted market rebalancing bot...")
        
        while True:
            now = datetime.now()

            if self.last_rebalance_time is None or now >= self.last_rebalance_time + timedelta(days=1):
                print(f"[{now}] Rebalancing positions...")
                balance = self.trading.getBalance()
                print(f"[{now}] Current balance: {balance:.2f} MPH")

                prices = {}
                for market in self.weighted_markets.keys():
                    price = self._fetch_market_price(market)
                    if price is not None:
                        print(f"[{now}] {market} price: {price:.2f} USDT")
                        prices[market] = price
                    else:
                        raise Exception("Cannot rebalance without price!")

                self._rebalance_positions(balance, prices)
                self.last_rebalance_time = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)

            time.sleep(300)
