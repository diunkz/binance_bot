from binance.client import Client
import pandas as pd
import numpy as np
import time
import pendulum
import os
import logging
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

env_path = Path(__file__).parent / 'env' / '.env'
log_dir = Path(__file__).parent / "logs" 
log_dir.mkdir(exist_ok=True)  # Cria a pasta "logs" se não existir
log_file = log_dir / "trading.log"

load_dotenv(dotenv_path=env_path)

# Configuração do logger
logging.basicConfig(
    filename=log_file,  # Caminho correto para o log
    level=logging.INFO,  # Nível do log
    format="%(asctime)s - %(message)s",  # Formato da mensagem
    datefmt="%d-%m-%Y %H:%M",  # Formato da data no log
)

# # Exibir todas as colunas
# pd.set_option('display.max_columns', None)

# # Exibir todas as linhas
# pd.set_option('display.max_rows', None)

# Substitua pelas suas credenciais da Binance
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
TIMEZONE = os.getenv("TIMEZONE")

# client = Client(API_KEY, API_SECRET)
client = Client(API_KEY, API_SECRET, {"timeout": 3})  # Define timeout global


def get_last_n_candles_and_ma99(n, interval, symbol, timezone):
    try:
        # Obtendo os dados do cliente
        klines = client.get_klines(symbol=symbol, interval=interval, limit=n+99)
    except Exception as e:
        logging.error(f"Erro ao obter candles para {symbol}: {e}")
        return pd.DataFrame()  # Retorna um DataFrame vazio para evitar quebra

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
    
    # print('hora dentro da funcao', hour_now.hour)
    # print('minuto dentro da funcao', hour_now.minute)
    # print(indices_iguais)

    # Remover as linhas com hora e minuto iguais à hora atual
    df = df.drop(index=indices_iguais)

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

def process_symbol(symbol):
    try:
        df = get_last_n_candles_and_ma99(5, interval, symbol, TIMEZONE)
        if df.empty:
            logging.warning(f"DataFrame vazio para {symbol}, ignorando.")
            return
        symbols_dataframes[symbol] = df
        print(f"{symbol} atualizado!")
    except Exception as e:
        print('erro na função process_symbol: ', e)
        logging.error(f"Erro ao processar {symbol}: {e}\n")



def wait_seconds_until_the_next_minute(timezone):
    now = pendulum.now(timezone)
    seconds_to_next_minute = 60 - now.second
    print(f"Aguardando {seconds_to_next_minute} segundos para o próximo minuto...\n")
    time.sleep(seconds_to_next_minute)

# Função para registrar o preço no log
def log_entry_price(symbol, price):
    log_message = f"{symbol}: {price} - 💰 ENTRADA"
    logging.info(log_message)  # Escreve no arquivo de log
    print(log_message)  # Opcional: printa no terminal também

def log_win_price(symbol, price):
    log_message = f"{symbol}: {price} - ✅ WIN\n"  # Formato da mensagem

    logging.info(log_message)  # Escreve no arquivo de log
    print(log_message)

def log_loss_price(symbol, price):
    log_message = f"{symbol}: {price} - ❌ LOSS\n"  # Formato da mensagem

    logging.info(log_message)  # Escreve no arquivo de log
    print(log_message)

# Define o par de moedas e o intervalo (1m)
symbols = ["SUIUSDT", "DOTUSDT", "XRPUSDT", "ETHUSDT", "ADAUSDT"]
interval = Client.KLINE_INTERVAL_1MINUTE  # 1 minuto
symbols_dataframes = {}
waiting_trade = False

# normalizar o horário para atualizar no final de cada minuto

while True:
    try:
        wait_seconds_until_the_next_minute(TIMEZONE)
        print('Data Atual:', pendulum.now().format("DD-MM-YYYY - HH:mm"), end='\n\n')

        with ThreadPoolExecutor(max_workers=len(symbols)) as executor:
            executor.map(process_symbol, symbols)

        for x in symbols:
            print()
            print(x)
            print(symbols_dataframes[x])
            all_ok = symbols_dataframes[x]["green_above_MA99"].eq("ok").all()
            if all_ok:
                print(f'Possível entrada em {x}!')
                os.system("tput bel")
                try:
                    price = float(client.get_symbol_ticker(symbol=x)["price"])
                    win_price = price + (price * 0.008)
                    loss_price = price - (price * 0.002)
                    log_entry_price(x, price)
                    waiting_trade = True

                    while waiting_trade:
                        try:
                            price = float(client.get_symbol_ticker(symbol=x)["price"])  # Tenta obter o preço
                            if price >= win_price:
                                log_win_price(x, price)
                                waiting_trade = False
                            elif price <= loss_price:
                                log_loss_price(x, price)
                                waiting_trade = False

                            print(f"Preço de {x}: {price}")
                            print(f"Meta de win: {win_price}")
                            print(f"Meta de loss: {loss_price}")
                            print()

                        except Exception as e:
                            logging.error(f"Erro ao obter preço de {x}: {e}")  # Log do erro
                            print(f"Erro ao obter preço de {x}, tentando novamente...")  
                            # time.sleep(1)  # Pequena pausa antes de tentar de novo para evitar muitas requisições seguida
                        # time.sleep(0.5)  # Intervalo normal entre requisições
                    os.system("tput bel")
                    # time.sleep(540) # esperando 9 min após um trade
                    break
                except Exception as e:
                    logging.error(f"Erro ao monitorar preço de {x}: {e}\n")
                    waiting_trade = False
            print()

    except Exception as e:
        logging.critical(f"Erro crítico no loop principal: {e}\n")
        time.sleep(10)  # Espera um pouco antes de tentar novamente


