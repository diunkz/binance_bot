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
import os

env_path = Path(__file__).parent / 'env' / '.env'
log_dir = Path(__file__).parent / "logs" 
log_dir.mkdir(exist_ok=True)  # Cria a pasta "logs" se não existir
log_file = log_dir / "trading.log"

load_dotenv(dotenv_path=env_path)

# Substitua pelas suas credenciais da Binance
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
TIMEZONE = os.getenv("TIMEZONE")

client = Client(API_KEY, API_SECRET)

# Configuração do logger
logging.basicConfig(
    filename=log_file,  # Caminho correto para o log
    level=logging.INFO,  # Nível do log
    format="%(asctime)s - %(message)s",  # Formato da mensagem
    # datefmt="%d-%m-%Y %H:%M",  # Formato da data no log
)

# Função para registrar o preço no log
def log_entry_price(timezone, symbol, price):
    hour_now = pendulum.now(timezone).format("DD-MM-YYYY - HH:mm")
    log_message = f"{hour_now} - ENTRY - {symbol}: {price}"
    logging.info(log_message)  # Escreve no arquivo de log
    print(log_message)  # Opcional: printa no terminal também


# price = float(client.get_symbol_ticker(symbol='SUIUSDT')["price"])  # Obter preço atual
# log_entry_price(TIMEZONE, 'SUIUSDT', price)
# print(price)
# print(type(price))
# win_price = price+(price*0.005)
# print(win_price)

os.system("tput bel")

