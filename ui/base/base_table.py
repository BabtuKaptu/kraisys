"""Base table widget for PyQt6 application"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableView, QLineEdit
from PyQt6.QtSql import QSqlTableModel, QSqlQuery
from PyQt6.QtCore import Qt, pyqtSignal

class BaseTableWidget(QWidget):
    """Базовый класс для табличных представлений"""

    # Сигналы
    recordSelected = pyqtSignal(int)  # ID выбранной записи
    recordDoubleClicked = pyqtSignal(int)

    def __init__(self, table_name: str, parent=None):
        super().__init__(parent)
        self.table_name = table_name
        self.model = None
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
        self.btn_add = QPushButton("Добавить")
        self.btn_edit = QPushButton("Изменить")
        self.btn_delete = QPushButton("Удалить")
        self.btn_refresh = QPushButton("Обновить")

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
        self.table_view = QTableView()
        self.table_view.setAlternatingRowColors(True)
        self.table_view.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.table_view.setSortingEnabled(True)
        self.table_view.doubleClicked.connect(self.on_double_click)
        layout.addWidget(self.table_view)

    def load_data(self):
        """Загрузка данных в таблицу"""
        self.model = QSqlTableModel()
        self.model.setTable(self.table_name)
        self.model.setEditStrategy(QSqlTableModel.EditStrategy.OnManualSubmit)
        self.model.select()

        self.table_view.setModel(self.model)
        self.table_view.resizeColumnsToContents()

        # Скрываем технические колонки
        self.hide_columns(['id', 'uuid', 'created_at', 'updated_at'])

    def hide_columns(self, columns: list):
        """Скрыть указанные колонки"""
        for col in columns:
            for i in range(self.model.columnCount()):
                if self.model.headerData(i, Qt.Orientation.Horizontal) == col:
                    self.table_view.hideColumn(i)

    def filter_data(self, text: str):
        """Фильтрация данных"""
        if text:
            filter_str = self.build_filter_string(text)
            self.model.setFilter(filter_str)
        else:
            self.model.setFilter("")
        self.model.select()

    def build_filter_string(self, text: str) -> str:
        """Построение строки фильтра (переопределить в наследниках)"""
        return f"name ILIKE '%{text}%' OR code ILIKE '%{text}%'"

    def get_current_id(self) -> int:
        """Получить ID текущей записи"""
        index = self.table_view.currentIndex()
        if index.isValid():
            return self.model.data(self.model.index(index.row(), 0))
        return None

    def add_record(self):
        """Добавить запись (переопределить в наследниках)"""
        pass

    def edit_record(self):
        """Редактировать запись (переопределить в наследниках)"""
        record_id = self.get_current_id()
        if record_id:
            self.recordSelected.emit(record_id)

    def delete_record(self):
        """Удалить запись"""
        index = self.table_view.currentIndex()
        if index.isValid():
            self.model.removeRow(index.row())
            self.model.submitAll()

    def refresh_data(self):
        """Обновить данные"""
        self.model.select()

    def on_double_click(self):
        """Обработка двойного клика"""
        record_id = self.get_current_id()
        if record_id:
            self.recordDoubleClicked.emit(record_id)