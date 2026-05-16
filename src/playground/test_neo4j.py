from neo4j import GraphDatabase

# Налаштування підключення
URI = "bolt://localhost:7687"
AUTH = ("neo4j", "password123")

def create_knowledge_node(tx, name):
    # Створюємо вузол та зв'язок
    query = """
    MERGE (p:Person {name: $name})
    MERGE (m:Degree {title: 'Master of Science AI/ML'})
    MERGE (p)-[:STUDIES]->(m)
    RETURN p.name, m.title
    """
    result = tx.run(query, name=name)
    return result.single()

try:
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        with driver.session() as session:
            record = session.execute_write(create_knowledge_node, "Ivan") # Можете змінити на своє ім'я
            print(f"✅ Успішно! {record['p.name']} тепер пов'язаний із {record['m.title']}")

except Exception as e:
    print(f"❌ Помилка: {e}")