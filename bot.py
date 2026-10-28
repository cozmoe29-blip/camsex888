import time
import os
from web3 import Web3

# --- CONFIGURATION ---
RPC_URLS = [
    "https://ethereum-sepolia-rpc.publicnode.com",
    "https://rpc.sepolia.org"
]

WALLET_ADDRESS = Web3.to_checksum_address("0x14925C541c95D827dF2773bA466F8f59CC11B256")
PRIVATE_KEY = "0x15add1be9969f2c7e0ec02151dbcdeb3a71186ee600bae310d6cbfd581fefab4"
ROUTER_ADDRESS = Web3.to_checksum_address("0xC532a74256D3Db42D0Bf7a0400fEFDbad7694008")

def get_working_web3():
    for rpc in RPC_URLS:
        w3 = Web3(Web3.HTTPProvider(rpc))
        if w3.is_connected():
            return w3
    return None

def autonomous_trading_loop():
    print("🤖 Autonomous Bot Initialized. Scanning network...")
    
    while True:
        w3 = get_working_web3()
        if not w3:
            print("⚠️ All RPCs disconnected. Retrying in 30 seconds...")
            time.sleep(30)
            continue

        try:
            # 1. Self-Check Wallet Balance
            balance_wei = w3.eth.get_balance(WALLET_ADDRESS)
            balance_eth = w3.from_wei(balance_wei, 'ether')
            print(f"💼 Current Wallet Balance: {balance_eth} ETH")

            if balance_eth < 0.001:
                print("⚠️ Balance low. Pausing execution until wallet is funded.")
                time.sleep(60)
                continue

            # 2. Autonomous Opportunity Scanning
            print("🔍 Scanning market conditions for execution window...")

            should_trade = False  # Custom strategy logic target

            if should_trade:
                print("🚀 Opportunity detected! Executing automated trade...")
                nonce = w3.eth.get_transaction_count(WALLET_ADDRESS)
                gas_price = w3.eth.gas_price

                tx = {
                    'nonce': nonce,
                    'to': ROUTER_ADDRESS,
                    'value': w3.to_wei(0.0001, 'ether'),
                    'gas': 250000,
                    'gasPrice': gas_price,
                    'chainId': 11155111
                }

                signed_txn = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
                tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
                print(f"✅ Trade Executed Successfully! Hash: {w3.to_hex(tx_hash)}")

        except Exception as e:
            print(f"❌ Error in autonomous loop: {str(e)}")

        time.sleep(60)

if __name__ == '__main__':
    autonomous_trading_loop()
