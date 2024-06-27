from load_env import BINANCE_API_NAME, BINANCE_API_KEY, BINANCE_SECRET_KEY

import httpx
from datetime import datetime, timedelta
import pandas as pd

class BinanceFuturesAPI:
    BASE_URL = "https://fapi.binance.com"
    
    def __init__(self):
        self.client = httpx.Client(base_url=self.BASE_URL)
    
    def _build_endpoint(self, symbol: str, interval: str, limit: int) -> str:
        return f"/fapi/v1/klines?symbol={symbol}&interval={interval}&limit={limit}"
    
    def get_market_data(self, symbol: str, interval: str, limit: int):
        endpoint = self._build_endpoint(symbol, interval, limit)
        response = self.client.get(endpoint)
        response.raise_for_status()  # Will raise an error for bad responses
        return response.json()

    def get_last_24h_data(self, symbol: str):
        interval = "1m"
        limit = 1440  # 1440 minutes in 24 hours
        data = self.get_market_data(symbol, interval, limit)
        return self._parse_market_data(data)
    
    def _parse_market_data(self, data):
        parsed_data = []
        for entry in data:
            parsed_entry = {
                "Date": datetime.fromtimestamp(entry[0] / 1000),
                "open": float(entry[1]),
                "high": float(entry[2]),
                "low": float(entry[3]),
                "close": float(entry[4]),
                "volume": float(entry[5])
            }
            parsed_data.append(parsed_entry)
        return parsed_data
    
    def close(self):
        self.client.close()

# Uso da classe
if __name__ == "__main__":
    symbol = "ADAUSDT"
    api = BinanceFuturesAPI()
    
    try:
        market_data = api.get_last_24h_data(symbol)
        df = pd.DataFrame(market_data)
        df.set_index(df['Date'], inplace=True)
        df.drop('Date', axis=1, inplace=True)
        print(df.head())
        print(df.shape)
        
    finally:
        api.close()


