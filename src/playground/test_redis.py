import redis

# Підключаємось до локального Redis
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

try:
    r.set('status', 'Всі системи працюють!')
    print(f"🚀 Повідомлення з Redis: {r.get('status')}")
except Exception as e:
    print(f"❌ Помилка: {e}")