#!/usr/bin/env python3
"""Проверка сохраненного варианта модели"""

import json
import psycopg2.extras
from database.connection import DatabaseConnection

db = DatabaseConnection()
conn = db.get_connection()

if conn:
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    # Находим модель Кроссовки Хлынов
    cursor.execute("""
        SELECT id, name
        FROM models
        WHERE name LIKE '%Хлынов%' OR name LIKE '%хлынов%'
    """)
    model = cursor.fetchone()

    if model:
        print(f"Модель найдена: {model['name']} (ID: {model['id']})")
        print("-" * 50)

        # Получаем варианты этой модели
        cursor.execute("""
            SELECT * FROM specifications
            WHERE model_id = %s
            ORDER BY created_at DESC
        """, (model['id'],))

        variants = cursor.fetchall()

        if variants:
            for variant in variants:
                print(f"\nВариант: {variant['variant_name']} ({variant['variant_code']})")
                print(f"UUID: {variant['uuid']}")
                if 'variant_type' in variant:
                    print(f"Тип: {variant['variant_type']}")
                print(f"Создан: {variant['created_at']}")
                if 'total_cost' in variant and variant['total_cost']:
                    print(f"Общая стоимость: {variant['total_cost']} руб")

                # Детали кроя
                if variant['cutting_parts']:
                    print("\nДетали кроя:")
                    for part in variant['cutting_parts']:
                        print(f"  - {part['name']}: {part['quantity']} шт, расход {part['consumption']} дм²")
                        if 'material' in part:
                            print(f"    Материал: {part['material']['name']} ({part['material']['code']})")

                # Материалы
                if variant['materials']:
                    print("\nМатериалы:")
                    if isinstance(variant['materials'], dict):
                        for mat_id, mat in variant['materials'].items():
                            print(f"  - {mat['name']} ({mat['code']}): {mat['total_consumption']} {mat['unit']}, цена {mat['price']} руб/{mat['unit']}")
                    elif isinstance(variant['materials'], list):
                        for mat in variant['materials']:
                            print(f"  - {mat}")

                # Фурнитура
                if variant['hardware']:
                    print("\nФурнитура:")
                    for hw in variant['hardware']:
                        print(f"  - {hw['name']}: {hw['quantity']} {hw['unit']}")

                # Подошва
                if 'sole' in variant and variant['sole']:
                    print("\nПодошва:")
                    print(f"  - {variant['sole']['name']} ({variant['sole']['code']})")
                    print(f"    Размерный ряд: {variant['sole']['size_range']}")

                print("-" * 50)
        else:
            print("Варианты не найдены")
    else:
        print("Модель не найдена")

    cursor.close()
    conn.close()
else:
    print("Не удалось подключиться к базе данных")