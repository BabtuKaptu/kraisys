#!/usr/bin/env python
"""
Добавляем поле soles в таблицу specifications
"""
from database.connection import DatabaseConnection

def add_soles_field():
    """Добавляем поле soles в таблицу specifications"""
    print("🔧 Добавление поля soles в таблицу specifications...")

    db = DatabaseConnection()
    conn = db.get_connection()

    if not conn:
        print("❌ Не удалось подключиться к БД")
        return

    try:
        cursor = conn.cursor()

        # Проверяем, есть ли уже поле soles
        cursor.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'specifications' AND column_name = 'soles'
        """)

        if cursor.fetchone():
            print("✅ Поле soles уже существует в таблице specifications")
            return

        # Добавляем поле soles типа JSONB
        cursor.execute("""
            ALTER TABLE specifications
            ADD COLUMN soles JSONB
        """)

        print("✅ Поле soles успешно добавлено в таблицу specifications")

        cursor.close()
        conn.commit()

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        conn.rollback()
    finally:
        if conn:
            db.put_connection(conn)

if __name__ == "__main__":
    add_soles_field()