#!/usr/bin/env python
"""
Проверка структуры таблицы specifications
"""
from database.connection import DatabaseConnection

def check_spec_structure():
    """Проверяем структуру таблицы specifications"""
    print("🔍 Проверка структуры таблицы specifications...")

    db = DatabaseConnection()
    conn = db.get_connection()

    if not conn:
        print("❌ Не удалось подключиться к БД")
        return

    try:
        cursor = conn.cursor()

        # Проверяем структуру таблицы specifications
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'specifications'
            ORDER BY ordinal_position;
        """)

        columns = cursor.fetchall()

        if not columns:
            print("❌ Таблица specifications не найдена")
            return

        print("\n📋 Структура таблицы specifications:")
        print("-" * 50)
        for col_name, data_type, is_nullable in columns:
            nullable = "NULL" if is_nullable == "YES" else "NOT NULL"
            print(f"  {col_name:<20} | {data_type:<15} | {nullable}")

        # Теперь посмотрим данные спецификаций для модели Хлынов
        print("\n🔍 Данные спецификаций для модели Хлынов (ID: 7):")
        cursor.execute("""
            SELECT * FROM specifications WHERE model_id = 7
        """)

        specs = cursor.fetchall()

        # Получаем названия колонок
        col_names = [desc[0] for desc in cursor.description]

        print(f"\nНайдено спецификаций: {len(specs)}")

        for i, spec in enumerate(specs, 1):
            print(f"\n📄 Спецификация #{i}:")
            for j, value in enumerate(spec):
                print(f"  {col_names[j]}: {value}")

        cursor.close()

    except Exception as e:
        print(f"❌ Ошибка: {e}")
    finally:
        if conn:
            db.put_connection(conn)

if __name__ == "__main__":
    check_spec_structure()