import pandas as pd
from pymongo import MongoClient
import os

# 1. Підключення
# Використовуй порт 27017, як ми налаштували в Docker
uri = "mongodb://admin:secret_pass@localhost:27017/"
client = MongoClient(uri)

# ОСЬ ТУТ МИ ЗМІНЮЄМО НАЗВУ БАЗИ
db = client["taxi_db"] 
collection = db["trips"]

def load_taxi_data():
   
# Отримуємо шлях до папки, де лежить ЦЕЙ скрипт (src/taxi_pipeline/)
    base_dir = os.path.dirname(os.path.abspath(__file__))

# Піднімаємося на два рівні вгору до кореня проєкту і йдемо в data/
    path = os.path.join(base_dir, "../../data/processed/clean_trips.parquet")
    
    print("📦 Завантаження даних з Parquet...")
    df = pd.read_parquet(path).head(100000) # Беремо 100000 рядків для тесту

    # Перетворюємо DataFrame у список словників для MongoDB
    data_dict = df.to_dict("records")
    
    print(f"🚀 Записуємо {len(data_dict)} записів у базу taxi_db...")
    collection.delete_many({}) # Очищуємо перед завантаженням
    collection.insert_many(data_dict)
    
    print("✅ Дані таксі успішно завантажені в MongoDB!")

if __name__ == "__main__":
    load_taxi_data()