from trading import MorpherTrading
from strategies.sma import SimpleMovingAverageStrategy


# BTC market
MARKET_ID = "0x0bc89e95f9fdaab7e8a11719155f2fd638cb0f665623f3d12aab71d1a125daf9"
LEVERAGE = 10.0
MPH_TOKENS = 5
MOVING_AVERAGE_PERIOD = 5 # 5 minutes
THRESHOLD_PERCENTAGE = 0.1 # Open position if price is over / under 0.1% of moving average


if __name__ == '__main__':

    trading_engine = MorpherTrading(private_key="0x7bc4c847c6e1ac0bc600383415f9c77bce7dc146c0b40fcafad86fe17bfab8b1")

    strategy = SimpleMovingAverageStrategy(
        trading_engine,
        MARKET_ID,
        LEVERAGE,
        MPH_TOKENS,
        MOVING_AVERAGE_PERIOD,
        THRESHOLD_PERCENTAGE
    )

    strategy.start_trading()
