from pymongo import MongoClient
import pandas as pd

# Підключення
uri = "mongodb://admin:secret_pass@localhost:27017/"
client = MongoClient(uri)
db = client["taxi_db"]
trips_col = db["trips"]
report_col = db["spatial_stats"]

def run_spatial_analytics():
    print("📍 Запуск просторового аналізу районів...")

    pipeline = [
    # ЕТАП 1: Фільтруємо "сміття"
    { 
        "$match": { 
            "PULocationID": { "$exists": True, "$gt": 0 },
            "fare_amount": { "$gt": 5 },      # Ігноруємо поїздки дешевше $5
            "trip_distance": { "$gt": 0.5 }   # Ігноруємо поїздки менше 800 метрів
        } 
    },
    {
        "$group": {
            # Групуємо тепер за двома полями
            "_id": {
                "LocationID": "$PULocationID",
                "payment_type": "$payment_type"
            },
            "total_trips": { "$sum": 1 },
            "avg_fare": { "$avg": "$fare_amount" },
            "avg_tip": { "$avg": "$tip_amount" }
        }
    },
    {
        "$project": {
            "_id": 0,
            "LocationID": "$_id.LocationID",
            "payment_type": "$_id.payment_type",
            "TripCount": "$total_trips",
            "AvgFare": { "$round": ["$avg_fare", 2] },
            "AvgTip": { "$round": ["$avg_tip", 2] }
        }
    }
]

    results = list(trips_col.aggregate(pipeline))

    if results:
        # Зберігаємо результат
        report_col.delete_many({})
        report_col.insert_many(results)
        
        # Вивід таблиці
        df = pd.DataFrame(results)
        print("\n🗽 ТОП-10 РАЙОНІВ ЗА КІЛЬКІСТЮ ПОСАДОК:")
        print(df.to_string(index=False))
        
        print(f"\n✅ Дані збережено в: {report_col.name}")
    else:
        print("⚠️ Дані для просторового аналізу не знайдені.")

if __name__ == "__main__":
    run_spatial_analytics()