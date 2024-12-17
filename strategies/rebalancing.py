import requests
from eth_hash.auto import keccak
from datetime import datetime, timedelta
import time
from trading import MorpherTrading


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
        total_balance = balance
        current_positions = {}
        for market in self.weighted_markets.keys():
            current_position = self.trading.getPositionValue(self._get_market_id(market), prices[market])
            current_positions[market] = current_position
            total_balance += current_position
        print(f"Total balance: {total_balance:.2f} MPH.")
        print(f"Current invested: {(total_balance - balance):.2f} MPH, current cash: {balance:.2f}.")
        print(f"New invested: {(total_balance * self.rebalance_percentage):.2f} MPH, new cash: {(total_balance * (1 - self.rebalance_percentage)):.2f}.")

        target_allocation = self._calculate_target_allocation(total_balance)

        for market, target_amount in target_allocation.items():
            current_position = current_positions[market]
            difference = target_amount - current_position

            if difference > 0: # Need to increase position
                self.trading.openPosition(
                    market_id=self._get_market_id(market),
                    mph_token_amount=difference,
                    direction=True, # Long positions for allocation
                    leverage=1,
                )
                print(f"[{datetime.now()}] Increased position in {market} by {difference:.2f} MPH.")
                time.sleep(5)
            elif difference < 0: # Need to decrease position
                self.trading.closePosition(
                    market_id=self._get_market_id(market),
                    percentage=abs(difference) / current_position,
                )
                print(f"[{datetime.now()}] Decreased position in {market} by {abs(difference):.2f} MPH.")
                time.sleep(5)

        print(f"[{datetime.now()}] Rebalancing complete. Target allocation: {target_allocation}")

    @staticmethod
    def _get_market_id(market):
        """Get the morpher market id from the ticker"""
        string = "CRYPTO_" + market
        input_bytes = string.encode('utf-8')
        return '0x' + keccak(input_bytes).hex()

    def start_trading(self):
        print("Launching weighted market rebalancing bot...")
        
        while True:
            now = datetime.now()

            if self.last_rebalance_time is None or now > self.last_rebalance_time + timedelta(days=1):
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
                self.last_rebalance_time = now.replace(hour=0, minute=0, second=0, microsecond=0)

            time.sleep(300)
