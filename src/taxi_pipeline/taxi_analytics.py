from pymongo import MongoClient
import pandas as pd

# Підключення до нашої професійної бази
uri = "mongodb://admin:secret_pass@localhost:27017/"
client = MongoClient(uri)
db = client["taxi_db"]
trips_col = db["trips"]
report_col = db["rate_code_stats"]

def run_taxi_pipeline():
    print("📊 Починаємо аналіз тарифів таксі...")

    pipeline = [
        # Етап 1: Фільтруємо сміття (дистанція > 0 і ціна > 0)
        {
            "$match": {
                "trip_distance": { "$gt": 0 },
                "fare_amount": { "$gt": 0 }
            }
        },
        # Етап 2: Групуємо за RatecodeID
        {
            "$group": {
                "_id": "$RatecodeID",
                "avg_fare": { "$avg": "$fare_amount" },
                "avg_distance": { "$avg": "$trip_distance" },
                "trip_count": { "$sum": 1 }
            }
        },
        # Етап 3: Гарне оформлення
        {
            "$project": {
                "_id": 0,
                "RateCode": "$_id",
                "AverageFare": { "$round": ["$avg_fare", 2] },
                "AverageDistance": { "$round": ["$avg_distance", 2] },
                "TotalTrips": "$trip_count"
            }
        },
        # Етап 4: Сортування за прибутковістю
        { "$sort": { "AverageFare": -1 } }
    ]

    # Виконуємо запит
    results = list(trips_col.aggregate(pipeline))

    if results:
        # Зберігаємо результат у нову колекцію для дашборду
        report_col.delete_many({})
        report_col.insert_many(results)
        
        # Виводимо гарну таблицю в термінал через Pandas
        print("\n📈 ЗВІТ ПО ТАРИФАХ:")
        print(pd.DataFrame(results))
        print(f"\n✅ Звіт збережено в колекцію: {report_col.name}")
    else:
        print("❓ Дані в taxi_db.trips не знайдені. Спершу запусти to_mongodb.py")

if __name__ == "__main__":
    run_taxi_pipeline()