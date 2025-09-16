#!/usr/bin/env python
"""
Проверка данных модели Хлынов в базе данных
"""
from database.connection import DatabaseConnection
import json

def check_khlynov_data():
    """Проверяем данные модели Хлынов"""
    print("🔍 Проверка данных модели Хлынов...")

    db = DatabaseConnection()
    conn = db.get_connection()

    if not conn:
        print("❌ Не удалось подключиться к БД")
        return

    try:
        cursor = conn.cursor()

        # Ищем модель Хлынов
        cursor.execute("""
            SELECT m.id, m.name, m.article, m.model_type, m.gender
            FROM models m
            WHERE m.name ILIKE %s OR m.article ILIKE %s
        """, ('%хлынов%', '%хлынов%'))

        models = cursor.fetchall()

        if not models:
            print("❌ Модель Хлынов не найдена")
            return

        for model in models:
            model_id, name, article, model_type, gender = model
            print(f"\n📋 Модель: {name} (ID: {model_id})")
            print(f"   Артикул: {article}")
            print(f"   Тип: {model_type}")
            print(f"   Пол: {gender}")

            # Проверяем спецификации
            cursor.execute("""
                SELECT s.id, s.parameters_data, s.created_at
                FROM specifications s
                WHERE s.model_id = %s
                ORDER BY s.created_at DESC
            """, (model_id,))

            specs = cursor.fetchall()

            if not specs:
                print("   ⚠️ Спецификации не найдены")
                continue

            print(f"\n   📊 Найдено спецификаций: {len(specs)}")

            for i, spec in enumerate(specs, 1):
                spec_id, parameters_data, created_at = spec
                print(f"\n   📄 Спецификация #{i} (ID: {spec_id})")
                print(f"      Создана: {created_at}")

                if parameters_data:
                    try:
                        params = json.loads(parameters_data) if isinstance(parameters_data, str) else parameters_data

                        print("      📋 Параметры:")

                        # Варианты перфорации
                        if 'perforation_ids' in params:
                            perf_ids = params['perforation_ids']
                            if perf_ids:
                                print(f"         🔸 Варианты перфорации (IDs): {perf_ids}")

                                # Получаем названия типов перфорации
                                if isinstance(perf_ids, list) and perf_ids:
                                    placeholders = ','.join(['%s'] * len(perf_ids))
                                    cursor.execute(f"""
                                        SELECT id, name FROM perforation_types
                                        WHERE id IN ({placeholders})
                                    """, perf_ids)

                                    perf_types = cursor.fetchall()
                                    for perf_id, perf_name in perf_types:
                                        print(f"           - {perf_name} (ID: {perf_id})")
                            else:
                                print("         🔸 Варианты перфорации: не выбраны")

                        # Варианты подкладки
                        if 'lining_ids' in params:
                            lining_ids = params['lining_ids']
                            if lining_ids:
                                print(f"         🔸 Варианты подкладки (IDs): {lining_ids}")

                                # Получаем названия типов подкладки
                                if isinstance(lining_ids, list) and lining_ids:
                                    placeholders = ','.join(['%s'] * len(lining_ids))
                                    cursor.execute(f"""
                                        SELECT id, name FROM lining_types
                                        WHERE id IN ({placeholders})
                                    """, lining_ids)

                                    lining_types = cursor.fetchall()
                                    for lining_id, lining_name in lining_types:
                                        print(f"           - {lining_name} (ID: {lining_id})")
                            else:
                                print("         🔸 Варианты подкладки: не выбраны")

                        # Тип затяжки
                        if 'lasting_type_id' in params:
                            lasting_id = params['lasting_type_id']
                            if lasting_id:
                                cursor.execute("""
                                    SELECT name FROM lasting_types WHERE id = %s
                                """, (lasting_id,))

                                lasting_result = cursor.fetchone()
                                if lasting_result:
                                    print(f"         🔸 Тип затяжки: {lasting_result[0]} (ID: {lasting_id})")
                                else:
                                    print(f"         🔸 Тип затяжки: ID {lasting_id} (не найден)")
                            else:
                                print("         🔸 Тип затяжки: не выбран")

                        # Примечания к параметрам
                        if 'parameters_notes' in params and params['parameters_notes']:
                            print(f"         📝 Примечания: {params['parameters_notes']}")

                    except json.JSONDecodeError as e:
                        print(f"      ❌ Ошибка парсинга JSON: {e}")
                        print(f"      Сырые данные: {parameters_data}")
                else:
                    print("      ⚠️ Данные параметров отсутствуют")

        cursor.close()

    except Exception as e:
        print(f"❌ Ошибка: {e}")
    finally:
        if conn:
            db.put_connection(conn)

if __name__ == "__main__":
    check_khlynov_data()