#!/usr/bin/env python3
"""Тест справочника типов перфорации"""

import sys
from PyQt6.QtWidgets import QApplication, QMessageBox
from database.connection import DatabaseConnection
from ui.references.perforation_types_view import PerforationTypesTableWidget, PerforationTypeEditForm

def test_perforation():
    """Тестирование создания новой записи перфорации"""
    app = QApplication(sys.argv)

    try:
        # Тест 1: Создание виджета таблицы
        print("🔹 Тест 1: Создание виджета таблицы перфораций...")
        table_widget = PerforationTypesTableWidget()
        print("✅ Виджет таблицы создан успешно")

        # Тест 2: Создание формы редактирования
        print("🔹 Тест 2: Создание формы редактирования...")
        edit_form = PerforationTypeEditForm()
        print("✅ Форма редактирования создана успешно")

        # Тест 3: Проверка table_name
        print("🔹 Тест 3: Проверка table_name...")
        print(f"table_name в форме: {edit_form.table_name}")

        if edit_form.table_name == 'perforation_types':
            print("✅ table_name установлен правильно")
        else:
            print(f"❌ table_name неправильный: {edit_form.table_name}")

        # Тест 4: Заполнение формы тестовыми данными
        print("🔹 Тест 4: Заполнение формы тестовыми данными...")
        edit_form.code_input.setText("TEST-001")
        edit_form.name_input.setText("Тестовая перфорация")
        edit_form.description_input.setPlainText("Описание тестовой перфорации")
        print("✅ Форма заполнена тестовыми данными")

        # Тест 5: Получение данных из формы
        print("🔹 Тест 5: Получение данных из формы...")
        form_data = edit_form.get_form_data()
        print(f"Данные формы: {form_data}")
        print("✅ Данные получены успешно")

        # Тест 6: Валидация
        print("🔹 Тест 6: Валидация формы...")
        errors = edit_form.validate_form()
        if errors:
            print(f"❌ Ошибки валидации: {errors}")
        else:
            print("✅ Валидация прошла успешно")

        # Тест 7: Показать форму для визуального теста
        print("🔹 Тест 7: Показ формы для визуального теста...")
        edit_form.show()

        print("🎯 Все тесты выполнены. Теперь попробуйте сохранить запись в форме...")
        print("   (нажмите Save в открывшейся форме)")

        app.exec()

    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_perforation()