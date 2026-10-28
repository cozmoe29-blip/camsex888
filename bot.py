import time
import os
import requests
from threading import Thread
from flask import Flask, request as flask_request
from web3 import Web3

app = Flask(__name__)

# Brand-new fresh token from BotFather
TELEGRAM_BOT_TOKEN = "9050551673:AAE2GnmCKV110k6aZ8kVLxKzZ6_aI7hhemE"
TELEGRAM_CHAT_ID = "5542612428"

RPC_URLS = [
    "https://eth.llamarpc.com",
    "https://rpc.ankr.com/eth",
    "https://cloudflare-eth.com"
]

WALLET_ADDRESS = Web3.to_checksum_address("0x14925C541c95D827dF2773bA466F8f59CC11B256")

@app.route('/')
def health_check():
    return "Moe Autonomous Bot is live & operational!", 200

@app.route('/webhook', methods=['POST'])
def telegram_webhook():
    try:
        data = flask_request.get_json()
        if 'message' in data:
            chat_id = data['message']['chat']['id']
            text = data['message'].get('text', '').strip().lower()
            
            if text in ['/start', '/help']:
                reply = (
                    "🤖 *Moe Autonomous Bot Active*\n\n"
                    "Available commands:\n"
                    "• `/balance` - Check live wallet balance & gas\n"
                    "• `/status` - Check bot operational status"
                )
                send_message(chat_id, reply)
            elif text in ['/balance', 'balance']:
                w3 = get_working_web3()
                if w3:
                    bal_wei = w3.eth.get_balance(WALLET_ADDRESS)
                    bal_eth = w3.from_wei(bal_wei, 'ether')
                    gas = w3.from_wei(w3.eth.gas_price, 'gwei')
                    reply = f"💼 *Wallet Balance:* `{bal_eth:.6f} ETH`\n⛽ *Gas Price:* `{gas:.2f} Gwei`"
                else:
                    reply = "⚠️ Could not connect to RPC network right now."
                send_message(chat_id, reply)
            elif text in ['/status', 'status']:
                send_message(chat_id, "🟢 *Status:* Bot is running 24/7 on Render cloud and scanning successfully.")
                
        return "OK", 200
    except Exception as e:
        print(f"Webhook error: {e}")
        return "OK", 200

def send_message(chat_id, message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}, timeout=10)
    except Exception as e:
        print(f"❌ Telegram send failed: {e}")

def get_working_web3():
    for rpc in RPC_URLS:
        try:
            w3 = Web3(Web3.HTTPProvider(rpc))
            if w3.is_connected():
                return w3
        except Exception:
            continue
    return None

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

def main_loop():
    print("🤖 Autonomous Worker Loop Starting...")
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": "🚀 *Bouzihaybot Online & Interactive!* Ready for commands.", "parse_mode": "Markdown"}, timeout=10)
    except Exception:
        pass

    while True:
        try:
            w3 = get_working_web3()
            if w3:
                bal = w3.from_wei(w3.eth.get_balance(WALLET_ADDRESS), 'ether')
                print(f"💼 Scan success | Balance: {bal:.6f} ETH")
        except Exception as e:
            print(f"Loop error: {e}")
        time.sleep(60)

if __name__ == '__main__':
    # Auto-register webhook
    try:
        set_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook?url=https://camsex888-1.onrender.com/webhook"
        res = requests.get(set_url, timeout=10)
        print(f"🔗 Webhook Response: {res.text}")
    except Exception as e:
        print(f"Webhook set failed: {e}")

    # Start web server thread
    t = Thread(target=run_web_server)
    t.daemon = True
    t.start()

    # Start background loop
    main_loop()
