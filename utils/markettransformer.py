import pandas as pd
import numpy as np

class MarketDataTransformer:
    def __init__(self, data: pd.DataFrame):
        self.data = data
    
    def calculate_rsi(self, period: int = 14):
        delta = self.data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        self.data['RSI'] = 100 - (100 / (1 + rs))
        return self
    
    def calculate_ema(self, column: str, period: int):
        self.data[f'EMA_{period}_{column}'] = self.data[column].ewm(span=period, adjust=False).mean()
        return self
    
    def add_rsi_ema(self, period: int):
        self.calculate_ema('RSI', period)
        return self
    
    def add_price_ema(self, period: int):
        self.calculate_ema('close', period)
        return self
    
    def calculate_differences(self):
        self.data['Diff_EMA_RSI'] = self.data['EMA_9_RSI'] - self.data['EMA_21_RSI']
        self.data['Diff_EMA_Close'] = self.data['EMA_9_close'] - self.data['EMA_21_close']
        return self
    
    def transform(self):
        # Calcular RSI
        self.calculate_rsi()
        
        # Calcular EMA de 9 e 21 períodos para close
        self.add_price_ema(9)
        self.add_price_ema(21)
        
        # Calcular EMA de 9 e 21 períodos para RSI
        self.calculate_ema('RSI', 9)
        self.calculate_ema('RSI', 21)
        
        # Calcular diferenças
        self.calculate_differences()
        
        return self.data

# Função para converter dados de lista para DataFrame
def list_to_dataframe(data: list):
    df = pd.DataFrame(data)
    df.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
    return df

# Uso da classe
if __name__ == "__main__":
    # Suponha que market_data seja uma lista de dicionários com os dados de mercado
    market_data = [
        # Adicione seus dados aqui
    ]
    
    # Converta a lista de dados para DataFrame
    df = list_to_dataframe(market_data)
    
    # Instancie a classe e transforme os dados
    transformer = MarketDataTransformer(df)
    transformed_data = transformer.transform()
    
    # Mostre os dados transformados
    print(transformed_data)
