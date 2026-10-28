import time
import os
import requests
from threading import Thread
from flask import Flask
from web3 import Web3

# ==========================================
# 1. RENDER HEALTH CHECK SERVER
# ==========================================
app = Flask(__name__)

@app.route('/')
def health_check():
    return "Moe Autonomous Bot is live & operational!", 200

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# ==========================================
# 2. CONFIGURATION & CONTRACT CONSTANTS
# ==========================================
RPC_URLS = [
    "https://eth.llamarpc.com",
    "https://rpc.ankr.com/eth",
    "https://cloudflare-eth.com"
]

WALLET_ADDRESS = Web3.to_checksum_address("0x14925C541c95D827dF2773bA466F8f59CC11B256")
PRIVATE_KEY = os.getenv("PRIVATE_KEY", "0x15add1be9969f2c7e0ec02151dbcdeb3a71186ee600bae310d6cbfd581fefab4")

# Uniswap V3 SwapRouter02 & Token Addresses
UNISWAP_ROUTER_ADDRESS = Web3.to_checksum_address("0x68b3465833fb72a70ecdf485e0e4c7bd8665fc45")
WETH_ADDRESS = Web3.to_checksum_address("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2")
USDC_ADDRESS = Web3.to_checksum_address("0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48")

TELEGRAM_BOT_TOKEN = os.getenv("TELE_BOT_TOKEN", "9050551673:AAG8_jkS0SNHUp1YtkxLZQVcik6s8UfnKvA")
TELEGRAM_CHAT_ID = os.getenv("TELE_CHAT_ID", "5542612428")

ROUTER_ABI = [
    {
        "inputs": [{
            "components": [
                {"internalType": "bytes", "name": "path", "type": "bytes"},
                {"internalType": "address", "name": "recipient", "type": "address"},
                {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
                {"internalType": "uint256", "name": "amountOutMinimum", "type": "uint256"}
            ],
            "internalType": "struct ISwapRouter.ExactInputParams",
            "name": "params",
            "type": "tuple"
        }],
        "name": "exactInput",
        "outputs": [{"internalType": "uint256", "name": "amountOut", "type": "uint256"}],
        "stateMutability": "payable",
        "type": "function"
    }
]

# ==========================================
# 3. UTILITY FUNCTIONS
# ==========================================
def send_telegram_alert(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print(f"[LOCAL REPORT] {message}")
        return
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"❌ Telegram alert failed: {e}")

def get_working_web3():
    for rpc in RPC_URLS:
        try:
            w3 = Web3(Web3.HTTPProvider(rpc))
            if w3.is_connected():
                return w3
        except Exception:
            continue
    return None

# ==========================================
# 4. DEX SWAP ENGINE LOGIC
# ==========================================
def execute_uniswap_v3_swap(w3, amount_in_eth):
    """Encodes and broadcasts a Uniswap V3 ETH -> USDC exactInput swap."""
    try:
        router_contract = w3.eth.contract(address=UNISWAP_ROUTER_ADDRESS, abi=ROUTER_ABI)
        amount_in_wei = w3.to_wei(amount_in_eth, 'ether')
        
        # Path encoding: WETH (20 bytes) + Fee 0.3% (3 bytes) + USDC (20 bytes)
        path = bytes.fromhex(WETH_ADDRESS[2:]) + (3000).to_bytes(3, 'big') + bytes.fromhex(USDC_ADDRESS[2:])
        
        params = {
            'path': path,
            'recipient': WALLET_ADDRESS,
            'amountIn': amount_in_wei,
            'amountOutMinimum': 0  # Adjust for slippage protection in production
        }
        
        nonce = w3.eth.get_transaction_count(WALLET_ADDRESS)
        gas_price = w3.eth.gas_price
        
        tx = router_contract.functions.exactInput(params).build_transaction({
            'from': WALLET_ADDRESS,
            'value': amount_in_wei,
            'gas': 250000,
            'maxFeePerGas': int(gas_price * 1.2),
            'maxPriorityFeePerGas': w3.to_wei(1.5, 'gwei'),
            'nonce': nonce,
            'chainId': 1
        })
        
        signed_tx = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        hash_hex = w3.to_hex(tx_hash)
        
        send_telegram_alert(f"🚀 *DEX Swap Executed!*\nHash: [{hash_hex}](https://etherscan.io/tx/{hash_hex})")
        return hash_hex
    except Exception as e:
        send_telegram_alert(f"❌ *DEX Swap Failed:* {str(e)}")
        return None

# ==========================================
# 5. MAIN BACKGROUND EXECUTION LOOP
# ==========================================
def main_execution_loop():
    print("🤖 Autonomous Worker Loop Starting...")
    send_telegram_alert("🚀 *Bouzihaybot Online!*\nRender container initialized. Web server and DEX engine active.")
    
    daily_stats = {"scans": 0, "swaps_attempted": 0}
    last_daily_report = time.time()

    while True:
        try:
            w3 = get_working_web3()
            if not w3:
                print("⚠️ RPC connection lost. Retrying in 30s...")
                time.sleep(30)
                continue

            balance_wei = w3.eth.get_balance(WALLET_ADDRESS)
            balance_eth = w3.from_wei(balance_wei, 'ether')
            daily_stats["scans"] += 1
            
            print(f"💼 Scan #{daily_stats['scans']} | Address: {WALLET_ADDRESS} | Balance: {balance_eth:.6f} ETH")

            # 24-Hour Daily Summary Report
            if time.time() - last_daily_report >= 86400:
                report = (
                    f"📊 *24-Hour Execution Summary Report*\n\n"
                    f"• Total Network Scans: `{daily_stats['scans']}`\n"
                    f"• DEX Swaps Attempted: `{daily_stats['swaps_attempted']}`\n"
                    f"• Current Wallet Balance: `{balance_eth:.6f} ETH`\n"
                    f"• System Status: `Operational`"
                )
                send_telegram_alert(report)
                last_daily_report = time.time()
                daily_stats["scans"] = 0
                daily_stats["swaps_attempted"] = 0

        except Exception as e:
            print(f"❌ Error in execution loop: {str(e)}")

        time.sleep(60)

if __name__ == '__main__':
    # 1. Start Flask web server in a daemon thread (satisfies Render port checks)
    server_thread = Thread(target=run_web_server)
    server_thread.daemon = True
    server_thread.start()
    
    # 2. Run the main blockchain trading loop
    main_execution_loop()
