from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    response = requests.post(url, json=payload)
    return response.json()

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data received"}), 400

    # TradingView envía el mensaje como texto plano o JSON
    alert_message = data.get("message", str(data))
    ticker         = data.get("ticker", "")
    price          = data.get("price", "")
    alert_type     = data.get("type", "")

    # Formateamos el mensaje según el tipo de alerta
    if "LONG" in alert_message.upper() or alert_type == "LONG":
        emoji = "🟢"
    elif "SHORT" in alert_message.upper() or alert_type == "SHORT":
        emoji = "🔴"
    elif "HIGH" in alert_message.upper():
        emoji = "⚠️"
    elif "LOW" in alert_message.upper():
        emoji = "⚠️"
    else:
        emoji = "📊"

    mensaje = f"{emoji} <b>Alerta TradingView</b>\n\n{alert_message}"
    if ticker:
        mensaje += f"\n\n<b>Símbolo:</b> {ticker}"
    if price:
        mensaje += f"\n<b>Precio:</b> {price}"

    result = send_telegram(mensaje)
    return jsonify({"status": "ok", "telegram": result})

@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "Bot activo ✅"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
