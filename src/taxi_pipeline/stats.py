import pandas as pd
import os
import redis
import json

def save_stats_to_redis(hourly_data):
    try:
        # Підключаємось до нашого Docker-Redis
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        
        # Перетворюємо дані у словник і зберігаємо як JSON
        stats_dict = hourly_data.to_dict()
        r.set('hourly_avg_revenue', json.dumps(stats_dict))
        
        print("\n🚀 Статистику успішно завантажено в Redis!")
        print(f"📥 Перевірка даних у кеші (перші 2 записи): {dict(list(stats_dict.items())[:2])}")
    except Exception as e:
        print(f"❌ Помилка підключення до Redis: {e}")

def run_basic_analytics():
    # 1. Завантажуємо дані
    path = "data/processed/clean_trips.parquet"
    if not os.path.exists(path):
        print("❌ Файл не знайдено! Спочатку запусти processor.py")
        return

    df = pd.read_parquet(path)
    print(f"✅ Завантажено {len(df)} рядків для аналізу.\n")

    # 2. Аналіз чайових
    df['distance_category'] = pd.cut(df['trip_distance'], 
                                   bins=[0, 2, 5, 10, 100], 
                                   labels=['Коротка (0-2)', 'Середня (2-5)', 'Довга (5-10)', 'Екстремальна (10+)'])

    tip_stats = df.groupby('distance_category')['tip_amount'].mean().reset_index()
    print("📊 Середні чайові по категоріях відстані ($):")
    print(tip_stats)
    print("-" * 30)

    # 3. Аналіз годин пік
    df['pickup_hour'] = df['tpep_pickup_datetime'].dt.hour
    hourly_revenue = df.groupby('pickup_hour')['total_amount'].mean()
    
    print("⏰ Топ-5 найприбутковіших годин доби (середній чек):")
    print(hourly_revenue.sort_values(ascending=False).head(5))

    # --- НОВИЙ КРОК: Збереження результатів ---
    save_stats_to_redis(hourly_revenue)

if __name__ == "__main__":
    run_basic_analytics()