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
load_dotenv(dotenv_path=env_path)

# Substitua pelas suas credenciais da Binance
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
TIMEZONE = os.getenv("TIMEZONE")

# client = Client(API_KEY, API_SECRET)
client = Client(API_KEY, API_SECRET, {"timeout": 3})  # Define timeout global

def get_balance(symbol):
    balance = client.get_asset_balance(asset=symbol)  # Consulta saldo de USDT
    return float(balance["free"])  # Retorna apenas o saldo disponível

usdt_balance = get_balance('USDT')
print(f"Saldo disponível em USDT: {usdt_balance:.2f}")

balance = client.get_asset_balance(asset='USDT')  # Consulta saldo de USDT
print(balance)