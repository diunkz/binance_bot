import os
import time
import pandas as pd
import pendulum
from dotenv import load_dotenv
from binance.client import Client

# Carrega as variáveis de ambiente
load_dotenv()
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
TIMEZONE = os.getenv("TIMEZONE", "America/Manaus")

client = Client(
    API_KEY,
    API_SECRET,
    requests_params={"timeout": 15}  # aumenta o tempo de espera pra 15 segundos
)

def fetch_sma_data(symbol, interval="1m", limit=200, retries=3, delay=5):
    for attempt in range(retries):
        try:
            klines = client.get_klines(symbol=symbol, interval=interval, limit=limit)
            df = pd.DataFrame(klines, columns=[
                "open_time", "open", "high", "low", "close", "volume",
                "close_time", "quote_asset_volume", "number_of_trades",
                "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume", "ignore"
            ])
            df["close"] = df["close"].astype(float)
            df["SMA50"] = df["close"].rolling(window=50).mean()
            df["SMA200"] = df["close"].rolling(window=200).mean()
            return df[["close", "SMA50", "SMA200"]]
        
        except Exception as e:
            print(f"Tentativa {attempt + 1} de {retries} falhou: {e}")
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                raise  # Estoura o erro se todas as tentativas falharem


def check_cross(df):
    last = df.iloc[-1]
    prev = df.iloc[-2]

    if prev["SMA50"] < prev["SMA200"] and last["SMA50"] > last["SMA200"]:
        return "Cruzamento de ALTA"
    elif prev["SMA50"] > prev["SMA200"] and last["SMA50"] < last["SMA200"]:
        return "Cruzamento de BAIXA"
    return None

def wait_seconds_until_the_next_minute(timezone):
    now = pendulum.now(timezone)
    seconds_to_next_minute = 60 - now.second
    print(f"Aguardando {seconds_to_next_minute} segundos para o próximo minuto...\n")
    time.sleep(seconds_to_next_minute)

symbol = "SUIUSDT"

while True:
    wait_seconds_until_the_next_minute(TIMEZONE)

    df = fetch_sma_data(symbol)
    result = check_cross(df)

    if result:
        now = pendulum.now(TIMEZONE).format("YYYY-MM-DD HH:mm")
        print(f"{now} - {result} detectado!")
