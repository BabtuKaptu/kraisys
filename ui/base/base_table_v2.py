"""Base table widget v2 using psycopg2 and custom model"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                            QTableWidget, QTableWidgetItem, QLineEdit, QHeaderView,
                            QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal
from database.connection import DatabaseConnection
import psycopg2.extras

class BaseTableWidgetV2(QWidget):
    """Базовый класс для табличных представлений с прямым SQL"""

    # Сигналы
    recordSelected = pyqtSignal(int)
    recordDoubleClicked = pyqtSignal(int)

    def __init__(self, table_name: str, parent=None):
        super().__init__(parent)
        self.table_name = table_name
        self.db = DatabaseConnection()
        self.data = []
        self.columns = []
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Панель инструментов
        toolbar = QHBoxLayout()

        # Поиск
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск...")
        self.search_input.textChanged.connect(self.filter_data)
        toolbar.addWidget(self.search_input)

        # Кнопки
        self.btn_add = QPushButton("➕ Добавить")
        self.btn_edit = QPushButton("✏️ Изменить")
        self.btn_delete = QPushButton("🗑 Удалить")
        self.btn_refresh = QPushButton("🔄 Обновить")

        self.btn_add.clicked.connect(self.add_record)
        self.btn_edit.clicked.connect(self.edit_record)
        self.btn_delete.clicked.connect(self.delete_record)
        self.btn_refresh.clicked.connect(self.refresh_data)

        toolbar.addWidget(self.btn_add)
        toolbar.addWidget(self.btn_edit)
        toolbar.addWidget(self.btn_delete)
        toolbar.addWidget(self.btn_refresh)
        toolbar.addStretch()

        layout.addLayout(toolbar)

        # Таблица
        self.table_widget = QTableWidget()
        self.table_widget.setAlternatingRowColors(True)
        self.table_widget.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table_widget.setSortingEnabled(True)
        self.table_widget.doubleClicked.connect(self.on_double_click)
        layout.addWidget(self.table_widget)

    def load_data(self):
        """Загрузка данных из БД"""
        try:
            conn = self.db.get_connection()
            if not conn:
                print(f"Failed to get connection for table {self.table_name}")
                return

            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

            # Получаем список колонок
            cursor.execute(f"""
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_name = %s
                ORDER BY ordinal_position
            """, (self.table_name,))

            self.columns = [(row['column_name'], row['data_type']) for row in cursor.fetchall()]

            # Загружаем данные
            cursor.execute(f"SELECT * FROM {self.table_name} ORDER BY id DESC LIMIT 1000")
            self.data = cursor.fetchall()

            cursor.close()
            self.db.put_connection(conn)

            self.update_table()

        except Exception as e:
            print(f"Error loading data from {self.table_name}: {e}")
            self.columns = []
            self.data = []

    def update_table(self):
        """Обновление виджета таблицы"""
        if not self.columns:
            return

        # Настраиваем колонки
        visible_columns = self.get_visible_columns()
        self.table_widget.setColumnCount(len(visible_columns))
        self.table_widget.setHorizontalHeaderLabels([self.get_column_label(col) for col in visible_columns])

        # Заполняем данные
        self.table_widget.setRowCount(len(self.data))
        for row_idx, row_data in enumerate(self.data):
            for col_idx, col_name in enumerate(visible_columns):
                value = row_data.get(col_name, '')
                item = QTableWidgetItem(str(value) if value is not None else '')
                self.table_widget.setItem(row_idx, col_idx, item)

        # Авторазмер колонок
        header = self.table_widget.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        header.setStretchLastSection(True)

    def get_visible_columns(self):
        """Получить список видимых колонок"""
        # Скрываем технические поля
        hidden = ['id', 'uuid', 'created_at', 'updated_at', 'created_by',
                 'import_batch', 'excel_row_id', 'version']
        return [col[0] for col in self.columns if col[0] not in hidden]

    def get_column_label(self, column_name):
        """Получить красивое название колонки"""
        labels = {
            'article': 'Артикул',
            'name': 'Название',
            'gender': 'Пол',
            'model_type': 'Тип',
            'category': 'Категория',
            'collection': 'Коллекция',
            'season': 'Сезон',
            'retail_price': 'Розница',
            'wholesale_price': 'Опт',
            'is_active': 'Активен',
            'size_min': 'Размер от',
            'size_max': 'Размер до',
            'material_cost': 'Себестоимость',
            'labor_cost': 'Работа',
            'overhead_cost': 'Накладные'
        }
        return labels.get(column_name, column_name.replace('_', ' ').title())

    def filter_data(self, text: str):
        """Фильтрация данных"""
        if not text:
            self.load_data()
            return

        try:
            conn = self.db.get_connection()
            if not conn:
                return

            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

            # Строим условие поиска
            search_columns = self.get_search_columns()
            conditions = " OR ".join([f"{col} ILIKE %s" for col in search_columns])
            search_param = f"%{text}%"
            params = [search_param] * len(search_columns)

            query = f"SELECT * FROM {self.table_name} WHERE {conditions} ORDER BY id DESC LIMIT 1000"
            cursor.execute(query, params)

            self.data = cursor.fetchall()
            cursor.close()
            self.db.put_connection(conn)

            self.update_table()

        except Exception as e:
            print(f"Error filtering data: {e}")

    def get_search_columns(self):
        """Получить колонки для поиска"""
        # Переопределить в наследниках
        return ['article', 'name']

    def get_current_record_id(self) -> int:
        """Получить ID текущей записи"""
        row = self.table_widget.currentRow()
        if row >= 0 and row < len(self.data):
            return self.data[row].get('id')
        return None

    def add_record(self):
        """Добавить запись (переопределить в наследниках)"""
        pass

    def edit_record(self):
        """Редактировать запись"""
        record_id = self.get_current_record_id()
        if record_id:
            self.recordSelected.emit(record_id)

    def delete_record(self):
        """Удалить запись"""
        record_id = self.get_current_record_id()
        if not record_id:
            QMessageBox.warning(self, "Внимание", "Выберите запись для удаления")
            return

        reply = QMessageBox.question(self, "Подтверждение",
                                    "Удалить выбранную запись?",
                                    QMessageBox.StandardButton.Yes |
                                    QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            try:
                conn = self.db.get_connection()
                cursor = conn.cursor()
                cursor.execute(f"DELETE FROM {self.table_name} WHERE id = %s", (record_id,))
                conn.commit()
                cursor.close()
                self.db.put_connection(conn)

                self.refresh_data()
                QMessageBox.information(self, "Успешно", "Запись удалена")

            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить запись: {e}")

    def refresh_data(self):
        """Обновить данные"""
        self.load_data()

    def on_double_click(self):
        """Обработка двойного клика"""
        record_id = self.get_current_record_id()
        if record_id:
            self.recordDoubleClicked.emit(record_id)