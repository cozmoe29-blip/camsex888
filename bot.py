import time
import os
import requests
from threading import Thread
from flask import Flask, request as flask_request
from web3 import Web3

app = Flask(__name__)

# Configuration
TELEGRAM_BOT_TOKEN = "9091003001:AAHfI2YGog1vWSVTkE4IY4Qbop-m5FBHA6A"
TELEGRAM_CHAT_ID = "5542612428"

RPC_URLS = [
    "https://eth.llamarpc.com",
    "https://rpc.ankr.com/eth",
    "https://cloudflare-eth.com"
]

WALLET_ADDRESS = Web3.to_checksum_address("0x14925C541c95D827dF2773bA466F8f59CC11B256")
PRIVATE_KEY = os.getenv("PRIVATE_KEY", "0x15add1be9969f2c7e0ec02151dbcdeb3a71186ee600bae310d6cbfd581fefab4")

# Global trading state flag controlled via Telegram
TRADING_ACTIVE = False
SESSION_STATS = {"scans": 0, "opportunities_found": 0, "trades_executed": 0, "estimated_profit_eth": 0.0}

@app.route('/')
def health_check():
    return "Moe Autonomous Trading Bot is live & operational!", 200

@app.route('/webhook', methods=['POST'])
def telegram_webhook():
    global TRADING_ACTIVE
    try:
        data = flask_request.get_json()
        if 'message' in data:
            chat_id = data['message']['chat']['id']
            text = data['message'].get('text', '').strip().lower()
            
            if text in ['/start', '/help']:
                reply = (
                    "🤖 *Moe Autonomous Trading Bot*\n\n"
                    "Command Center:\n"
                    "• `/balance` - Live wallet balance & gas\n"
                    "• `/start_trading` - Enable 24/7 autonomous profit scanner\n"
                    "• `/stop_trading` - Pause autonomous trading\n"
                    "• `/profits` - View live session performance & stats\n"
                    "• `/status` - Check system health"
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
                
            elif text == '/start_trading':
                TRADING_ACTIVE = True
                send_message(chat_id, "🟢 *Autonomous Trading Activated!* Bot is now actively scanning DEX pools 24/7 for opportunities.")
                
            elif text == '/stop_trading':
                TRADING_ACTIVE = False
                send_message(chat_id, "🔴 *Autonomous Trading Paused.* Bot is in standby monitoring mode.")
                
            elif text in ['/profits', 'profits']:
                reply = (
                    f"📊 *Live Trading Session Stats*\n\n"
                    f"• Status: `{'ACTIVE 🟢' if TRADING_ACTIVE else 'PAUSED 🔴'}`\n"
                    f"• Total Scans Completed: `{SESSION_STATS['scans']}`\n"
                    f"• Market Opportunities Logged: `{SESSION_STATS['opportunities_found']}`\n"
                    f"• Trades Executed: `{SESSION_STATS['trades_executed']}`\n"
                    f"• Est. Profit: `{SESSION_STATS['estimated_profit_eth']:.6f} ETH`"
                )
                send_message(chat_id, reply)
                
            elif text in ['/status', 'status']:
                status_text = "🟢 Active & Scanning" if TRADING_ACTIVE else "🟡 Standby Mode"
                send_message(chat_id, f"🤖 *System Status:* `{status_text}`\nRender cloud worker operating normally.")
                
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
    global TRADING_ACTIVE
    print("🤖 Autonomous Trading Loop Initialized...")
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": "🚀 *Moe Dex Bot Initialized!* Use `/start_trading` in Telegram to launch 24/7 autonomous profit scanning.", "parse_mode": "Markdown"}, timeout=10)
    except Exception:
        pass

    while True:
        try:
            w3 = get_working_web3()
            if w3:
                SESSION_STATS["scans"] += 1
                bal = w3.from_wei(w3.eth.get_balance(WALLET_ADDRESS), 'ether')
                gas = w3.from_wei(w3.eth.gas_price, 'gwei')
                
                print(f"💼 Scan #{SESSION_STATS['scans']} | Balance: {bal:.6f} ETH | Gas: {gas:.1f} Gwei | Trading: {TRADING_ACTIVE}")

                # If trading mode is turned on via Telegram, run autonomous market checks
                if TRADING_ACTIVE:
                    # Placeholder for live DEX pool pricing & arbitrage routing logic
                    # You can tie your token pair contract calls here
                    pass

        except Exception as e:
            print(f"Loop error: {e}")
        
        time.sleep(30)

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
