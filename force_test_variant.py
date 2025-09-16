#!/usr/bin/env python3
"""
Принудительный тест варианта - полная имитация UI загрузки
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Принудительная очистка модулей
modules_to_reload = [
    'ui.references.variant_view_edit_form',
    'ui.references.variants_list_dialog'
]

for module in modules_to_reload:
    if module in sys.modules:
        del sys.modules[module]

# Импорты после очистки
from PyQt6.QtWidgets import QApplication
from database.connection import DatabaseConnection
from ui.references.variant_view_edit_form import VariantViewEditForm

def test_variant_ui():
    """Тест UI варианта с полной имитацией"""

    print("🧪 Принудительный тест UI варианта...")

    app = QApplication(sys.argv)

    try:
        # Подключение к БД
        db = DatabaseConnection()

        # Создаем форму в режиме просмотра
        print("🔍 Создаем форму просмотра варианта ID=5...")
        dialog = VariantViewEditForm(
            variant_id=5,
            db=db,
            read_only=True
        )

        print("✅ Форма создана успешно!")
        print(f"📝 Название: '{dialog.variant_name_input.text()}'")
        print(f"🔢 Код: '{dialog.variant_code_input.text()}'")
        print(f"📋 Строк в таблице: {dialog.cutting_table.rowCount()}")

        # Проверяем данные в таблице
        if dialog.cutting_table.rowCount() > 0:
            print("🔍 Содержимое таблицы:")
            for row in range(dialog.cutting_table.rowCount()):
                name_item = dialog.cutting_table.item(row, 0)
                material_item = dialog.cutting_table.item(row, 2)
                if name_item and material_item:
                    print(f"  [{row}] {name_item.text()} - {material_item.text()}")

        # Теперь тестируем переключение в режим редактирования
        print("\n🔄 Переключаемся в режим редактирования...")
        dialog.toggle_mode()

        print(f"📝 Режим: {dialog.mode}")
        print(f"🔧 Кнопка: {dialog.mode_btn.text()}")

        return True

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_variant_ui()
    if success:
        print("\n🎉 UI тест прошел успешно!")
    else:
        print("\n💥 UI тест провалился!")