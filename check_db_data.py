#!/usr/bin/env python3
"""
Проверка данных в базе - что сохранено в базовых моделях
"""

import json
from database.connection import DatabaseConnection
import psycopg2.extras

def check_specifications_data():
    """Проверить данные в таблице specifications"""
    db = DatabaseConnection()
    conn = db.get_connection()

    if not conn:
        print("❌ Не удалось подключиться к базе данных")
        return

    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        # Получаем базовые модели через specifications
        print("🔍 БАЗОВЫЕ МОДЕЛИ:")
        print("=" * 80)

        cursor.execute("""
            SELECT s.id, s.variant_name, s.variants, s.lining_ids, s.perforation_ids, m.name as model_name
            FROM specifications s
            JOIN models m ON s.model_id = m.id
            WHERE s.is_default = true OR s.variant_name IS NULL OR s.variant_name = ''
            ORDER BY s.id
        """)

        base_models = cursor.fetchall()

        if not base_models:
            print("❌ Базовые модели не найдены")
            return

        for model in base_models:
            print(f"\n📋 ID: {model['id']} | Модель: {model['model_name']} | Вариант: {model['variant_name'] or 'БАЗОВЫЙ'}")
            print("-" * 50)

            # Проверяем JSON варианты
            variants = model['variants']
            if variants:
                if isinstance(variants, str):
                    try:
                        variants = json.loads(variants)
                    except:
                        print("❌ Ошибка парсинга JSON вариантов")
                        continue

                print("📊 ВАРИАНТЫ:")

                # Проверяем варианты подкладки/стельки
                if 'lining' in variants:
                    lining_list = variants['lining']
                    print(f"🔸 Подкладка/стелька ({len(lining_list)} вариантов):")
                    for i, lining in enumerate(lining_list, 1):
                        print(f"   {i}. {lining.get('name', 'Без названия')} (ID: {lining.get('id', 'N/A')})")
                else:
                    print("🔸 Подкладка/стелька в variants: НЕ НАЙДЕНО")

                # Проверяем варианты перфорации
                if 'perforation' in variants:
                    perf_list = variants['perforation']
                    print(f"🔸 Перфорация ({len(perf_list)} вариантов):")
                    for i, perf in enumerate(perf_list, 1):
                        print(f"   {i}. {perf.get('name', 'Без названия')} (ID: {perf.get('id', 'N/A')})")
                else:
                    print("🔸 Перфорация в variants: НЕ НАЙДЕНО")

                # Показываем все ключи в вариантах
                print(f"🔸 Все ключи вариантов: {list(variants.keys())}")
            else:
                print("❌ Варианты отсутствуют или пусты")

            # Проверяем отдельные поля
            if model['lining_ids']:
                lining_ids = model['lining_ids']
                if isinstance(lining_ids, str):
                    try:
                        lining_ids = json.loads(lining_ids)
                    except:
                        pass
                print(f"🔹 lining_ids поле: {lining_ids}")
            else:
                print("🔹 lining_ids поле: пусто")

            if model['perforation_ids']:
                perf_ids = model['perforation_ids']
                if isinstance(perf_ids, str):
                    try:
                        perf_ids = json.loads(perf_ids)
                    except:
                        pass
                print(f"🔹 perforation_ids поле: {perf_ids}")
            else:
                print("🔹 perforation_ids поле: пусто")

        print("\n" + "=" * 80)
        print("🔍 ВАРИАНТЫ МОДЕЛЕЙ:")
        print("=" * 80)

        cursor.execute("""
            SELECT s.id, s.variant_name, s.model_id, s.variants, m.name as model_name
            FROM specifications s
            JOIN models m ON s.model_id = m.id
            WHERE s.variant_name IS NOT NULL AND s.variant_name != ''
            ORDER BY s.model_id, s.id
        """)

        variants = cursor.fetchall()

        if variants:
            for variant in variants:
                print(f"\n🎨 ID: {variant['id']} | Вариант: {variant['variant_name']} | Модель: {variant['model_name']} (ID: {variant['model_id']})")
        else:
            print("📝 Варианты моделей не найдены")

    except Exception as e:
        print(f"❌ Ошибка при проверке данных: {e}")
    finally:
        if conn:
            db.put_connection(conn)

if __name__ == "__main__":
    check_specifications_data()