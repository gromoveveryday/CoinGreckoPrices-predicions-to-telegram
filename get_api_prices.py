import os 
import pickle
import pandas as pd
from pycoingecko import CoinGeckoAPI

cg = CoinGeckoAPI() # Настройка обращения к API

cryptocurrencies = { # Словарь основных криптовалют
    'bitcoin': 'BTC',
    'ethereum': 'ETH',
    'binancecoin': 'BNB',
    'ripple': 'XRP',
    'cardano': 'ADA',
    'solana': 'SOL',
    'dogecoin': 'DOGE',
    'polkadot': 'DOT',
    'litecoin': 'LTC',
    'chainlink': 'LINK'
} 

def get_historical_data(crypto_id): # Делает попытку загрузки цен на криптовалюту и сохраняем их как датафрейм
    try:
        data = cg.get_coin_market_chart_by_id(id=crypto_id, vs_currency='usd', days=364) # От 365 дней дял платного API
        prices = data['prices']  
        df = pd.DataFrame(prices, columns=['timestamp', 'price'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df['date'] = df['timestamp'].dt.date       
        df = df[['date', 'price']]
        
        return df
    except Exception as e:
        print(f"Ошибка при загрузке данных для {crypto_id}: {e}")
        return None
    
all_data = {} # Словарь для загрузки в него датафреймов по ключу - названию криптовалюты
for crypto_id, symbol in cryptocurrencies.items():
    print(f"Загружаем данные для {symbol} ({crypto_id})...")
    data = get_historical_data(crypto_id)
    if data is not None:
        all_data[symbol] = data

save_directory = 'data' # При повторной активации - сохраняет словарь с новыми данными в папку data
if not os.path.exists(save_directory):
    os.makedirs(save_directory)

file_path = os.path.join(save_directory, 'crypto_data.pkl') 

with open(file_path, 'wb') as f: # Чтобы не потерять информацию по фреймах - сохраняем в формате пикл
    pickle.dump(all_data, f)

print(f"Файл сохранен по пути: {file_path}")