from binance.client import Client
import pandas as pd
import numpy as np
import time
import pendulum

# # Exibir todas as colunas
# pd.set_option('display.max_columns', None)

# # Exibir todas as linhas
# pd.set_option('display.max_rows', None)

# Substitua pelas suas credenciais da Binance
API_KEY = ""
API_SECRET = ""

client = Client(API_KEY, API_SECRET)

def get_last_n_candles_and_ma99(n, interval, symbol, timezone):
    # Obtendo os dados do cliente
    klines = client.get_klines(symbol=symbol, interval=interval, limit=n+99)

    # Criando o dataframe
    df = pd.DataFrame(klines, columns=[
                "open_time", "open", "high", "low", "close", "volume", 
                "close_time", "quote_asset_volume", "number_of_trades", 
                "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume", "ignore"
            ])

    # Convertendo os tempos para o fuso horário correto
    df["open_time"] = pd.to_datetime(df["open_time"], unit="ms").dt.tz_localize("UTC").dt.tz_convert(timezone)
    df["close_time"] = pd.to_datetime(df["close_time"], unit="ms").dt.tz_localize("UTC").dt.tz_convert(timezone)
    
    # Convertendo as colunas open e close para float
    df["open"] = df["open"].astype(float)
    df["close"] = df["close"].astype(float)

    # Selecionando apenas as colunas necessárias
    df = df[['open_time', 'close_time', 'open', 'close']]
    
    # Calculando a média móvel de 99 períodos
    df["MA99"] = df["close"].rolling(window=99).mean().round(4)

    # Obter a hora e o minuto atual
    hour_now = pendulum.now(timezone)
    hour_and_minute = (hour_now.hour, hour_now.minute)

    # Encontrar os índices com a mesma hora e minuto
    indices_iguais = df[
                    (df["open_time"].dt.hour == hour_and_minute[0]) & 
                    (df["open_time"].dt.minute == hour_and_minute[1])
                    ].index
    
    # Remover as linhas com hora e minuto iguais à hora atual
    df.drop(index=indices_iguais, inplace=True)

    # Salve o DataFrame com os últimos N candles escolhidos
    df = df.tail(n).reset_index(drop=True)

    # Criando a nova coluna candle_color
    df["candle_color"] = df.apply(
            lambda row: 'green' if row['close'] > row['open'] else ('red' if row['close'] < row['open'] else 'doji'),
            axis=1
        )
    # Verificando os candles acima da MA99
    df["green_above_MA99"] = df.apply(
        lambda row: 'ok' if row['close'] > row['MA99'] and row['candle_color'] == 'green' else 'not ok', 
        axis=1
    )

    # Retornar as últimas n linhas com os índices resetados
    return df


# Define o par de moedas e o intervalo (1m)
symbol = "DOTUSDT"
interval = Client.KLINE_INTERVAL_1MINUTE  # 1 minuto
timezone = 'America/Manaus'


while True:
    now = pendulum.now("America/Manaus")
    
    # Ajuste para o próximo minuto
    seconds_to_next_minute = 60 - now.second
    print(f"Aguardando {seconds_to_next_minute} segundos para o próximo minuto...")
    time.sleep(seconds_to_next_minute)

    last_5_candles = get_last_n_candles_and_ma99(5, interval, symbol, timezone) # 5+99 to get MA(99) in the last 5

    print(last_5_candles)