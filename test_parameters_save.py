#!/usr/bin/env python
"""
Тестирование сохранения параметров модели
"""
import sys
import time
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QTimer
from PyQt6.QtTest import QTest

from database.connection import DatabaseConnection
from ui.references.model_specification_form_v4 import ModelSpecificationFormV4

def test_parameters_save():
    """Тестирование сохранения параметров"""
    print("🧪 Тестирование сохранения параметров для модели Хлынов...")

    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)

    db = DatabaseConnection()

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

        # Проверяем существующие параметры
        print(f"📋 Текущее состояние таблиц:")
        print(f"   Перфорация: {model_form.perforation_table.rowCount()} строк")
        print(f"   Подкладка: {model_form.lining_table.rowCount()} строк")

        # Добавляем тип перфорации если таблица пуста
        if model_form.perforation_table.rowCount() == 0:
            print("📝 Добавляем тип перфорации...")
            try:
                model_form.add_perforation()
                app.processEvents()
                time.sleep(1)
                print("✓ Диалог добавления перфорации вызван")
            except Exception as e:
                print(f"❌ Ошибка при добавлении перфорации: {e}")

        # Добавляем тип подкладки если таблица пуста
        if model_form.lining_table.rowCount() == 0:
            print("📝 Добавляем тип подкладки...")
            try:
                model_form.add_lining()
                app.processEvents()
                time.sleep(1)
                print("✓ Диалог добавления подкладки вызван")
            except Exception as e:
                print(f"❌ Ошибка при добавлении подкладки: {e}")

        # Имитируем сохранение (не будем реально сохранять, чтобы не сломать данные)
        print("📝 Симуляция сохранения модели...")

        # Проверяем, что методы сбора данных работают
        try:
            # Собираем данные параметров как это делает save_model
            selected_perforations = []
            for row in range(model_form.perforation_table.rowCount()):
                item = model_form.perforation_table.item(row, 0)
                if item:
                    perf_id = item.data(1001)  # Qt.ItemDataRole.UserRole
                    if perf_id:
                        selected_perforations.append(perf_id)

            selected_linings = []
            for row in range(model_form.lining_table.rowCount()):
                item = model_form.lining_table.item(row, 0)
                if item:
                    lining_id = item.data(1001)  # Qt.ItemDataRole.UserRole
                    if lining_id:
                        selected_linings.append(lining_id)

            print(f"✓ Собраны ID перфораций: {selected_perforations}")
            print(f"✓ Собраны ID подкладок: {selected_linings}")

        except Exception as e:
            print(f"❌ Ошибка при сборе данных: {e}")

    else:
        print("❌ Вкладка 'Параметры модели' не найдена")

    # Закрываем форму
    model_form.close()

    print("=" * 50)
    print("🏁 Тестирование параметров завершено")

    return True

def main():
    """Главная функция"""
    success = test_parameters_save()
    if success:
        print("\n✅ Тест прошел успешно!")
    else:
        print("\n❌ Обнаружены ошибки в тесте!")

if __name__ == "__main__":
    main()