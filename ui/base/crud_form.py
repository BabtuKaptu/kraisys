"""CRUD Form Dialog base class"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                            QDialogButtonBox, QMessageBox)
from PyQt6.QtCore import Qt
from database.connection import DatabaseConnection
import psycopg2.extras


class CrudFormDialog(QDialog):
    """Базовый класс для CRUD форм"""

    def __init__(self, record_data=None, parent=None):
        super().__init__(parent)
        self.record_data = record_data
        # table_name должно быть установлено в наследниках перед вызовом super().__init__()
        if not hasattr(self, 'table_name'):
            self.table_name = None
        self.db = DatabaseConnection()

        self.setModal(True)
        self.setup_ui()

        if record_data:
            self.set_form_data(record_data)

    def setup_ui(self):
        """Настройка UI"""
        layout = QVBoxLayout(self)

        # Создаем поля формы
        form_layout = self.create_form_fields()
        layout.addLayout(form_layout)

        # Кнопки
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save |
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.save_record)
        button_box.rejected.connect(self.reject)

        layout.addWidget(button_box)

    def create_form_fields(self):
        """Создать поля формы (переопределить в наследниках)"""
        raise NotImplementedError("Метод create_form_fields должен быть переопределен")

    def get_form_data(self):
        """Получить данные из формы (переопределить в наследниках)"""
        raise NotImplementedError("Метод get_form_data должен быть переопределен")

    def set_form_data(self, data):
        """Установить данные в форму (переопределить в наследниках)"""
        raise NotImplementedError("Метод set_form_data должен быть переопределен")

    def validate_form(self):
        """Валидация формы (переопределить в наследниках)"""
        return []

    def save_record(self):
        """Сохранение записи"""
        # Проверяем, что table_name установлен
        if not self.table_name:
            QMessageBox.critical(self, "Ошибка",
                f"table_name не установлен в классе {self.__class__.__name__}. "
                f"Убедитесь, что self.table_name установлен ПЕРЕД вызовом super().__init__()")
            return

        # Валидация
        errors = self.validate_form()
        if errors:
            error_text = "\\n".join(errors)
            QMessageBox.warning(self, "Ошибка валидации", error_text)
            return

        try:
            form_data = self.get_form_data()
            conn = self.db.get_connection()
            cursor = conn.cursor()

            if self.record_data:  # Редактирование
                # Формируем SQL для UPDATE
                set_clause = ", ".join([f"{key} = %s" for key in form_data.keys()])
                sql = f"UPDATE {self.table_name} SET {set_clause} WHERE id = %s"
                params = list(form_data.values()) + [self.record_data['id']]
                cursor.execute(sql, params)

                QMessageBox.information(self, "Успешно", "Запись обновлена")
            else:  # Добавление
                # Формируем SQL для INSERT
                columns = ", ".join(form_data.keys())
                placeholders = ", ".join(["%s"] * len(form_data))
                sql = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})"
                cursor.execute(sql, list(form_data.values()))

                QMessageBox.information(self, "Успешно", "Запись добавлена")

            conn.commit()
            cursor.close()
            self.db.put_connection(conn)

            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить запись: {e}")