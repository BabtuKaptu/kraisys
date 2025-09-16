#!/usr/bin/env python
"""
Тестирование сохранения типа затяжки
"""
import sys
import time
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QTimer
from PyQt6.QtTest import QTest

from database.connection import DatabaseConnection
from ui.references.model_specification_form_v4 import ModelSpecificationFormV4

def test_lasting_type():
    """Тестирование типа затяжки"""
    print("🧪 Тестирование сохранения типа затяжки...")

    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)

    db = DatabaseConnection()

    # Проверим доступные типы затяжки
    conn = db.get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, name FROM lasting_types LIMIT 5")
    lasting_types = cursor.fetchall()

    print(f"📋 Доступные типы затяжки:")
    for lasting_id, lasting_name in lasting_types:
        print(f"  - {lasting_name} (ID: {lasting_id})")

    if not lasting_types:
        print("❌ Нет доступных типов затяжки")
        cursor.close()
        db.put_connection(conn)
        return False

    # Выберем первый тип затяжки для теста
    test_lasting_id = lasting_types[0][0]
    test_lasting_name = lasting_types[0][1]

    cursor.close()
    db.put_connection(conn)

    # Открываем модель Хлынов для редактирования (ID: 7)
    model_form = ModelSpecificationFormV4(model_id=7, is_variant=False)
    model_form.show()

    # Даем время на загрузку
    app.processEvents()
    time.sleep(2)

    print("✓ Форма модели Хлынов открыта")

    # Переходим на вкладку "Параметры модели"
    parameters_tab_index = None
    for i in range(model_form.tabs.count()):
        if "Параметры" in model_form.tabs.tabText(i):
            model_form.tabs.setCurrentIndex(i)
            parameters_tab_index = i
            break

    if parameters_tab_index is not None:
        print("✓ Перешли на вкладку 'Параметры модели'")

        # Устанавливаем тип затяжки
        index = model_form.lasting_combo.findData(test_lasting_id)
        if index >= 0:
            model_form.lasting_combo.setCurrentIndex(index)
            print(f"✓ Установлен тип затяжки: {test_lasting_name} (ID: {test_lasting_id})")
        else:
            print(f"❌ Не удалось найти тип затяжки с ID {test_lasting_id}")

        # Сохраняем модель
        print("💾 Сохраняем модель с типом затяжки...")

        try:
            model_form.save_model()
            print("✅ Модель сохранена успешно!")
        except Exception as e:
            print(f"❌ Ошибка при сохранении: {e}")

    else:
        print("❌ Вкладка 'Параметры модели' не найдена")

    # Закрываем форму
    model_form.close()

    print("\\n=== ПРОВЕРКА РЕЗУЛЬТАТОВ ===")

    # Проверяем, что тип затяжки сохранился в базе данных
    conn = db.get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT lasting_type_id
        FROM specifications
        WHERE model_id = 7
        ORDER BY created_at DESC
        LIMIT 1
    """)

    result = cursor.fetchone()
    if result:
        saved_lasting_id = result[0]
        print(f"\\n📋 Сохраненный тип затяжки: {saved_lasting_id}")

        if saved_lasting_id == test_lasting_id:
            print("\\n✅ УСПЕХ: Тип затяжки сохранен корректно!")
        else:
            print(f"\\n⚠️  Тип затяжки не совпадает. Ожидался: {test_lasting_id}, получен: {saved_lasting_id}")

        # Получаем название сохраненного типа затяжки
        if saved_lasting_id:
            cursor.execute("SELECT name FROM lasting_types WHERE id = %s", (saved_lasting_id,))
            name_result = cursor.fetchone()
            if name_result:
                print(f"   Название: {name_result[0]}")

    else:
        print("\\n❌ Не удалось найти сохраненную спецификацию")

    cursor.close()
    db.put_connection(conn)

    print("\\n🏁 Тестирование типа затяжки завершено")
    return True

def main():
    """Главная функция"""
    success = test_lasting_type()
    if success:
        print("\\n✅ Тест прошел успешно!")
    else:
        print("\\n❌ Обнаружены ошибки в тесте!")

if __name__ == "__main__":
    main()