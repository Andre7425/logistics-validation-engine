import pandas as pd
import logging
import os
from src.db.mongo_client import MongoDBClient

# Налаштування логування (дуже важливо для систем моніторингу)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class LogisticsDataProcessor:
    def __init__(self):
        self.df = None

    
    def extract_from_url(self, url: str):
        try:
            logging.info(f"Downloading data from {url}...")
            full_df = pd.read_parquet(url)
            # Беремо перші 100 000 рядків для стабільної розробки
            self.df = full_df.head(100000).copy() 
            logging.info(f"Successfully loaded {len(self.df)} records for development.")
        except Exception as e:
            logging.error(f"Error: {e}")
            raise
    
    def transform(self):
        """Очищення та базова трансформація даних."""
        if self.df is None:
            logging.warning("No data to transform. Call extract first.")
            return

        initial_count = len(self.df)

        # 1. Валідація значень (Business Logic Validation)
        # Видаляємо поїздки з нульовою або від'ємною дистанцією
        self.df = self.df[self.df['trip_distance'] > 0]
        
        # Видаляємо записи, де кількість пасажирів некоректна (напр. <= 0)
        if 'passenger_count' in self.df.columns:
            self.df = self.df[self.df['passenger_count'] > 0]

        # 2. Робота з часом (Feature Engineering)
        self.df['tpep_pickup_datetime'] = pd.to_datetime(self.df['tpep_pickup_datetime'])
        self.df['tpep_dropoff_datetime'] = pd.to_datetime(self.df['tpep_dropoff_datetime'])
        
        # Розраховуємо тривалість поїздки в хвилинах
        self.df['duration_minutes'] = (
            self.df['tpep_dropoff_datetime'] - self.df['tpep_pickup_datetime']
        ).dt.total_seconds() / 60

        # Видаляємо аномальні поїздки (напр. понад 5 годин або менше 30 секунд)
        self.df = self.df[(self.df['duration_minutes'] > 0.5) & (self.df['duration_minutes'] < 300)]

        final_count = len(self.df)
        logging.info(f"Transformation complete. Removed {initial_count - final_count} invalid records.")

    def load_to_parquet(self, output_path: str):
        """Збереження очищених даних для подальшого аналізу."""
        if self.df is not None:
            self.df.to_parquet(output_path, index=False)
            logging.info(f"Data saved to {output_path}")

if __name__ == "__main__":
    # 1. Налаштування
    DATA_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-01.parquet"
    os.makedirs('data/processed', exist_ok=True)
    
    # 2. Обробка даних
    processor = LogisticsDataProcessor()
    
    try:
        logging.info("Starting ETL process...")
        processor.extract_from_url(DATA_URL)
        
        # Зберігаємо кількість рядків до трансформації
        initial_count = len(processor.df) 
        
        processor.transform()
        processor.load_to_parquet('data/processed/clean_trips.parquet')
        
        # 3. Логування успіху в хмару Atlas
        db = MongoDBClient()
        db.log_process({
            "event": "ETL_Execution",
            "status": "Success",
            "dataset": "NYC_Taxi_2024_01",
            "initial_rows": initial_count,
            "processed_rows": len(processor.df),
            "removed_outliers": initial_count - len(processor.df)
        })
        logging.info("ETL process finished and logged to cloud.")

    except Exception as e:
        # Логування помилки, якщо щось пішло не так
        logging.error(f"ETL failed: {e}")
        try:
            db = MongoDBClient()
            db.log_process({"event": "ETL_Execution", "status": "Failed", "error": str(e)})
        except:
            pass