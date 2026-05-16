import pandas as pd
from pymongo import MongoClient
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import joblib

# 1. Підключення та вибірка даних
client = MongoClient("mongodb://admin:secret_pass@localhost:27017/")
db = client["taxi_db"]

# ... (підключення залишається таким самим) ...

print("📥 Завантаження даних з дистанцією...")
# Додаємо trip_distance у список полів {..., "trip_distance": 1}
cursor = db["trips"].find(
    {"fare_amount": {"$gt": 5}, "trip_distance": {"$gt": 0.5}},
    {"PULocationID": 1, "tpep_pickup_datetime": 1, "trip_distance": 1, "fare_amount": 1, "_id": 0}
).limit(100000) # Можна збільшити до 100к для кращої точності

df = pd.DataFrame(list(cursor))

if not df.empty:
    df['hour'] = pd.to_datetime(df['tpep_pickup_datetime']).dt.hour
    
    # 2. ОНОВЛЮЄМО НАБІР ОЗНАК (X)
    # Тепер у нас три колонки для навчання
    X = df[['PULocationID', 'hour', 'trip_distance']]
    y = df['fare_amount']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    print("🤖 Навчання покращеної моделі (Distance-aware)...")
    model = RandomForestRegressor(n_estimators=100, max_depth=12, random_state=42)
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    mae = mean_absolute_error(y_test, predictions)
    print(f"✅ Модель оновлена! Нова MAE: ${mae:.2f}") # Очікуємо зниження помилки!

    joblib.dump(model, "taxi_model.joblib")