from eth_account import Account
import json
import time
from web3 import Web3


SIDECHAIN_RPC = 'https://sidechain.morpher.com'
MORPHER_TOKEN_ADDRESS='0xC44628734a9432a3DAA302E11AfbdFa8361424A5'
MORPHER_ORACLE_ADDRESS='0xf8B5b1699A00EDfdB6F15524646Bd5071bA419Fb'
MORPHER_TRADE_ENGINE_ADDRESS='0xc4a877Ed48c2727278183E18fd558f4b0c26030A'
MORPHER_STATE_ADDRESS='0xB4881186b9E52F8BD6EC5F19708450cE57b24370'


class TradingLibrary:

    def __init__(self, private_key: str):
        self.private_key = private_key
        self.address = Web3.to_checksum_address(Account.from_key(private_key).address)
        self.web3 = Web3(Web3.HTTPProvider(SIDECHAIN_RPC))
        with open("./abi/MorpherToken.json", "r") as abi_file:
            contract_abi = json.load(abi_file)
            self.morpher_token = self.web3.eth.contract(address=MORPHER_TOKEN_ADDRESS, abi=contract_abi)
        with open("./abi/MorpherOracle.json", "r") as abi_file:
            contract_abi = json.load(abi_file)
            self.morpher_oracle = self.web3.eth.contract(address=MORPHER_ORACLE_ADDRESS, abi=contract_abi)
        with open("./abi/MorpherTradeEngine.json", "r") as abi_file:
            contract_abi = json.load(abi_file)
            self.morpher_trade_engine = self.web3.eth.contract(address=MORPHER_TRADE_ENGINE_ADDRESS, abi=contract_abi)
        with open("./abi/MorpherState.json", "r") as abi_file:
            contract_abi = json.load(abi_file)
            self.morpher_state = self.web3.eth.contract(address=MORPHER_STATE_ADDRESS, abi=contract_abi)


    def openPosition(
            self,
            market_id: str,
            mph_token_amount: float,
            direction: bool,
            leverage: float,
            only_if_price_above: float = 0,
            only_if_price_below: float = 0,
            good_until: int = 0,
            good_from: int = 0
        ):
        """
        Opens a new trading position.

        Args:
            market_id (str): The ID (hash) of the market where the position will be opened.
            mph_token_amount (float): The amount of MPH tokens to use for this position.
            direction (bool): The direction of the position; `True` for long, `False` for short.
            leverage (float): The leverage multiplier to apply to the position. (1.0 to 10.0)
            only_if_price_above (float): Open the position only if the price is above this value. 0 for no limit.
            only_if_price_below (float): Open the position only if the price is below this value. 0 for no limit.
            good_until (int): Unix timestamp in seconds specifying the expiration time of the order. 0 for no expiration.
            good_from (int): Unix timestamp in seconds specifying the activation time of the order. 0 for no activation.
        """
        return self.openPositionExact(
            market_id,
            round(mph_token_amount * 1e18),
            direction, round(leverage * 1e8),
            round(only_if_price_above * 1e8),
            round(only_if_price_below * 1e8),
            good_until,
            good_from
        )


    def openPositionExact(
            self,
            market_id: str,
            mph_token_amount: int,
            direction: bool,
            leverage: int,
            only_if_price_above: int = 0,
            only_if_price_below: int = 0,
            good_until: int = 0,
            good_from: int = 0
        ):
        """
        Opens a new trading position.

        Args:
            market_id (str): The ID (hash) of the market where the position will be opened.
            mph_token_amount (int): The amount of MPH tokens to use for this position in WEI.
            direction (bool): The direction of the position; `True` for long, `False` for short.
            leverage (int): The leverage multiplier to apply to the position with 8 decimals points. (100000000 to 1000000000)
            only_if_price_above (int): Open the position only if the price with 8 decimals is above this value. 0 for no limit.
            only_if_price_below (int): Open the position only if the price with 8 decimals is below this value. 0 for no limit.
            good_until (int): Unix timestamp in seconds specifying the expiration time of the order. 0 for no expiration.
            good_from (int): Unix timestamp in seconds specifying the activation time of the order. 0 for no activation.

        Returns:
            str: Transaction hash of the order creation transaction.
        """
        tx = self.morpher_oracle.functions.createOrder(
            market_id,
            0,
            mph_token_amount,
            direction,
            leverage,
            only_if_price_above,
            only_if_price_below,
            good_until,
            good_from
        ).build_transaction({
            "from": self.address,
            "gas": 2000000,
            "gasPrice": 100,
            "nonce": self.web3.eth.get_transaction_count(self.address)
        })

        signed_tx = self.web3.eth.account.sign_transaction(tx, self.private_key)
        tx_hash = self.web3.eth.send_raw_transaction(signed_tx.raw_transaction)

        return self.web3.to_hex(tx_hash)


    def closePosition(
            self,
            market_id: str,
            percentage: float = 1,
            only_if_price_above: float = 0,
            only_if_price_below: float = 0,
            good_until: int = 0,
            good_from: int = 0
        ):
        """
        Closes a percentage of an existing position.

        Args:
            market_id (str): The ID (hash) of the market of the position.
            percentage (int): The percentage of the position to close.
            only_if_price_above (int): Close the position only if the price is above this value. 0 for no limit.
            only_if_price_below (int): Close the position only if the price is below this value. 0 for no limit.
            good_until (int): Unix timestamp in seconds specifying the expiration time of the order. 0 for no expiration.
            good_from (int): Unix timestamp in seconds specifying the activation time of the order. 0 for no activation.

        Returns:
            str: Transaction hash of the order creation transaction.
        """
        position = self.getPosition(market_id)
        if position["longShares"] > 0 and position["shortShares"] > 0:
            raise Exception("Found mixed position (long and short), can't close!")
        elif position["longShares"] == 0 and position["shortShares"] == 0:
            raise Exception("No position found for this market!")

        close_shares = position["longShares"] if position["longShares"] > 0 else position["shortShares"]
        return self.closePositionExact(
            market_id,
            round(percentage * close_shares),
            round(only_if_price_above * 1e8),
            round(only_if_price_below * 1e8),
            good_until,
            good_from
        )


    def closePositionExact(
            self,
            market_id: str,
            close_shares_amount: int,
            only_if_price_above: int = 0,
            only_if_price_below: int = 0,
            good_until: int = 0,
            good_from: int = 0
        ):
        """
        Closes an existing position using the amount of shares.

        Args:
            market_id (str): The ID (hash) of the market of the position.
            close_shares_amount (int): The amount of shares to sell.
            only_if_price_above (int): Close the position only if the price with 8 decimals is above this value. 0 for no limit.
            only_if_price_below (int): Close the position only if the price with 8 decimals is below this value. 0 for no limit.
            good_until (int): Unix timestamp in seconds specifying the expiration time of the order. 0 for no expiration.
            good_from (int): Unix timestamp in seconds specifying the activation time of the order. 0 for no activation.

        Returns:
            str: Transaction hash of the order creation transaction.
        """

        position = self.getPosition(market_id)
        if position["longShares"] > 0 and position["shortShares"] > 0:
            raise Exception("Found mixed position (long and short), can't close!")
        elif position["longShares"] == 0 and position["shortShares"] == 0:
            raise Exception("No position found for this market!")

        tx = self.morpher_oracle.functions.createOrder(
            market_id,
            close_shares_amount,
            0,
            False if position["longShares"] > 0 else True,
            100000000,
            only_if_price_above,
            only_if_price_below,
            good_until,
            good_from
        ).build_transaction({
            "from": self.address,
            "gas": 2000000,
            "gasPrice": 100,
            "nonce": self.web3.eth.get_transaction_count(self.address)
        })

        signed_tx = self.web3.eth.account.sign_transaction(tx, self.private_key)
        tx_hash = self.web3.eth.send_raw_transaction(signed_tx.raw_transaction)

        return self.web3.to_hex(tx_hash)


    def getBalance(self):
        """
        Shows current MPH balance of the account.

        Returns:
            float: current MPH balance.
        """
        return self.getBalanceExact() / 1e18


    def getBalanceExact(self):
        """
        Shows current MPH balance of the account in WEI.

        Returns:
            int: current MPH balance in WEI.
        """
        return self.morpher_token.functions.balanceOf(self.address).call()


    def getPosition(self, market_id: str):
        """
        Shows current position for a specific market.

        Returns:
            dict: All information regarding current position in the market.
        """
        result = self.morpher_trade_engine.functions.getPosition(self.address, market_id).call()
        return {
            "longShares": result[0],
            "shortShares": result[1],
            "averagePrice": result[2],
            "averageSpread": result[3],
            "averageLeverage": result[4],
            "liquidationPrice": result[5]
        }


    def getPositionValue(self, market_id: str, current_price: float, current_spread: float = None):
        """
        Shows current value of the position for a specific market.

        Args:
            market_id (str): The ID (hash) of the market of the position.
            current_price (float): The current market price.
            current_spread (float): The current market spread in USD, if None it will use the same spread as position

        Returns:
            float: Position value in MPH.
        """
        return self.getPositionValueExact(market_id, current_price, current_spread) / 1e18


    def getPositionValueExact(self, market_id: str, current_price: float, current_spread: float = None):
        """
        Shows current value of the position for a specific market.

        Args:
            market_id (str): The ID (hash) of the market of the position.
            current_price (float): The current market price.
            current_spread (float): The current market spread in USD, if None it will use the same spread as position

        Returns:
            int: Position value in MPH WEI.
        """
        position = self.getPosition(market_id)
        if position["longShares"] > 0 and position["shortShares"] > 0:
            raise Exception("Found mixed position (long and short)!")
        elif position["longShares"] == 0 and position["shortShares"] == 0:
            return 0

        price = round(current_price * 1e8)
        spread = round(current_spread * 1e8) if current_spread is not None else position["averageSpread"]
        last_updated = self.morpher_state.functions.getLastUpdated(self.address, market_id).call()

        if position["longShares"] > 0:
            value = self.morpher_trade_engine.functions.longShareValue(
                position["averagePrice"],
                position["averageLeverage"],
                last_updated,
                price,
                spread,
                position["averageLeverage"],
                True
            ).call()
            return value * position["longShares"]

        value = self.morpher_trade_engine.functions.shortShareValue(
            position["averagePrice"],
            position["averageLeverage"],
            last_updated,
            price,
            spread,
            position["averageLeverage"],
            True
        ).call()
        return value * position["shortShares"]

    def _getOrderId(self, market_id: str):
        time.sleep(1)
        retries = 0
        while retries < 10:
            start = self.web3.eth.block_number - 10
            logs = self.web3.eth.get_logs({
                'fromBlock': start,
                'toBlock': 'latest',
                'address': MORPHER_ORACLE_ADDRESS,
                'topics': ['0xc7392b9822094f2dca86d2a7a97945e80918a8aee61c04de90253f3683b56950'] # OrderCreated
            })
            found_log = None
            for log in logs:
                if log.topics[2] == f"0x000000000000000000000000{self.address[2:]}" and log.topics[3] == market_id:
                    found_log = log
            if found_log:
                return found_log.topics[1]
            time.sleep(1)
            retries += 1
        raise Exception("Order not found after 10 seconds!")
