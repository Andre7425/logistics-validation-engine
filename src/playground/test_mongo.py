from pymongo import MongoClient

try:
    # Підключаємося до локального MongoDB
    client = MongoClient("mongodb://admin:secret_pass@localhost:27017/")
    
    # Вибираємо базу та колекцію (вони створяться автоматично)
    # Раніше було: db = client["test_database"]
    db = client["learning_db"] 
    collection = db["lecture_examples"]
    # Записуємо тестовий документ
    result = collection.insert_one({"name": "Gemini User", "role": "AI/ML Student", "status": "Success"})
    print(f"Документ збережено з ID: {result.inserted_id}")
    
    # Перевіряємо, чи він там є
    doc = collection.find_one({"name": "Gemini User"})
    print(f"Знайдено в базі: {doc}")

except Exception as e:
    print(f"Помилка підключення: {e}")