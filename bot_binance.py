from binance.client import Client
import pandas as pd
import numpy as np
import time
import pendulum
import os
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).parent / 'env' / '.env'
print(f"Carregando o .env de: {env_path}")
load_dotenv(dotenv_path=env_path)

# Substitua pelas suas credenciais da Binance
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")

client = Client(API_KEY, API_SECRET)

# Define o par de moedas e o intervalo (1m)
symbol = "DOTUSDT"
interval = Client.KLINE_INTERVAL_1MINUTE  # 1 minuto

# Função para obter os preços de fechamento dos últimos 99 candles e calcular MA(99)
def get_last_99_candles_and_ma(symbol, interval):
    try:
        # Obtém os últimos 104 candles para garantir a MA(99) completa nos últimos 99
        klines = client.get_klines(symbol=symbol, interval=interval, limit=104)

        # Criar DataFrame com as informações necessárias
        df = pd.DataFrame(klines, columns=[
            "open_time", "open", "high", "low", "close", "volume", 
            "close_time", "quote_asset_volume", "number_of_trades", 
            "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume", "ignore"
        ])
        
        df["open_time"] = pd.to_datetime(df["open_time"], unit="ms").dt.tz_localize("UTC").dt.tz_convert("America/Manaus")
        df["close_time"] = pd.to_datetime(df["close_time"], unit="ms").dt.tz_localize("UTC").dt.tz_convert("America/Manaus")
        df["open"] = df["open"].astype(float)
        df["close"] = df["close"].astype(float)

        # Calcular MA(99)
        df["MA99"] = df["close"].rolling(window=99).mean()

        # Pegamos apenas os últimos 99 candles para exibição
        df = df.iloc[-5:]

        candles = []
        for i in range(len(df)):
            open_time = df.iloc[i]["open_time"].strftime('%Y-%m-%d %H:%M:%S')
            close_time = df.iloc[i]["close_time"].strftime('%Y-%m-%d %H:%M:%S')
            open_price = df.iloc[i]["open"]
            close_price = df.iloc[i]["close"]
            ma99 = df.iloc[i]["MA99"]

            # Definir a cor do candle
            color = "🟩 Verde" if close_price > open_price else "🟥 Vermelho"

            # Se a MA(99) for NaN, exibir "N/A"
            ma99_str = f"{ma99:.4f} USDT" if not np.isnan(ma99) else "N/A"

            # Condição para adicionar um ✅ somente nos candles verdes onde o fechamento é maior que a MA99
            check = " ✅" if color == "🟩 Verde" and close_price > ma99 else ""

            candles.append({
                "open_time": open_time,
                "close_time": close_time,
                "open_price": open_price,
                "close_price": close_price,
                "color": color,
                "MA99": ma99_str,
                "check": check
            })
        
        return candles
    
    except Exception as e:
        print(f"Erro ao buscar dados para {symbol}: {e}")
        return []

# Loop para rodar exatamente no início de cada minuto
while True:
    now = pendulum.now("America/Manaus")
    
    # Ajuste para o próximo minuto
    seconds_to_next_minute = 60 - now.second
    print(f"Aguardando {seconds_to_next_minute} segundos para o próximo minuto...")
    time.sleep(seconds_to_next_minute)

    # Executa a função no começo do minuto
    candles = get_last_99_candles_and_ma(symbol, interval)

    # Exibindo os resultados
    if candles:
        print("\n📊 Últimos 99 candles com MA(99):")
        for candle in candles:
            print(f"  🕒 {candle['open_time']} - Abertura: {candle['open_price']} USDT, Fechamento: {candle['close_price']} USDT, Cor: {candle['color']}, MA(99): {candle['MA99']}{candle['check']}")
    else:
        print("Não foi possível obter os candles.")