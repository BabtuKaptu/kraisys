#!/usr/bin/env python3
"""Тест сохранения новой записи перфорации"""

import sys
from PyQt6.QtWidgets import QApplication, QMessageBox
from database.connection import DatabaseConnection
from ui.references.perforation_types_view import PerforationTypeEditForm

def test_save_perforation():
    """Тестирование сохранения новой записи перфорации"""
    app = QApplication(sys.argv)

    try:
        print("🔹 Создание формы для новой записи...")
        edit_form = PerforationTypeEditForm()

        print("🔹 Заполнение формы тестовыми данными...")
        edit_form.code_input.setText("TEST-SAVE-001")
        edit_form.name_input.setText("Тестовая перфорация для сохранения")
        edit_form.description_input.setPlainText("Описание тестовой перфорации для проверки сохранения в БД")
        edit_form.is_active_checkbox.setChecked(True)

        print("🔹 Попытка сохранения записи...")
        edit_form.save_record()

        print("✅ Тест сохранения завершен. Проверьте результат в сообщении выше.")

    except Exception as e:
        print(f"❌ Ошибка при тестировании сохранения: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_save_perforation()