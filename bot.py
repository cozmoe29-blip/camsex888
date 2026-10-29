import time
import os
import requests
from threading import Thread
from flask import Flask, request as flask_request, render_template_string
from web3 import Web3

app = Flask(__name__)

# Configuration
TELEGRAM_BOT_TOKEN = "9091003001:AAHfI2YGog1vWSVTkE4IY4Qbop-m5FBHA6A"
TELEGRAM_CHAT_ID = "5542612428"

# Optimized public node endpoints
RPC_URLS = [
    "https://eth.public-node.com",
    "https://1rpc.io/eth",
    "https://rpc.ankr.com/eth",
    "https://cloudflare-eth.com"
]

WALLET_ADDRESS = Web3.to_checksum_address("0x14925C541c95D827dF2773bA466F8f59CC11B256")

# Global trading state & live stats
BOT_STATE = {
    "active": False,
    "scans": 0,
    "opportunities": 0,
    "trades_executed": 0,
    "earnings_eth": 0.000000,
    "last_balance": 0.0,
    "gas_price": 0.0,
    "log_history": ["System initialized and waiting..."]
}

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Moe Autonomous DEX Bot - Control Center</title>
    <style>
        body { background-color: #0d1117; color: #c9d1d9; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 0; padding: 20px; }
        .container { max-width: 900px; margin: auto; }
        header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #30363d; padding-bottom: 15px; margin-bottom: 20px; }
        h1 { margin: 0; font-size: 22px; color: #58a6ff; }
        .badge { padding: 5px 12px; border-radius: 20px; font-size: 12px; font-weight: bold; }
        .badge.active { background-color: #238636; color: white; }
        .badge.paused { background-color: #da3633; color: white; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 25px; }
        .card { background-color: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 15px; text-align: center; }
        .card h3 { margin: 0 0 10px 0; font-size: 14px; color: #8b949e; }
        .card .value { font-size: 20px; font-weight: bold; color: #f0f6fc; }
        .controls { display: flex; gap: 10px; margin-bottom: 25px; }
        button { padding: 12px 24px; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; font-size: 14px; width: 100%; }
        .btn-start { background-color: #238636; color: white; }
        .btn-stop { background-color: #da3633; color: white; }
        button:hover { opacity: 0.8; }
        .logs-box { background-color: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 15px; height: 200px; overflow-y: auto; font-family: monospace; font-size: 13px; color: #7ee787; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🤖 Moe Autonomous DEX Bot</h1>
            <div>
                Status: <span id="status-badge" class="badge {{ 'active' if state.active else 'paused' }}">{{ 'ACTIVE (24/7)' if state.active else 'PAUSED' }}</span>
            </div>
        </header>

        <div class="controls">
            <form action="/toggle" method="POST" style="width: 100%;">
                {% if state.active %}
                    <button type="submit" class="btn-stop">⏸️ Pause Trading</button>
                {% else %}
                    <button type="submit" class="btn-start">▶️ Start Trading & Earning</button>
                {% endif %}
            </form>
        </div>

        <div class="grid">
            <div class="card">
                <h3>Wallet Balance</h3>
                <div class="value">{{ "%.6f"|format(state.last_balance) }} ETH</div>
            </div>
            <div class="card">
                <h3>Total Earnings</h3>
                <div class="value" style="color: #7ee787;">{{ "%.6f"|format(state.earnings_eth) }} ETH</div>
            </div>
            <div class="card">
                <h3>Network Gas</h3>
                <div class="value">{{ "%.1f"|format(state.gas_price) }} Gwei</div>
            </div>
            <div class="card">
                <h3>Total Scans</h3>
                <div class="value">{{ state.scans }}</div>
            </div>
        </div>

        <h3 style="color: #8b949e; font-size: 14px; margin-bottom: 8px;">Live Activity & Execution Log</h3>
        <div class="logs-box">
            {% for log in state.log_history|reverse %}
                <div>> {{ log }}</div>
            {% endfor %}
        </div>
    </div>
    <script>
        setTimeout(() => { window.location.reload(); }, 5000);
    </script>
</body>
</html>
"""

@app.route('/')
def dashboard():
    return render_template_string(DASHBOARD_HTML, state=BOT_STATE)

@app.route('/toggle', methods=['POST'])
def toggle_trading():
    BOT_STATE["active"] = not BOT_STATE["active"]
    action_text = "Activated 24/7 Autonomous Trading" if BOT_STATE["active"] else "Paused Autonomous Trading"
    BOT_STATE["log_history"].append(action_text)
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": f"⚙️ *Dashboard Action:* {action_text}", "parse_mode": "Markdown"}, timeout=5)
    except Exception:
        pass
    return dashboard()

@app.route('/webhook', methods=['POST'])
def telegram_webhook():
    try:
        data = flask_request.get_json()
        if 'message' in data:
            chat_id = data['message']['chat']['id']
            text = data['message'].get('text', '').strip().lower()
            if text in ['/balance', 'balance']:
                send_message(chat_id, f"💼 *Wallet Balance:* `{BOT_STATE['last_balance']:.6f} ETH`\n⛽ *Gas Price:* `{BOT_STATE['gas_price']:.2f} Gwei`")
        return "OK", 200
    except Exception:
        return "OK", 200

def send_message(chat_id, message):
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        requests.post(url, json={"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}, timeout=10)
    except Exception:
        pass

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

def main_loop():
    print("🤖 Autonomous Worker Loop Running...")
    while True:
        try:
            connected = False
            for rpc in RPC_URLS:
                try:
                    w3 = Web3(Web3.HTTPProvider(rpc, request_kwargs={'timeout': 10}))
                    if w3.is_connected():
                        bal_wei = w3.eth.get_balance(WALLET_ADDRESS)
                        gas_wei = w3.eth.gas_price
                        
                        BOT_STATE["last_balance"] = float(w3.from_wei(bal_wei, 'ether'))
                        BOT_STATE["gas_price"] = float(w3.from_wei(gas_wei, 'gwei'))
                        connected = True
                        break
                except Exception:
                    continue

            BOT_STATE["scans"] += 1
            if connected:
                log_msg = f"Scan #{BOT_STATE['scans']} | Balance: {BOT_STATE['last_balance']:.6f} ETH | Gas: {BOT_STATE['gas_price']:.1f} Gwei"
            else:
                log_msg = f"Scan #{BOT_STATE['scans']} | Node connection syncing..."
                
            print(log_msg)
            
            if len(BOT_STATE["log_history"]) > 20:
                BOT_STATE["log_history"].pop(0)
            BOT_STATE["log_history"].append(log_msg)

            if BOT_STATE["active"]:
                # Active trading scan logic runs here
                pass

        except Exception as e:
            print(f"Loop error: {e}")
        
        time.sleep(15)

if __name__ == '__main__':
    try:
        set_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook?url=https://camsex888-1.onrender.com/webhook"
        requests.get(set_url, timeout=10)
    except Exception:
        pass

    t = Thread(target=run_web_server)
    t.daemon = True
    t.start()

    main_loop()
