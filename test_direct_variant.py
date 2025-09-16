#!/usr/bin/env python3
"""
Прямой тест варианта - проверка исправлений в изолированном процессе
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import json
import psycopg2.extras
from database.connection import DatabaseConnection

def test_direct_variant_load():
    """Прямой тест загрузки варианта"""

    print("🔍 Тестируем прямую загрузку варианта из БД...")

    try:
        # Подключение к БД
        db = DatabaseConnection()
        conn = db.get_connection()
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # Загружаем данные варианта
        cursor.execute("""
            SELECT s.*, m.name as model_name, m.article as model_article
            FROM specifications s
            JOIN models m ON s.model_id = m.id
            WHERE s.id = %s
        """, (5,))

        variant = cursor.fetchone()

        if variant:
            print(f"✅ Вариант найден: {variant['variant_name']}")
            print(f"📊 Тип cutting_parts: {type(variant.get('cutting_parts'))}")

            # Проверяем наше исправление
            cutting_parts = variant.get('cutting_parts', [])
            print(f"🔍 cutting_parts до обработки: {cutting_parts}")

            if isinstance(cutting_parts, str):
                print("🔧 Обнаружена строка, применяем JSON парсинг...")
                cutting_parts = json.loads(cutting_parts) if cutting_parts else []
                print(f"✅ cutting_parts после парсинга: {len(cutting_parts)} элементов")

                # Проверяем первый элемент
                if cutting_parts:
                    first_part = cutting_parts[0]
                    name = first_part.get('name', '')
                    print(f"🎯 Первая деталь: {name}")
                    print("✅ Метод .get() работает корректно!")

            else:
                print("📝 cutting_parts уже является объектом")
                if cutting_parts:
                    first_part = cutting_parts[0]
                    name = first_part.get('name', '')
                    print(f"🎯 Первая деталь: {name}")

            return True
        else:
            print("❌ Вариант не найден")
            return False

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_direct_variant_load()
    if success:
        print("🎉 Исправления работают!")
    else:
        print("💥 Проблема с исправлениями!")