import time
import os
import requests
from threading import Thread
from flask import Flask, request as flask_request
from web3 import Web3

# ==========================================
# 1. RENDER HEALTH CHECK & TELEGRAM WEBHOOK SERVER
# ==========================================
app = Flask(__name__)

@app.route('/')
def health_check():
    return "Moe Autonomous Bot is live & operational!", 200

@app.route('/webhook', methods=['POST'])
def telegram_webhook():
    """Receives incoming messages from Telegram so you can talk to your bot."""
    try:
        data = flask_request.get_json()
        if 'message' in data:
            chat_id = data['message']['chat']['id']
            text = data['message'].get('text', '').strip().lower()
            
            if text == '/start' or text == '/help':
                reply = (
                    "🤖 *Moe Autonomous Bot Active*\n\n"
                    "Available commands:\n"
                    "• `/balance` - Check live wallet balance & gas\n"
                    "• `/status` - Check bot operational status"
                )
                send_telegram_message_to_chat(chat_id, reply)
            elif text == '/balance' or text == 'balance':
                w3 = get_working_web3()
                if w3:
                    bal_wei = w3.eth.get_balance(WALLET_ADDRESS)
                    bal_eth = w3.from_wei(bal_wei, 'ether')
                    gas = w3.from_wei(w3.eth.gas_price, 'gwei')
                    reply = f"💼 *Wallet Balance:* `{bal_eth:.6f} ETH`\n⛽ *Gas Price:* `{gas:.2f} Gwei`"
                else:
                    reply = "⚠️ Could not connect to RPC network right now."
                send_telegram_message_to_chat(chat_id, reply)
            elif text == '/status' or text == 'status':
                send_telegram_message_to_chat(chat_id, "🟢 *Status:* Bot is running 24/7 on Render cloud and scanning successfully.")
                
        return "OK", 200
    except Exception as e:
        print(f"Webhook error: {e}")
        return "OK", 200

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

# Hardcoded credentials to completely bypass environment variable truncation issues
TELEGRAM_BOT_TOKEN = "9050551673:AAG8_jkS0SNHUp1YtkxLZQVcik6s8UfnKvA"
TELEGRAM_CHAT_ID = "5542612428"

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
    send_telegram_message_to_chat(TELEGRAM_CHAT_ID, message)

def send_telegram_message_to_chat(chat_id, message):
    if not TELEGRAM_BOT_TOKEN or not chat_id:
        print(f"[LOCAL REPORT] {message}")
        return
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
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
# 4. MAIN BACKGROUND EXECUTION LOOP
# ==========================================
def main_execution_loop():
    print("🤖 Autonomous Worker Loop Starting...")
    send_telegram_alert("🚀 *Bouzihaybot Online & Interactive!*\nRender container initialized. Send `/balance` or `/status` to chat with me.")
    
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
    # 1. Automatically register Telegram Webhook on startup
    if TELEGRAM_BOT_TOKEN:
        webhook_url = "https://camsex888-1.onrender.com/webhook"
        set_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook?url={webhook_url}"
        try:
            res = requests.get(set_url, timeout=10)
            print(f"🔗 Auto-set Webhook Response: {res.text}")
        except Exception as e:
            print(f"⚠️ Failed to auto-set webhook: {e}")

    # 2. Start Flask web server in a daemon thread
    server_thread = Thread(target=run_web_server)
    server_thread.daemon = True
    server_thread.start()
    
    # 3. Run the main blockchain trading loop
    main_execution_loop()
