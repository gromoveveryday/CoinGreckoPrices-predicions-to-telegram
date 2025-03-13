import pickle
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import telebot
import json
from pathlib import Path
from xgb import XGBRegressor


file_path = Path('data/crypto_data.pkl')

with open(file_path, 'rb') as f:
    loaded_data = pickle.load(f)

with open('config.json', 'r', encoding='utf-8') as file:
    config = json.load(file)

bot_token = config['bot_token']
bot = telebot.TeleBot(token = bot_token)
chat_id = config['chat_id']

for i in loaded_data.keys():
    loaded_data[i]['date'] = pd.to_datetime(loaded_data[i]['date'], dayfirst=True)
    loaded_data[i].set_index('date', inplace=True)

    lags = [1, 3, 5, 10, 15, 20, 30] 
    for lag in lags:
        loaded_data[i][f'lag_{lag}'] = loaded_data[i]['price'].shift(lag)
    
    loaded_data[i].dropna(inplace=True)
    
    X_train, y_train = loaded_data[i].drop(columns=['price']), loaded_data[i]['price']
   
    params = {
    'objective': 'reg:squarederror',  # Функция потерь для регрессии
    'n_estimators': 200, # Количество деревьев
    'max_depth': 5,  # Максимальная глубина дерева
    'learning_rate': 0.05, # Скорость обучения
    'subsample': 0.8, # Доля строк для обучения каждого дерева
    'colsample_bytree': 0.8, # Доля признаков для обучения каждого дерева
    'reg_alpha': 0.1, # L1 регуляризация
    'reg_lambda': 1.0, # L2 регуляризация
    'min_child_weight': 1, # Минимальная сумма весов в листе
    'gamma': 0, # Минимальное снижение потерь для разделения
    'random_state': 42 # Для воспроизводимости
}
    model = XGBRegressor(**params)
    
    model.fit(X_train, y_train)

    future_predictions = []
    current_features = X_train.iloc[-1].values.copy()

    for _ in range(30):
        next_value = model.predict(current_features.reshape(1, -1))[0]
        future_predictions.append(next_value)

        # Обновляем лаговые признаки
        current_features = np.roll(current_features, -1)
        current_features[-1] = next_value
    
    future_dates = pd.date_range(start=loaded_data[i].index[-1] + pd.Timedelta(days=1), periods=30, freq='D')

    crypto_name = str(i)
    plt.figure(figsize=(15, 10))
    plt.plot(X_train.index[-30:], y_train[-30:], label='Фактические значения, $USD')
    plt.plot(future_dates, future_predictions, label='Предсказанные значения на 30 дней вперед, $USD', linestyle='--')
    plt.legend()
    plt.title('Предсказание на 30 дней по криптовалюте: ' + i)
    plt.savefig('plot.png')

    message = 'Текущая стоимость за единицу ' + crypto_name + ', $USD: ' + str(loaded_data[i]['price'][-1]) 
    bot.send_message(chat_id, message)
    with open('plot.png', 'rb') as plot_file:
        bot.send_photo(chat_id, plot_file)