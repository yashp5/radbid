import asyncio
from web3 import Web3
from eth_account import Account
from eth_account.signers.local import LocalAccount
from web3.middleware import construct_sign_and_send_raw_middleware
from eth_defi.token import fetch_erc20_details
from eth_defi.token import fetch_erc20_details
from eth_defi.confirmation import wait_transactions_to_complete
import datetime
from datetime import datetime as dt
from web3.middleware import geth_poa_middleware
from web3 import exceptions as w3EXP


import json
from cSRC.inf import env as ENV
from cSRC.dbUser import Acc as ACC


def checkETHBalance(wallet_address):
    w3 = Web3(Web3.HTTPProvider(ENV.ETH_NODE_URL))
    if w3.is_address(wallet_address):
        balance_wei = w3.eth.get_balance(wallet_address)
        balance_eth = w3.from_wei(balance_wei, "ether")
        return balance_eth
    return None


def checkUSDCBalance(wallet_address):
    w3 = Web3(Web3.HTTPProvider(ENV.ETH_NODE_URL))
    with open("usdc_abi.json") as f:
        usdc_abi = json.load(f)

    if w3.is_address(wallet_address):
        usdc_contract = w3.eth.contract(address=ENV.USDC_CONTRACT_ADDRESS, abi=usdc_abi)
        usdc_balance = usdc_contract.functions.balanceOf(wallet_address).call()
        return usdc_balance
    return None


w3 = Web3(Web3.HTTPProvider(ENV.ETH_NODE_URL))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
contract_address = ENV.USDC_CONTRACT_ADDRESS
with open("usdc_abi.json", "r") as abi_file:
    usdt_contract_abi = json.load(abi_file)
contract = w3.eth.contract(address=contract_address, abi=usdt_contract_abi)
token_details = fetch_erc20_details(w3, contract_address)


async def send_usdt_transaction(from_wallet: ACC, to_wallet: ACC, amount):
    # try :
    print(ENV.SK)
    private_key = w3.to_hex(
        w3.eth.account.decrypt(from_wallet.private_key, from_wallet.encription + ENV.SK)
    )
    account: LocalAccount = Account.from_key(private_key)
    w3.middleware_onion.add(construct_sign_and_send_raw_middleware(account))
    raw_amount = token_details.convert_to_raw(amount)

    # print(f'stamps1:{str(dt.now())}')
    async def th():
        transaction_hash = contract.functions.transfer(
            to_wallet.address, raw_amount
        ).transact(
            {"from": from_wallet.address}
        )  # w3.eth.send_raw_transaction(signed_transaction.rawTransaction)
        return transaction_hash.hex()

    tx = await asyncio.to_thread(th)
    # print(f'stamps2:{str(dt.now())}')
    return tx
    # usdt_contract_address = ENV.USDC_CONTRACT_ADDRESS
    # contract = w3.eth.contract(address=usdt_contract_address, abi=usdt_contract_abi)
    # assert w3.is_checksum_address(to_wallet.address), f"Not a valid address: {to_wallet.address}"
    # token_details =  fetch_erc20_details(w3, usdt_contract_address)
    # raw_amount =  token_details.convert_to_raw(amount)
    # tx_hash = contract.functions.transfer(to_wallet.address, raw_amount).transact({"from": account.address})
    # await wait_transactions_to_complete(w3, [tx_hash], max_timeout=datetime.timedelta(seconds=45))
    # return tx_hash.hex() , None
    # except w3EXP.ContractLogicError as e:
    #  return None , e
    # except:
    #   return None , 'ETH balance is low'


def calculate_gas_and_eth(private_key, recipient_address, amount_usdt, public_key):
    w3 = Web3(Web3.HTTPProvider(ENV.ETH_NODE_URL))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    with open("usdc_abi.json", "r") as abi_file:
        usdt_contract_abi = json.load(abi_file)
    usdt_contract_address = ENV.USDC_CONTRACT_ADDRESS
    contract = w3.eth.contract(address=usdt_contract_address, abi=usdt_contract_abi)
    amount_in_wei = int(amount_usdt * 10**6)
    gas_cost = contract.functions.transfer(
        recipient_address, amount_in_wei
    ).estimate_gas({"from": Web3.to_checksum_address(public_key)})
    gas_price = w3.eth.gas_price
    total_eth_needed = w3.from_wei(gas_cost * gas_price, "ether")
    return gas_cost, gas_price, total_eth_needed
