"""CRUD form for perforation types reference"""
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
from ui.base.base_table_v2 import BaseTableWidgetV2
from ui.base.crud_form import CrudFormDialog
from database.connection import DatabaseConnection
import psycopg2.extras


class PerforationTypesTableWidget(BaseTableWidgetV2):
    """Таблица типов перфорации с интеграцией БД"""

    def __init__(self, parent=None):
        super().__init__('perforation_types', parent)
        self.setWindowTitle("Справочник типов перфорации")

    def get_visible_columns(self):
        """Видимые колонки для типов перфорации"""
        return ['code', 'name', 'description', 'is_active']

    def get_column_label(self, column_name):
        """Метки колонок для типов перфорации"""
        labels = {
            'code': 'Код',
            'name': 'Название',
            'description': 'Описание',
            'is_active': 'Активен'
        }
        return labels.get(column_name, column_name)

    def create_edit_form(self, record_data=None):
        """Создать форму редактирования"""
        return PerforationTypeEditForm(record_data, self)

    def add_record(self):
        """Добавить новую запись"""
        form = self.create_edit_form()
        if form.exec() == QDialog.DialogCode.Accepted:
            self.refresh_data()

    def edit_record(self):
        """Редактировать запись"""
        record_id = self.get_current_record_id()
        if not record_id:
            QMessageBox.warning(self, "Внимание", "Выберите запись для редактирования")
            return

        # Получаем полные данные записи
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cursor.execute(f"SELECT * FROM {self.table_name} WHERE id = %s", (record_id,))
            record_data = cursor.fetchone()
            cursor.close()
            self.db.put_connection(conn)

            if record_data:
                form = self.create_edit_form(dict(record_data))
                if form.exec() == QDialog.DialogCode.Accepted:
                    self.refresh_data()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить данные записи: {e}")


class PerforationTypeEditForm(CrudFormDialog):
    """Форма редактирования типа перфорации"""

    def __init__(self, record_data=None, parent=None):
        # ВАЖНО: table_name должен быть установлен ДО вызова super().__init__()
        self.table_name = 'perforation_types'
        super().__init__(record_data, parent)

        title = "Редактирование типа перфорации" if record_data else "Добавление типа перфорации"
        self.setWindowTitle(title)
        self.setFixedSize(400, 300)

    def create_form_fields(self):
        """Создание полей формы"""
        layout = QFormLayout()

        # Код
        self.code_input = QLineEdit()
        self.code_input.setMaxLength(20)
        self.code_input.setPlaceholderText("Например: PERF-001")
        layout.addRow("Код:", self.code_input)

        # Название
        self.name_input = QLineEdit()
        self.name_input.setMaxLength(100)
        self.name_input.setPlaceholderText("Например: Мелкая перфорация")
        layout.addRow("Название:", self.name_input)

        # Описание
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(80)
        self.description_input.setPlaceholderText("Описание типа перфорации...")
        layout.addRow("Описание:", self.description_input)

        # Активен
        self.is_active_checkbox = QCheckBox()
        self.is_active_checkbox.setChecked(True)
        layout.addRow("Активен:", self.is_active_checkbox)

        return layout

    def get_form_data(self):
        """Получить данные из формы"""
        return {
            'code': self.code_input.text().strip(),
            'name': self.name_input.text().strip(),
            'description': self.description_input.toPlainText().strip(),
            'is_active': self.is_active_checkbox.isChecked()
        }

    def set_form_data(self, data):
        """Установить данные в форму"""
        self.code_input.setText(data.get('code', ''))
        self.name_input.setText(data.get('name', ''))
        self.description_input.setPlainText(data.get('description', ''))
        self.is_active_checkbox.setChecked(data.get('is_active', True))

    def validate_form(self):
        """Валидация формы"""
        errors = []

        if not self.code_input.text().strip():
            errors.append("Код обязателен для заполнения")

        if not self.name_input.text().strip():
            errors.append("Название обязательно для заполнения")

        # Проверка уникальности кода
        code = self.code_input.text().strip()
        if code:
            db = DatabaseConnection()
            conn = db.get_connection()
            try:
                cursor = conn.cursor()
                if self.record_data:  # Редактирование
                    cursor.execute(
                        "SELECT id FROM perforation_types WHERE code = %s AND id != %s",
                        (code, self.record_data['id'])
                    )
                else:  # Добавление
                    cursor.execute(
                        "SELECT id FROM perforation_types WHERE code = %s",
                        (code,)
                    )

                if cursor.fetchone():
                    errors.append(f"Код '{code}' уже используется")

                cursor.close()
            except Exception as e:
                errors.append(f"Ошибка проверки уникальности: {e}")
            finally:
                if conn:
                    db.put_connection(conn)

        return errors


def main():
    """Тестовая функция"""
    import sys
    app = QApplication(sys.argv)
    window = PerforationTypesTableWidget()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()