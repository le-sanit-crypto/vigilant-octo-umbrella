import requests

def send_web_notification(title, message, url=None):
    # For demo: just print, but here you could integrate a real web API (Pushbullet, IFTTT Webhook, etc.)
    payload = {
        "title": title,
        "message": message,
    }
    if url:
        payload["url"] = url
    print(f"Web notification: {payload}")
    # requests.post("https://my-webhook-service/api/notify", json=payload)

def notify_trade(symbol, side, price):
    send_web_notification("Trade executed", f"{side} {symbol} at {price}")

def notify_alert(message):
    send_web_notification("Alert", message)