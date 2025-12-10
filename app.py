
from flask import Flask, request, render_template, redirect, url_for
import os, threading, time, json
from scraper import search_della_ati

app = Flask(__name__)

# Телеграм токен: положите в переменную окружения TELEGRAM_BOT_TOKEN
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")

@app.route("/")
def index():
    return render_template("index.html", results=[])

@app.route("/search", methods=["POST"])
def search():
    query = request.form.get("query","")
    # Вызываем парсер (он вернёт список словарей)
    results = search_della_ati(query)
    return render_template("index.html", results=results, query=query)

# Простой webhook для телеграм (можно использовать polling, но для простоты webhook)
@app.route("/telegram_webhook", methods=["POST"])
def telegram_webhook():
    data = request.json
    # Здесь простая логика: если пришла команда /search, запускаем поиск
    if "message" in data and "text" in data["message"]:
        text = data["message"]["text"]
        chat_id = data["message"]["chat"]["id"]
        if text.startswith("/search"):
            query = text[len("/search"):].strip()
            if not query:
                send_telegram_message(chat_id, "Напишите: /search Город1-Город2")
            else:
                results = search_della_ati(query)
                msg = format_results_text(results)
                send_telegram_message(chat_id, msg)
    return {"ok": True}

def send_telegram_message(chat_id, text):
    token = TELEGRAM_BOT_TOKEN
    if not token:
        print("No TELEGRAM_BOT_TOKEN set")
        return
    import requests
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text})

def format_results_text(results):
    if not results:
        return "Ничего не найдено."
    lines = []
    for r in results[:10]:
        lines.append(f'{r.get("title","")} \\n{r.get("link","")}')
    return "\\n\\n".join(lines)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)
