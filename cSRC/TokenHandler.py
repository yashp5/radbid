from web3 import Web3
import json
import time
from .inf import env as ENV

w3 = Web3(Web3.HTTPProvider(ENV.ETH_NODE_URL))

# Load the USDC token contract ABI
with open("usdc_abi.json") as f:
    usdc_abi = json.load(f)

# Instantiate the USDC token contract
usdc_contract = w3.eth.contract(address=ENV.USDC_CONTRACT_ADDRESS, abi=usdc_abi)


def check_transactions():
    event_filter = usdc_contract.events.Transfer.create_filter(
        fromBlock=w3.eth.block_number - 100000,
        argument_filters={"to": ENV.WALLET_ADDRESS},
    )

    # Get all the events that match the filter
    events = event_filter.get_all_entries()
    return events


def text_transaction_details(event):
    USDC_TEXT = f"""
<b>New Tx Has been deposited</b>    
Tx Hash : {event.transactionHash.hex()} 
From : {event.args['from']}  
To : {event.args['to']}
Amount : {event.args['value'] / 10 ** 6}

    """
    return USDC_TEXT


def TokenHandler():
    events = check_transactions()
    return events
