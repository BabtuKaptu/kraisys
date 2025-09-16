#!/usr/bin/env python3
"""
Тест просмотра варианта - проверяем исправления
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from database.connection import DatabaseConnection
from ui.references.variant_view_edit_form import VariantViewEditForm

def test_variant_view():
    """Тестируем просмотр варианта ID=5"""

    print("🧪 Тестируем просмотр варианта ID=4...")

    try:
        # Подключение к БД
        db = DatabaseConnection()

        # Создаем форму просмотра варианта
        dialog = VariantViewEditForm(
            variant_id=4,
            db=db,
            read_only=True
        )

        print("✅ Форма просмотра варианта создана успешно!")
        print(f"📝 Название варианта: {dialog.variant_name_input.text()}")
        print(f"🔢 Код варианта: {dialog.variant_code_input.text()}")
        print(f"📋 Строк в таблице деталей кроя: {dialog.cutting_table.rowCount()}")

        # Проверяем содержимое таблицы
        if dialog.cutting_table.rowCount() > 0:
            print("🔍 Детали кроя:")
            for row in range(dialog.cutting_table.rowCount()):
                name_item = dialog.cutting_table.item(row, 0)
                if name_item:
                    print(f"  - {name_item.text()}")

        return True

    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    app = QApplication(sys.argv)
    success = test_variant_view()
    if success:
        print("🎉 Тест прошел успешно!")
    else:
        print("💥 Тест провалился!")