import logging
from datetime import datetime
from pymongo import MongoClient
from pymongo.server_api import ServerApi

# Налаштування логування, щоб бачити результат у терміналі
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class MongoDBClient:
    def __init__(self):
        # Твій рядок підключення до MongoDB Atlas
        self.uri = "mongodb+srv://odnamonetka_db_user:9H5ucSkcYJBxzYUe@cluster0.sdts7db.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
        
        try:
            # Створюємо клієнт та підключаємось до сервера
            self.client = MongoClient(self.uri, server_api=ServerApi('1'))
            
            # Відправляємо "ping", щоб перевірити, чи жива база
            self.client.admin.command('ping')
            logging.info("✅ Successfully connected to MongoDB Atlas!")
            
            # Визначаємо базу та колекцію для логів
            self.db = self.client['logistics_db']
            self.logs = self.db['etl_logs']
            
        except Exception as e:
            logging.error(f"❌ Could not connect to MongoDB: {e}")
            raise

    def log_process(self, stats: dict):
        """Метод для збереження результатів ETL у базу."""
        try:
            document = {
                "timestamp": datetime.now(),
                **stats
            }
            result = self.logs.insert_one(document)
            logging.info(f"💾 Audit log saved to Atlas. ID: {result.inserted_id}")
        except Exception as e:
            logging.error(f"❌ Failed to save log to MongoDB: {e}")

if __name__ == "__main__":
    # Тестовий запуск для перевірки зв'язку
    client = MongoDBClient()
    client.log_process({
        "status": "initial_test",
        "message": "Hello from my laptop to the Cloud!",
        "project": "logistics-validation-engine"
    })