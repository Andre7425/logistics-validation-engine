from pymongo import MongoClient
import pandas as pd

# 1. Підключення
uri = "mongodb://admin:secret_pass@localhost:27017/"
client = MongoClient(uri)
db = client["taxi_db"]
trips_col = db["trips"]
report_col = db["hourly_stats"]

def run_time_analytics():
    print("🕒 Запуск розширеного часового аналізу (з типами оплати)...")

    pipeline = [
        # Етап 1: Очищення даних
        {
            "$match": {
                "fare_amount": { "$gt": 0, "$lt": 500 },
                "tpep_pickup_datetime": { "$exists": True }
            }
        },
        # Етап 2: Витягуємо годину
        {
            "$addFields": {
                "pickup_hour": { "$hour": "$tpep_pickup_datetime" }
            }
        },
        # Етап 3: Групуємо за ГОДИНОЮ та ТИПОМ ОПЛАТИ
        {
            "$group": {
                "_id": {
                    "hour": "$pickup_hour",
                    "payment": "$payment_type"
                },
                "avg_fare": { "$avg": "$fare_amount" },
                "total_trips": { "$sum": 1 }
            }
        },
        # Етап 4: Проєкція (витягуємо дані зі складеного _id на верхній рівень)
        {
            "$project": {
                "_id": 0,
                "Hour": "$_id.hour",
                "payment_type": "$_id.payment",
                "AvgFare": { "$round": ["$avg_fare", 2] },
                "TripCount": "$total_trips"
            }
        },
        # Етап 5: Сортування
        { "$sort": { "Hour": 1, "payment_type": 1 } }
    ]

    # Виконання агрегації
    results = list(trips_col.aggregate(pipeline))

    if results:
        # Збереження в нову колекцію
        report_col.delete_many({})
        report_col.insert_many(results)
        
        # Вивід для перевірки
        df = pd.DataFrame(results)
        print("\n📊 Сформовано статистику по годинах та типах оплат:")
        print(df.head(10).to_string(index=False))
        print(f"\n✅ Дані збережено в: {report_col.name}")
    else:
        print("⚠️ Дані не знайдені або tpep_pickup_datetime не у форматі Date.")

if __name__ == "__main__":
    run_time_analytics()