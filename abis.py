morpher_token_abi = [
    {
        "type": "function",
        "name": "balanceOf",
        "inputs": [
            {
                "name": "account",
                "type": "address",
                "internalType": "address"
            }
        ],
        "outputs": [
            {
                "name": "",
                "type": "uint256",
                "internalType": "uint256"
            }
        ],
        "stateMutability": "view"
    }
]

morpher_oracle_abi = [
    {
        "type": "function",
        "name": "createOrder",
        "inputs": [
            {
                "name": "_marketId",
                "type": "bytes32",
                "internalType": "bytes32"
            },
            {
                "name": "_closeSharesAmount",
                "type": "uint256",
                "internalType": "uint256"
            },
            {
                "name": "_openMPHTokenAmount",
                "type": "uint256",
                "internalType": "uint256"
            },
            {
                "name": "_tradeDirection",
                "type": "bool",
                "internalType": "bool"
            },
            {
                "name": "_orderLeverage",
                "type": "uint256",
                "internalType": "uint256"
            },
            {
                "name": "_onlyIfPriceAbove",
                "type": "uint256",
                "internalType": "uint256"
            },
            {
                "name": "_onlyIfPriceBelow",
                "type": "uint256",
                "internalType": "uint256"
            },
            {
                "name": "_goodUntil",
                "type": "uint256",
                "internalType": "uint256"
            },
            {
                "name": "_goodFrom",
                "type": "uint256",
                "internalType": "uint256"
            }
        ],
        "outputs": [
            {
                "name": "_orderId",
                "type": "bytes32",
                "internalType": "bytes32"
            }
        ],
        "stateMutability": "payable"
    },
    {
        "type": "function",
        "name": "initiateCancelOrder",
        "inputs": [
            {
                "name": "_orderId",
                "type": "bytes32",
                "internalType": "bytes32"
            }
        ],
        "outputs": [],
        "stateMutability": "nonpayable"
    }
]

morpher_trade_engine_abi = [
    {
        "type": "function",
        "name": "getOrder",
        "inputs": [
            {
                "name": "_orderId",
                "type": "bytes32",
                "internalType": "bytes32"
            }
        ],
        "outputs": [
            {
                "name": "_userId",
                "type": "address",
                "internalType": "address"
            },
            {
                "name": "_marketId",
                "type": "bytes32",
                "internalType": "bytes32"
            },
            {
                "name": "_closeSharesAmount",
                "type": "uint256",
                "internalType": "uint256"
            },
            {
                "name": "_openMPHTokenAmount",
                "type": "uint256",
                "internalType": "uint256"
            },
            {
                "name": "_marketPrice",
                "type": "uint256",
                "internalType": "uint256"
            },
            {
                "name": "_marketSpread",
                "type": "uint256",
                "internalType": "uint256"
            },
            {
                "name": "_orderLeverage",
                "type": "uint256",
                "internalType": "uint256"
            }
        ],
        "stateMutability": "view"
    },
    {
        "type": "function",
        "name": "getPosition",
        "inputs": [
            {
                "name": "_address",
                "type": "address",
                "internalType": "address"
            },
            {
                "name": "_marketId",
                "type": "bytes32",
                "internalType": "bytes32"
            }
        ],
        "outputs": [
            {
                "name": "longShares",
                "type": "uint256",
                "internalType": "uint256"
            },
            {
                "name": "shortShares",
                "type": "uint256",
                "internalType": "uint256"
            },
            {
                "name": "meanEntryPrice",
                "type": "uint256",
                "internalType": "uint256"
            },
            {
                "name": "meanEntrySpread",
                "type": "uint256",
                "internalType": "uint256"
            },
            {
                "name": "meanEntryLeverage",
                "type": "uint256",
                "internalType": "uint256"
            },
            {
                "name": "liquidationPrice",
                "type": "uint256",
                "internalType": "uint256"
            }
        ],
        "stateMutability": "view"
    },
    {
        "type": "function",
        "name": "longShareValue",
        "inputs": [
            {
                "name": "_positionAveragePrice",
                "type": "uint256",
                "internalType": "uint256"
            },
            {
                "name": "_positionAverageLeverage",
                "type": "uint256",
                "internalType": "uint256"
            },
            {
                "name": "_positionTimeStampInMs",
                "type": "uint256",
                "internalType": "uint256"
            },
            {
                "name": "_marketPrice",
                "type": "uint256",
                "internalType": "uint256"
            },
            {
                "name": "_marketSpread",
                "type": "uint256",
                "internalType": "uint256"
            },
            {
                "name": "_orderLeverage",
                "type": "uint256",
                "internalType": "uint256"
            },
            {
                "name": "_sell",
                "type": "bool",
                "internalType": "bool"
            }
        ],
        "outputs": [
            {
                "name": "_shareValue",
                "type": "uint256",
                "internalType": "uint256"
            }
        ],
        "stateMutability": "view"
    },
    {
        "type": "function",
        "name": "shortShareValue",
        "inputs": [
            {
                "name": "_positionAveragePrice",
                "type": "uint256",
                "internalType": "uint256"
            },
            {
                "name": "_positionAverageLeverage",
                "type": "uint256",
                "internalType": "uint256"
            },
            {
                "name": "_positionTimeStampInMs",
                "type": "uint256",
                "internalType": "uint256"
            },
            {
                "name": "_marketPrice",
                "type": "uint256",
                "internalType": "uint256"
            },
            {
                "name": "_marketSpread",
                "type": "uint256",
                "internalType": "uint256"
            },
            {
                "name": "_orderLeverage",
                "type": "uint256",
                "internalType": "uint256"
            },
            {
                "name": "_sell",
                "type": "bool",
                "internalType": "bool"
            }
        ],
        "outputs": [
            {
                "name": "_shareValue",
                "type": "uint256",
                "internalType": "uint256"
            }
        ],
        "stateMutability": "view"
    }
]

morpher_state_abi = [
    {
        "type": "function",
        "name": "getLastUpdated",
        "inputs": [
            {
                "name": "_address",
                "type": "address",
                "internalType": "address"
            },
            {
                "name": "_marketHash",
                "type": "bytes32",
                "internalType": "bytes32"
            }
        ],
        "outputs": [
            {
                "name": "",
                "type": "uint256",
                "internalType": "uint256"
            }
        ],
        "stateMutability": "view"
    }
]
