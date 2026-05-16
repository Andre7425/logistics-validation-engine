import redis
import json

def save_stats_to_redis(hourly_data):
    # Підключаємось до нашого Docker-Redis
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    
    # Перетворюємо Series у словник і зберігаємо як JSON
    stats_dict = hourly_data.to_dict()
    r.set('hourly_avg_revenue', json.dumps(stats_dict))
    
    print("🚀 Статистику успішно завантажено в Redis!")
    print(f"Приклад даних у кеші: {r.get('hourly_avg_revenue')}")

# Виклич цю функцію в кінці свого основного скрипта, 
# передавши туди hourly_revenue