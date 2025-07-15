
import ccxt
import pandas as pd
import requests
import smtplib
from email.mime.text import MIMEText
from ta.volatility import BollingerBands
from datetime import datetime

# --- Telegram config ---
TELEGRAM_TOKEN = '7472465800:AAFwaExCDSZE2_YzB2I9buvjxeQbKu9SA7Y'
TELEGRAM_CHAT_ID = '1977359498'

# --- Gmail config ---
EMAIL_SENDER = 'yusif.samedzade.1@gmail.com'
EMAIL_PASSWORD = 'ucdr pyuz sllk toit'
EMAIL_RECEIVER = 'yusif.samedzade.1@gmail.com'

# --- Binance Futures init ---
exchange = ccxt.binance({
    'enableRateLimit': True,
    'options': {
        'defaultType': 'future'
    }
})

# --- Telegram send ---
def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {'chat_id': TELEGRAM_CHAT_ID, 'text': message}
    requests.post(url, data=payload)

# --- Gmail send ---
def send_email(subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECEIVER
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)

# --- Check Bollinger %B ---
def check_bbands(symbol):
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe='1d', limit=21)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        indicator = BollingerBands(close=df['close'], window=20, window_dev=2)
        percent_b = indicator.bollinger_pband()
        last_pb = percent_b.iloc[-1]
        if last_pb <= 0.00:
            msg = f"🔻 {symbol} упал до нижней границы Bollinger %B = {last_pb:.2f}"
            send_telegram(msg)
            send_email(f"Bollinger Alert: {symbol}", msg)
    except Exception as e:
        print(f"Ошибка с {symbol}: {e}")

# --- Main loop ---
def main():
    print(f"Запуск в {datetime.now()}")
    markets = exchange.load_markets()
    symbols = [s for s in markets if '/USDT' in s and markets[s].get('contractType') == 'PERPETUAL']
    for symbol in symbols:
        check_bbands(symbol)

if __name__ == '__main__':
    main()
