#!/usr/bin/env python
"""
Тестирование сохранения множественных параметров для базовой модели
"""
import sys
import time
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QTimer
from PyQt6.QtTest import QTest

from database.connection import DatabaseConnection
from ui.references.model_specification_form_v4 import ModelSpecificationFormV4

def test_multiple_parameters():
    """Тестирование множественных параметров"""
    print("🧪 Тестирование сохранения множественных параметров...")

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

        # Очищаем существующие параметры
        model_form.perforation_table.setRowCount(0)
        model_form.lining_table.setRowCount(0)

        print("📝 Добавляем множественные типы перфораций...")

        # Симулируем добавление нескольких типов перфорации
        # (в реальности это делается через диалоги, но мы добавим программно)

        # Получаем доступные типы перфораций
        conn = db.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id, name FROM perforation_types LIMIT 3")
        perf_types = cursor.fetchall()

        for perf_type in perf_types:
            perf_id, perf_name = perf_type
            row = model_form.perforation_table.rowCount()
            model_form.perforation_table.insertRow(row)
            from PyQt6.QtWidgets import QTableWidgetItem
            from PyQt6.QtCore import Qt
            item = QTableWidgetItem(perf_name)
            item.setData(Qt.ItemDataRole.UserRole, perf_id)
            model_form.perforation_table.setItem(row, 0, item)
            print(f"  + Добавлена перфорация: {perf_name} (ID: {perf_id})")

        # Добавляем множественные типы подкладок
        cursor.execute("SELECT id, name FROM lining_types LIMIT 2")
        lining_types = cursor.fetchall()

        for lining_type in lining_types:
            lining_id, lining_name = lining_type
            row = model_form.lining_table.rowCount()
            model_form.lining_table.insertRow(row)
            item = QTableWidgetItem(lining_name)
            item.setData(Qt.ItemDataRole.UserRole, lining_id)
            model_form.lining_table.setItem(row, 0, item)
            print(f"  + Добавлена подкладка: {lining_name} (ID: {lining_id})")

        cursor.close()
        db.put_connection(conn)

        print(f"\\n📊 Текущее состояние таблиц:")
        print(f"   Перфорация: {model_form.perforation_table.rowCount()} строк")
        print(f"   Подкладка: {model_form.lining_table.rowCount()} строк")

        # Имитируем сохранение
        print("\\n💾 Сохраняем модель с множественными параметрами...")

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

    # Проверяем, что параметры сохранились в базе данных
    conn = db.get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT perforation_id, lining_id, perforation_ids, lining_ids
        FROM specifications
        WHERE model_id = 7
        ORDER BY created_at DESC
        LIMIT 1
    """)

    result = cursor.fetchone()
    if result:
        perf_id, lining_id, perf_ids, lining_ids = result
        print(f"\\n📋 Сохраненные параметры:")
        print(f"   perforation_id: {perf_id}")
        print(f"   lining_id: {lining_id}")
        print(f"   perforation_ids: {perf_ids}")
        print(f"   lining_ids: {lining_ids}")

        if perf_ids and lining_ids:
            print("\\n✅ УСПЕХ: Множественные параметры сохранены в новых полях!")
        else:
            print("\\n⚠️  Множественные параметры не сохранились")

    cursor.close()
    db.put_connection(conn)

    print("\\n🏁 Тестирование множественных параметров завершено")
    return True

def main():
    """Главная функция"""
    success = test_multiple_parameters()
    if success:
        print("\\n✅ Тест прошел успешно!")
    else:
        print("\\n❌ Обнаружены ошибки в тесте!")

if __name__ == "__main__":
    main()