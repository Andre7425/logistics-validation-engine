from pymongo import MongoClient

# 1. Підключення до бази (обов'язково!)
uri = "mongodb://admin:secret_pass@localhost:27017/"
client = MongoClient(uri)
db = client["taxi_db"]

def check_jfk_data():
    print("🔎 Аналіз реальних поїздок з JFK (ID 132):")
    
    # Шукаємо 10 поїздок, щоб побачити ширшу картину
    jfk_trips = list(db["trips"].find({"PULocationID": 132}).limit(10))
    
    if not jfk_trips:
        print("❌ Поїздок з JFK не знайдено. Перевірте, чи завантажені дані.")
        return

    for t in jfk_trips:
        fare = t.get('fare_amount', 0)
        dist = t.get('trip_distance', 0)
        tip = t.get('tip_amount', 0)
        total = t.get('total_amount', 0)
        
        print(f"Ціна: ${fare:<6} | Дистанція: {dist:<5} миль | Чайові: ${tip:<5} | Разом: ${total}")

if __name__ == "__main__":
    check_jfk_data()