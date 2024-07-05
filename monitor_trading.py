import json
import time
import logging
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import yaml
from binance.websocket.um_futures.websocket_client import UMFuturesWebsocketClient
from threading import Thread

# Função para configurar o logging
def config_logging():
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger()
    return logger

# Carregar configuração do arquivo YAML
def load_config(config_path='config.yaml'):
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    return config

# Handler de mensagens do WebSocket
def message_handler(_, message):
    global df, new_data
    message = json.loads(message)
    #print(message)
    if 'k' in message:
        kline = message['k']
        
        if kline['x']:
            print(kline['x'], type(kline['x']))
            # Candle fechado
            new_row = {
                'time': pd.to_datetime(kline['t'], unit='ms'),
                'open': float(kline['o']),
                'high': float(kline['h']),
                'low': float(kline['l']),
                'close': float(kline['c']),
                'volume': float(kline['v'])
            }
            df = pd.concat([df, pd.DataFrame([new_row])], axis=0, ignore_index=True) # df.append(new_row, ignore_index=True)
            df = df.drop_duplicates(subset='time', keep='last')
            df.sort_values(by='time', inplace=True)
            df.reset_index(drop=True, inplace=True)
            new_data = True
        else:
            # Candle ainda não fechado
            if not df.empty and df.iloc[-1]['time'] <= pd.to_datetime(kline['t'], unit='ms'):
                df.at[len(df)-1, 'high'] = max(df.iloc[-1]['high'], float(kline['h']))
                df.at[len(df)-1, 'low'] = min(df.iloc[-1]['low'], float(kline['l']))
                df.at[len(df)-1, 'close'] = float(kline['c'])
                df.at[len(df)-1, 'volume'] += float(kline['v'])
                new_data = True
    print(df.tail(1))
# Configurar o cliente WebSocket
def start_websocket(symbol, interval):
    client = UMFuturesWebsocketClient(on_message=message_handler)
    client.continuous_kline(
        pair=symbol,
        id=1,
        contractType="perpetual",
        interval=interval,
    )
    return client

# Configurar a interface Streamlit
def create_interface():
    st.set_page_config(layout='wide')
    st.title("Monitor de Trading em Tempo Real")

    fig = go.Figure()
    fig.update_layout(
        xaxis_rangeslider_visible=False,
        title="Gráfico de Candlestick",
        xaxis_title="Tempo",
        yaxis_title="Preço"
    )

    placeholder = st.empty()

    return fig, placeholder

# Atualizar a interface Streamlit
def update_interface(fig, placeholder):
    fig.data = []
    fig.add_trace(go.Candlestick(
        x=df['time'],
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        name='Candlestick'
    ))

    placeholder.plotly_chart(fig, use_container_width=True)

# Função principal do Streamlit
def main():
    global df, new_data
    new_data = False
    df = pd.DataFrame(columns=['time', 'open', 'high', 'low', 'close', 'volume'])

    config = load_config()
    symbol = config['symbol']
    interval = config['real_time_interval']

    fig, placeholder = create_interface()

    ws_thread = Thread(target=start_websocket, args=(symbol, interval))
    ws_thread.daemon = True
    ws_thread.start()

    while True:
        if new_data:
            update_interface(fig, placeholder)
            new_data = False
        time.sleep(1)

if __name__ == "__main__":
    main()
