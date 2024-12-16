# Morpher Trading Bot

A simple cryptocurrency trading bot that operates on the Morpher Plasma Sidechain. Instead of using traditional brokers, this bot executes trades through blockchain transactions, providing a decentralized trading experience.

## Overview

This bot implements a basic scalping strategy using moving averages:
- Opens positions when price moves outside a defined band around the moving average
- Closes positions when price crosses the band on the opposite side
- Uses stop losses at 2x the threshold for a 1:2 risk/reward ratio
- Trades BTC market with configurable leverage and position sizes

## Features

- Real-time price data from Binance WebSocket feed
- Configurable parameters:
  - Moving average period (default: 5 minutes)
  - Threshold percentage (default: 0.1%)
  - Leverage (default: 10x)
  - Position size in MPH tokens
- Automatic position management with stop losses and take profits
- Full integration with Morpher's smart contracts for trading

## Requirements

Create a local python env and install requirements:
```bash
python3 -m venv env
source ./env/bin/activate
pip install -r requirements.txt
```

A Private Key.

If you signed up with the Morpher Wallet, then Login to https://wallet.morpher.com, and export your Private Key.

## Configuration

Edit `main.py` to set your parameters:

```python
MARKET_ID = "0x0bc89e95f9fdaab7e8a11719155f2fd638cb0f665623f3d12aab71d1a125daf9"  # BTC market
LEVERAGE = 10.0
MPH_TOKENS = 5
MOVING_AVERAGE_PERIOD = 5  # 5 minutes
THRESHOLD_PERCENTAGE = 0.1  # Open position if price is over/under 0.1% of moving average
```

Create a .env file with your private key inside:

```bash
PRIVATE_KEY=0x...
```

## Usage

Run the bot:

```bash
python example.py
```

The bot will:
1. Connect to Binance's WebSocket feed
2. Calculate moving averages from price data
3. Open long positions when price drops below the lower band
4. Open short positions when price rises above the upper band
5. Manage positions with automatic stop losses and take profits

## Trading Logic

The bot uses the following strategy:
- Calculates a moving average over the specified period
- Creates upper and lower bands using the threshold percentage
- Opens long positions when price drops below lower band
- Opens short positions when price rises above upper band
- Sets stop losses at 2x the threshold distance
- Takes profit when price crosses the opposite band

## Warning

This is experimental software. Use at your own risk. Always test with small amounts first and monitor the bot's performance carefully.

## Dependencies

- web3==7.6.0
- websocket-client
- numpy
