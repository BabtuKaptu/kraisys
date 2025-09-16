"""CRUD form for lining types reference"""
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDoubleValidator
from ui.base.base_table_v2 import BaseTableWidgetV2
from ui.base.crud_form import CrudFormDialog
from database.connection import DatabaseConnection
import psycopg2.extras


class LiningTypesTableWidget(BaseTableWidgetV2):
    """Таблица типов подкладки/стельки с интеграцией БД"""

    def __init__(self, parent=None):
        super().__init__('lining_types', parent)
        self.setWindowTitle("Справочник типов подкладки/стельки")

    def get_visible_columns(self):
        """Видимые колонки для типов подкладки"""
        return ['code', 'name', 'material_type', 'thickness', 'description', 'is_active']

    def get_column_label(self, column_name):
        """Метки колонок для типов подкладки"""
        labels = {
            'code': 'Код',
            'name': 'Название',
            'material_type': 'Тип материала',
            'thickness': 'Толщина',
            'description': 'Описание',
            'is_active': 'Активен'
        }
        return labels.get(column_name, column_name)

    def create_edit_form(self, record_data=None):
        """Создать форму редактирования"""
        return LiningTypeEditForm(record_data, self)

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


class LiningTypeEditForm(CrudFormDialog):
    """Форма редактирования типа подкладки/стельки"""

    def __init__(self, record_data=None, parent=None):
        # ВАЖНО: table_name должен быть установлен ДО вызова super().__init__()
        self.table_name = 'lining_types'
        super().__init__(record_data, parent)

        title = "Редактирование типа подкладки" if record_data else "Добавление типа подкладки"
        self.setWindowTitle(title)
        self.setFixedSize(450, 350)

    def create_form_fields(self):
        """Создание полей формы"""
        layout = QFormLayout()

        # Код
        self.code_input = QLineEdit()
        self.code_input.setMaxLength(20)
        self.code_input.setPlaceholderText("Например: LIN-001")
        layout.addRow("Код:", self.code_input)

        # Название
        self.name_input = QLineEdit()
        self.name_input.setMaxLength(100)
        self.name_input.setPlaceholderText("Например: Хлопковая подкладка")
        layout.addRow("Название:", self.name_input)

        # Тип материала
        self.material_type_combo = QComboBox()
        self.material_type_combo.addItems([
            "Хлопок",
            "Синтетика",
            "Кожа",
            "Замша",
            "Нубук",
            "Текстиль",
            "Мех",
            "Войлок",
            "Другое"
        ])
        self.material_type_combo.setEditable(True)
        layout.addRow("Тип материала:", self.material_type_combo)

        # Толщина
        self.thickness_input = QLineEdit()
        self.thickness_input.setValidator(QDoubleValidator(0.0, 99.9, 2))
        self.thickness_input.setPlaceholderText("Например: 1.5")
        layout.addRow("Толщина (мм):", self.thickness_input)

        # Описание
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(80)
        self.description_input.setPlaceholderText("Описание типа подкладки/стельки...")
        layout.addRow("Описание:", self.description_input)

        # Активен
        self.is_active_checkbox = QCheckBox()
        self.is_active_checkbox.setChecked(True)
        layout.addRow("Активен:", self.is_active_checkbox)

        return layout

    def get_form_data(self):
        """Получить данные из формы"""
        thickness = None
        if self.thickness_input.text().strip():
            try:
                thickness = float(self.thickness_input.text().strip())
            except ValueError:
                thickness = None

        return {
            'code': self.code_input.text().strip(),
            'name': self.name_input.text().strip(),
            'material_type': self.material_type_combo.currentText().strip(),
            'thickness': thickness,
            'description': self.description_input.toPlainText().strip(),
            'is_active': self.is_active_checkbox.isChecked()
        }

    def set_form_data(self, data):
        """Установить данные в форму"""
        self.code_input.setText(data.get('code', ''))
        self.name_input.setText(data.get('name', ''))

        # Устанавливаем тип материала
        material_type = data.get('material_type', '')
        if material_type:
            index = self.material_type_combo.findText(material_type)
            if index >= 0:
                self.material_type_combo.setCurrentIndex(index)
            else:
                self.material_type_combo.setCurrentText(material_type)

        # Толщина
        thickness = data.get('thickness')
        if thickness is not None:
            self.thickness_input.setText(str(thickness))

        self.description_input.setPlainText(data.get('description', ''))
        self.is_active_checkbox.setChecked(data.get('is_active', True))

    def validate_form(self):
        """Валидация формы"""
        errors = []

        if not self.code_input.text().strip():
            errors.append("Код обязателен для заполнения")

        if not self.name_input.text().strip():
            errors.append("Название обязательно для заполнения")

        if not self.material_type_combo.currentText().strip():
            errors.append("Тип материала обязателен для заполнения")

        # Проверка толщины
        thickness_text = self.thickness_input.text().strip()
        if thickness_text:
            try:
                thickness = float(thickness_text)
                if thickness <= 0:
                    errors.append("Толщина должна быть больше 0")
            except ValueError:
                errors.append("Толщина должна быть числом")

        # Проверка уникальности кода
        code = self.code_input.text().strip()
        if code:
            db = DatabaseConnection()
            conn = db.get_connection()
            try:
                cursor = conn.cursor()
                if self.record_data:  # Редактирование
                    cursor.execute(
                        "SELECT id FROM lining_types WHERE code = %s AND id != %s",
                        (code, self.record_data['id'])
                    )
                else:  # Добавление
                    cursor.execute(
                        "SELECT id FROM lining_types WHERE code = %s",
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
    window = LiningTypesTableWidget()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()