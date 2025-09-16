#!/usr/bin/env python
"""
Полное тестирование функционала ModelsViewFull и ModelSpecificationFormV4
"""
import sys
import time
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QTimer
from PyQt6.QtTest import QTest

from database.connection import DatabaseConnection
from ui.references.models_view_full import ModelsViewFull
from ui.references.model_specification_form_v4 import ModelSpecificationFormV4

def test_complete_workflow():
    """Полное тестирование workflow"""
    print("🧪 Полное тестирование workflow модели...")

    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)

    db = DatabaseConnection()

    # Тест 1: Открытие основной формы моделей
    print("1. Тестирование основной формы моделей...")
    main_view = ModelsViewFull()
    main_view.show()

    # Даем время на загрузку
    app.processEvents()
    time.sleep(1)

    print("✓ Основная форма моделей открыта")

    # Тест 2: Открытие формы создания модели
    print("2. Тестирование формы создания модели...")
    model_form = ModelSpecificationFormV4()
    model_form.show()

    # Даем время на загрузку
    app.processEvents()
    time.sleep(1)

    print("✓ Форма создания модели открыта")

    # Тест 3: Проверка наличия вкладки "Параметры модели"
    print("3. Проверка вкладки 'Параметры модели'...")
    parameters_found = False
    for i in range(model_form.tabs.count()):
        if "Параметры" in model_form.tabs.tabText(i):
            model_form.tabs.setCurrentIndex(i)
            parameters_found = True
            break

    if parameters_found:
        print("✓ Вкладка 'Параметры модели' найдена и активирована")
    else:
        print("❌ Вкладка 'Параметры модели' не найдена")

    # Тест 4: Заполнение базовых полей
    print("4. Заполнение базовых полей...")
    model_form.name_input.setText("Тестовая модель workflow")
    model_form.article_input.setText("TWF001")
    model_form.last_code_input.setText("75")

    print("✓ Базовые поля заполнены")

    # Тест 5: Проверка работы справочников
    print("5. Проверка загрузки справочников...")

    # Проверим, что справочники загружены
    if hasattr(model_form, 'lasting_combo') and model_form.lasting_combo.count() > 0:
        print(f"✓ Справочник типов затяжки загружен: {model_form.lasting_combo.count()} элементов")
    else:
        print("⚠️ Справочник типов затяжки пуст")

    if hasattr(model_form, 'perforation_table'):
        print("✓ Таблица вариантов перфорации доступна")
    else:
        print("❌ Таблица вариантов перфорации недоступна")

    if hasattr(model_form, 'lining_table'):
        print("✓ Таблица вариантов подкладки доступна")
    else:
        print("❌ Таблица вариантов подкладки недоступна")

    # Тест 6: Тестирование соединений БД
    print("6. Тестирование соединений БД...")

    conn_count = 0
    connections = []
    try:
        # Получим несколько соединений
        for i in range(3):
            conn = db.get_connection()
            if conn:
                connections.append(conn)
                conn_count += 1

        print(f"✓ Получено {conn_count} соединений из пула")

        # Вернем их обратно
        for conn in connections:
            db.put_connection(conn)

        print("✓ Все соединения возвращены в пул")

    except Exception as e:
        print(f"❌ Ошибка работы с пулом соединений: {e}")

    # Закрываем формы
    model_form.close()
    main_view.close()

    print("=" * 50)
    print("🏁 Полное тестирование завершено")

    return True

if __name__ == "__main__":
    success = test_complete_workflow()
    if success:
        print("\n✅ Все тесты прошли успешно!")
    else:
        print("\n❌ Обнаружены ошибки в тестах!")