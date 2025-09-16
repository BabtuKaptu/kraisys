"""CRUD form for cutting parts reference"""
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
from ui.base.base_table_v2 import BaseTableWidgetV2
from ui.base.crud_form import CrudFormDialog
from database.connection import DatabaseConnection
import psycopg2.extras


class CuttingPartsTableWidget(BaseTableWidgetV2):
    """Таблица деталей раскроя с интеграцией БД"""

    def __init__(self, parent=None):
        super().__init__('cutting_parts', parent)
        self.setWindowTitle("Справочник деталей раскроя")

    def get_visible_columns(self):
        """Видимые колонки для деталей раскроя"""
        return ['code', 'name', 'category', 'material_consumption', 'material_name', 'notes', 'is_active']

    def get_column_label(self, column_name):
        """Метки колонок для деталей раскроя"""
        labels = {
            'code': 'Код',
            'name': 'Название',
            'category': 'Категория',
            'material_consumption': 'Расход материала',
            'material_name': 'Материал',
            'notes': 'Описание',
            'is_active': 'Активен'
        }
        return labels.get(column_name, column_name)

    def load_data(self):
        """Загрузка данных из БД с JOIN для материалов"""
        try:
            conn = self.db.get_connection()
            if not conn:
                print(f"Failed to get connection for table {self.table_name}")
                return

            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

            # Загружаем данные с JOIN к таблице материалов
            cursor.execute("""
                SELECT
                    c.id,
                    c.code,
                    c.name,
                    c.category,
                    c.material_consumption,
                    c.material_id,
                    m.name as material_name,
                    c.notes,
                    c.is_active,
                    c.created_at,
                    c.updated_at
                FROM cutting_parts c
                LEFT JOIN materials m ON c.material_id = m.id
                ORDER BY c.id DESC LIMIT 1000
            """)

            self.data = cursor.fetchall()

            # Устанавливаем колонки для таблицы
            self.columns = [
                ('id', 'integer'),
                ('code', 'character varying'),
                ('name', 'character varying'),
                ('category', 'character varying'),
                ('material_consumption', 'numeric'),
                ('material_id', 'integer'),
                ('material_name', 'character varying'),
                ('notes', 'text'),
                ('is_active', 'boolean'),
                ('created_at', 'timestamp'),
                ('updated_at', 'timestamp')
            ]

            cursor.close()
            self.db.put_connection(conn)

            self.update_table()

        except Exception as e:
            print(f"Error loading data from {self.table_name}: {e}")
            self.columns = []
            self.data = []

    def create_edit_form(self, record_data=None):
        """Создать форму редактирования"""
        return CuttingPartEditForm(record_data, self)

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


class CuttingPartEditForm(CrudFormDialog):
    """Форма редактирования детали раскроя"""

    def __init__(self, record_data=None, parent=None):
        # ВАЖНО: table_name должен быть установлен ДО вызова super().__init__()
        self.table_name = 'cutting_parts'
        super().__init__(record_data, parent)

        title = "Редактирование детали раскроя" if record_data else "Добавление детали раскроя"
        self.setWindowTitle(title)
        self.setFixedSize(500, 450)

    def create_form_fields(self):
        """Создание полей формы"""
        layout = QFormLayout()

        # Код
        self.code_input = QLineEdit()
        self.code_input.setMaxLength(20)
        self.code_input.setPlaceholderText("Например: CUT-001")
        layout.addRow("Код:", self.code_input)

        # Название
        self.name_input = QLineEdit()
        self.name_input.setMaxLength(100)
        self.name_input.setPlaceholderText("Например: Передняя часть")
        layout.addRow("Название:", self.name_input)

        # Категория
        self.category_combo = QComboBox()
        self.category_combo.addItems([
            "Верх",
            "Подкладка",
            "Стелька",
            "Задник",
            "Подносок",
            "Союзка",
            "Берцы",
            "Язычок",
            "Манжета",
            "Другое"
        ])
        self.category_combo.setEditable(True)
        layout.addRow("Категория:", self.category_combo)

        # Расход материала
        self.material_consumption_input = QDoubleSpinBox()
        self.material_consumption_input.setRange(0.0001, 9999.9999)
        self.material_consumption_input.setDecimals(4)
        self.material_consumption_input.setSuffix(" м²")
        self.material_consumption_input.setValue(0.0)
        layout.addRow("Расход материала:", self.material_consumption_input)

        # Материал
        self.material_combo = QComboBox()
        self.material_combo.setEditable(False)
        self.load_materials()
        layout.addRow("Материал:", self.material_combo)

        # Описание
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(80)
        self.description_input.setPlaceholderText("Описание детали раскроя...")
        layout.addRow("Описание:", self.description_input)

        # Активен
        self.is_active_checkbox = QCheckBox()
        self.is_active_checkbox.setChecked(True)
        layout.addRow("Активен:", self.is_active_checkbox)

        return layout

    def load_materials(self):
        """Загружает материалы (кожа и ткань) в комбобокс"""
        try:
            db = DatabaseConnection()
            conn = db.get_connection()
            cursor = conn.cursor()

            # Получаем только кожу и ткань
            cursor.execute("""
                SELECT id, name, type_name
                FROM materials
                WHERE type_name IN ('Кожа', 'Ткань')
                AND is_active = true
                ORDER BY type_name, name
            """)

            materials = cursor.fetchall()

            # Очищаем комбобокс
            self.material_combo.clear()
            self.material_combo.addItem("-- Выберите материал --", None)

            # Добавляем материалы
            for material_id, name, type_name in materials:
                display_text = f"{type_name}: {name}"
                self.material_combo.addItem(display_text, material_id)

            cursor.close()
            db.put_connection(conn)

        except Exception as e:
            print(f"Ошибка загрузки материалов: {e}")
            self.material_combo.clear()
            self.material_combo.addItem("Ошибка загрузки", None)

    def get_form_data(self):
        """Получить данные из формы"""
        material_id = self.material_combo.currentData()
        return {
            'code': self.code_input.text().strip(),
            'name': self.name_input.text().strip(),
            'category': self.category_combo.currentText().strip(),
            'material_consumption': self.material_consumption_input.value() if self.material_consumption_input.value() > 0 else None,
            'material_id': material_id if material_id else None,
            'notes': self.description_input.toPlainText().strip(),
            'is_active': self.is_active_checkbox.isChecked()
        }

    def set_form_data(self, data):
        """Установить данные в форму"""
        self.code_input.setText(data.get('code', ''))
        self.name_input.setText(data.get('name', ''))

        # Устанавливаем категорию
        category = data.get('category', '')
        if category:
            index = self.category_combo.findText(category)
            if index >= 0:
                self.category_combo.setCurrentIndex(index)
            else:
                self.category_combo.setCurrentText(category)

        # Устанавливаем расход материала
        material_consumption = data.get('material_consumption')
        if material_consumption is not None:
            self.material_consumption_input.setValue(float(material_consumption))
        else:
            self.material_consumption_input.setValue(0.0)

        # Устанавливаем материал
        material_id = data.get('material_id')
        if material_id:
            # Ищем элемент с нужным material_id
            for i in range(self.material_combo.count()):
                if self.material_combo.itemData(i) == material_id:
                    self.material_combo.setCurrentIndex(i)
                    break

        self.description_input.setPlainText(data.get('notes', ''))
        self.is_active_checkbox.setChecked(data.get('is_active', True))

    def validate_form(self):
        """Валидация формы"""
        errors = []

        if not self.code_input.text().strip():
            errors.append("Код обязателен для заполнения")

        if not self.name_input.text().strip():
            errors.append("Название обязательно для заполнения")

        if not self.category_combo.currentText().strip():
            errors.append("Категория обязательна для заполнения")

        # Проверка уникальности кода
        code = self.code_input.text().strip()
        if code:
            db = DatabaseConnection()
            conn = db.get_connection()
            try:
                cursor = conn.cursor()
                if self.record_data:  # Редактирование
                    cursor.execute(
                        "SELECT id FROM cutting_parts WHERE code = %s AND id != %s",
                        (code, self.record_data['id'])
                    )
                else:  # Добавление
                    cursor.execute(
                        "SELECT id FROM cutting_parts WHERE code = %s",
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
    window = CuttingPartsTableWidget()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()