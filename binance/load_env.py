import os
from dotenv import load_dotenv

load_dotenv(dotenv_path='../')

BINANCE_API_KEY = os.getenv('BINANCE_API_KEY')
BINANCE_SECRET_KEY = os.getenv('BINANCE_SECRET_KEY')
BINANCE_API_NAME = os.getenv('BINANCE_API_NAME')