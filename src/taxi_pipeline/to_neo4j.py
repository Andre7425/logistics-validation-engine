import pandas as pd
from neo4j import GraphDatabase
import os

# Налаштування підключення (те, що ми прописали в docker-compose)
URI = "bolt://localhost:7687"
AUTH = ("neo4j", "password123")

def upload_trips_to_graph():
    # 1. Завантажуємо дані
    path = "data/processed/clean_trips.parquet"
    if not os.path.exists(path):
        print("❌ Файл не знайдено!")
        return

    df = pd.read_parquet(path).head(1000) # Беремо 1000 для тесту
    print(f"🚀 Завантажуємо {len(df)} маршрутів у Neo4j...")

    # 2. Підключаємось до бази
    driver = GraphDatabase.driver(URI, auth=AUTH)
    
    # Cypher запит: створює два райони та зв'язок між ними
    # MERGE гарантує, що ми не створимо дублікати районів
    query = """
    MERGE (p:Location {id: $pu_id})
    MERGE (d:Location {id: $do_id})
    CREATE (p)-[:TRIP {distance: $dist, fare: $fare}]->(d)
    """

    with driver.session() as session:
        for i, row in df.iterrows():
            session.run(query, 
                        pu_id=int(row['PULocationID']), 
                        do_id=int(row['DOLocationID']),
                        dist=float(row['trip_distance']),
                        fare=float(row['total_amount']))
            if i % 100 == 0:
                print(f"Оброблено {i} поїздок...")

    driver.close()
    print("✅ Граф побудовано! Час дивитися на результат.")

if __name__ == "__main__":
    upload_trips_to_graph()