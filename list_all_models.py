#!/usr/bin/env python
"""
Показать все модели в базе данных
"""
from database.connection import DatabaseConnection
import json

def list_all_models():
    """Показываем все модели в БД"""
    print("📋 Список всех моделей в базе данных...")

    db = DatabaseConnection()
    conn = db.get_connection()

    if not conn:
        print("❌ Не удалось подключиться к БД")
        return

    try:
        cursor = conn.cursor()

        # Получаем все модели
        cursor.execute("""
            SELECT m.id, m.name, m.article, m.model_type, m.gender, m.created_at
            FROM models m
            ORDER BY m.created_at DESC
        """)

        models = cursor.fetchall()

        if not models:
            print("❌ Модели в базе данных не найдены")
            return

        print(f"\n📊 Всего найдено моделей: {len(models)}")
        print("=" * 80)

        for model in models:
            model_id, name, article, model_type, gender, created_at = model
            print(f"\n🟦 ID: {model_id}")
            print(f"   📝 Название: {name}")
            print(f"   🏷️  Артикул: {article}")
            print(f"   👟 Тип: {model_type}")
            print(f"   👤 Пол: {gender}")
            print(f"   📅 Создана: {created_at}")

            # Проверяем наличие спецификаций
            cursor.execute("""
                SELECT COUNT(*) FROM specifications s WHERE s.model_id = %s
            """, (model_id,))

            spec_count = cursor.fetchone()[0]
            print(f"   📄 Спецификаций: {spec_count}")

            # Если есть спецификации, покажем последнюю
            if spec_count > 0:
                cursor.execute("""
                    SELECT s.parameters_data, s.created_at
                    FROM specifications s
                    WHERE s.model_id = %s
                    ORDER BY s.created_at DESC
                    LIMIT 1
                """, (model_id,))

                spec_result = cursor.fetchone()
                if spec_result:
                    parameters_data, spec_created = spec_result
                    print(f"   📋 Последняя спецификация: {spec_created}")

                    if parameters_data:
                        try:
                            params = json.loads(parameters_data) if isinstance(parameters_data, str) else parameters_data

                            # Кратко о параметрах
                            has_perforation = 'perforation_ids' in params and params['perforation_ids']
                            has_lining = 'lining_ids' in params and params['lining_ids']
                            has_lasting = 'lasting_type_id' in params and params['lasting_type_id']

                            features = []
                            if has_perforation:
                                perf_count = len(params['perforation_ids']) if isinstance(params['perforation_ids'], list) else 1
                                features.append(f"перфорация ({perf_count})")
                            if has_lining:
                                lining_count = len(params['lining_ids']) if isinstance(params['lining_ids'], list) else 1
                                features.append(f"подкладка ({lining_count})")
                            if has_lasting:
                                features.append("затяжка")

                            if features:
                                print(f"   ✅ Параметры: {', '.join(features)}")
                            else:
                                print("   ⚠️  Параметры не заданы")

                        except Exception as e:
                            print(f"   ❌ Ошибка чтения параметров: {e}")

        cursor.close()

    except Exception as e:
        print(f"❌ Ошибка: {e}")
    finally:
        if conn:
            db.put_connection(conn)

if __name__ == "__main__":
    list_all_models()