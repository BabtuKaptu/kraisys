"""
Улучшенная таблица с поиском, фильтрацией и красивым дизайном
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QLineEdit, QPushButton, QLabel, QComboBox, QHeaderView, QAbstractItemView,
    QMenu, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QAction, QFont
from ui.styles.app_styles import AppColors, AppIcons, AppFonts
from ui.components.enhanced_widgets import StyledButton, ValidatedLineEdit, ButtonGroup


class EnhancedTableWidget(QWidget):
    """Улучшенная таблица с поиском, фильтрацией и современным дизайном"""

    recordSelected = pyqtSignal(int)
    recordDoubleClicked = pyqtSignal(int)

    def __init__(self, title="Данные", parent=None):
        super().__init__(parent)
        self.title = title
        self.data = []
        self.filtered_data = []
        self.current_filters = {}

        self._setup_ui()
        self._setup_styles()

    def _setup_ui(self):
        """Настройка интерфейса"""
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # Заголовок и статистика
        header_layout = QHBoxLayout()

        title_label = QLabel(self.title)
        title_label.setStyleSheet(f"""
            QLabel {{
                font-size: 18px;
                font-weight: 600;
                color: {AppColors.TEXT_PRIMARY};
                margin: 8px 0;
            }}
        """)
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        self.stats_label = QLabel("0 записей")
        self.stats_label.setStyleSheet(f"color: {AppColors.TEXT_SECONDARY};")
        header_layout.addWidget(self.stats_label)

        layout.addLayout(header_layout)

        # Панель инструментов
        toolbar_layout = QHBoxLayout()

        # Поиск
        search_label = QLabel(f"{AppIcons.SEARCH}")
        search_label.setStyleSheet(f"color: {AppColors.TEXT_SECONDARY}; font-size: 16px;")
        toolbar_layout.addWidget(search_label)

        self.search_input = ValidatedLineEdit("Поиск...")
        self.search_input.textChanged.connect(self._on_search_changed)
        self.search_input.setMaximumWidth(300)
        toolbar_layout.addWidget(self.search_input)

        toolbar_layout.addStretch()

        # Кнопки действий
        self.buttons = ButtonGroup()

        self.add_btn = self.buttons.add_button("Добавить", AppIcons.ADD, StyledButton.STYLE_PRIMARY)
        self.edit_btn = self.buttons.add_button("Редактировать", AppIcons.EDIT, StyledButton.STYLE_SECONDARY)
        self.delete_btn = self.buttons.add_button("Удалить", AppIcons.DELETE, StyledButton.STYLE_ERROR)
        self.refresh_btn = self.buttons.add_button("Обновить", AppIcons.REFRESH, StyledButton.STYLE_SECONDARY)

        # Подключение сигналов
        self.add_btn.clicked.connect(self.add_record)
        self.edit_btn.clicked.connect(self.edit_record)
        self.delete_btn.clicked.connect(self.delete_record)
        self.refresh_btn.clicked.connect(self.refresh_data)

        toolbar_layout.addWidget(self.buttons)
        layout.addLayout(toolbar_layout)

        # Таблица
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setSortingEnabled(True)

        # Подключение сигналов таблицы
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        self.table.doubleClicked.connect(self._on_double_clicked)

        layout.addWidget(self.table)

        # Нижняя панель с информацией
        footer_layout = QHBoxLayout()

        self.status_label = QLabel(f"{AppIcons.SUCCESS} Готово")
        self.status_label.setStyleSheet(f"color: {AppColors.TEXT_SECONDARY}; font-size: 12px;")
        footer_layout.addWidget(self.status_label)

        footer_layout.addStretch()

        # Быстрые фильтры
        filter_label = QLabel("Фильтр:")
        filter_label.setStyleSheet(f"color: {AppColors.TEXT_SECONDARY};")
        footer_layout.addWidget(filter_label)

        self.quick_filter = QComboBox()
        self.quick_filter.addItem("Все записи", "all")
        self.quick_filter.currentTextChanged.connect(self._on_filter_changed)
        footer_layout.addWidget(self.quick_filter)

        layout.addLayout(footer_layout)

    def _setup_styles(self):
        """Настройка стилей таблицы"""
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {AppColors.SURFACE};
                alternate-background-color: {AppColors.SURFACE_VARIANT};
                gridline-color: {AppColors.LIGHT_GRAY};
                selection-background-color: {AppColors.PRIMARY_LIGHT};
                color: {AppColors.TEXT_PRIMARY};
                border: 1px solid {AppColors.LIGHT_GRAY};
                border-radius: 8px;
                font-size: 13px;
            }}

            QTableWidget::item {{
                padding: 8px;
                border: none;
            }}

            QTableWidget::item:selected {{
                background-color: {AppColors.PRIMARY_LIGHT};
                color: {AppColors.TEXT_PRIMARY};
            }}

            QHeaderView::section {{
                background-color: {AppColors.SURFACE_VARIANT};
                color: {AppColors.TEXT_PRIMARY};
                padding: 10px 8px;
                border: none;
                border-bottom: 2px solid {AppColors.PRIMARY};
                font-weight: 600;
                font-size: 13px;
            }}

            QHeaderView::section:hover {{
                background-color: {AppColors.PRIMARY_LIGHT};
            }}

            QHeaderView::section:pressed {{
                background-color: {AppColors.PRIMARY};
                color: {AppColors.TEXT_ON_PRIMARY};
            }}
        """)

    def set_columns(self, headers):
        """Установка заголовков колонок"""
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)

        # Настройка растягивания колонок
        header = self.table.horizontalHeader()
        for i, _ in enumerate(headers):
            if i == 0:  # Первая колонка - фиксированная ширина
                header.setSectionResizeMode(i, QHeaderView.ResizeMode.Fixed)
                header.resizeSection(i, 60)
            elif i == len(headers) - 1:  # Последняя колонка - растягивается
                header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)
            else:  # Остальные - по содержимому
                header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)

    def set_data(self, data):
        """Установка данных"""
        self.data = data
        self.filtered_data = data[:]
        self._update_table_display()
        self._update_stats()

    def _update_table_display(self):
        """Обновление отображения таблицы"""
        self.table.setRowCount(len(self.filtered_data))

        for row, record in enumerate(self.filtered_data):
            for col, value in enumerate(record):
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)  # Только чтение
                self.table.setItem(row, col, item)

    def _update_stats(self):
        """Обновление статистики"""
        total = len(self.data)
        filtered = len(self.filtered_data)

        if total == filtered:
            self.stats_label.setText(f"{total} записей")
        else:
            self.stats_label.setText(f"{filtered} из {total} записей")

    def _on_search_changed(self):
        """Обработка изменения поиска"""
        search_text = self.search_input.text().lower()

        if not search_text:
            self.filtered_data = self.data[:]
        else:
            self.filtered_data = []
            for record in self.data:
                # Поиск по всем колонкам
                if any(search_text in str(value).lower() for value in record):
                    self.filtered_data.append(record)

        self._update_table_display()
        self._update_stats()

    def _on_filter_changed(self):
        """Обработка изменения фильтра"""
        filter_value = self.quick_filter.currentData()

        # Здесь можно добавить логику фильтрации
        # Пока просто обновляем поиск
        self._on_search_changed()

    def _on_selection_changed(self):
        """Обработка изменения выделения"""
        current_row = self.table.currentRow()
        has_selection = current_row >= 0

        # Включение/отключение кнопок
        self.edit_btn.setEnabled(has_selection)
        self.delete_btn.setEnabled(has_selection)

        if has_selection and current_row < len(self.filtered_data):
            # Получаем ID из первой колонки
            record_id = self.filtered_data[current_row][0]
            self.recordSelected.emit(record_id)

    def _on_double_clicked(self):
        """Обработка двойного клика"""
        current_row = self.table.currentRow()
        if current_row >= 0 and current_row < len(self.filtered_data):
            record_id = self.filtered_data[current_row][0]
            self.recordDoubleClicked.emit(record_id)

    def get_current_record_id(self):
        """Получение ID текущей записи"""
        current_row = self.table.currentRow()
        if current_row >= 0 and current_row < len(self.filtered_data):
            return self.filtered_data[current_row][0]
        return None

    def set_status(self, message, icon=AppIcons.INFO):
        """Установка статуса"""
        self.status_label.setText(f"{icon} {message}")

    def add_quick_filter(self, name, value):
        """Добавление быстрого фильтра"""
        self.quick_filter.addItem(name, value)

    # Методы для переопределения в наследниках
    def add_record(self):
        """Добавление записи (переопределить в наследнике)"""
        self.set_status("Добавление записи...", AppIcons.ADD)

    def edit_record(self):
        """Редактирование записи (переопределить в наследнике)"""
        record_id = self.get_current_record_id()
        if record_id:
            self.set_status(f"Редактирование записи #{record_id}...", AppIcons.EDIT)

    def delete_record(self):
        """Удаление записи (переопределить в наследнике)"""
        record_id = self.get_current_record_id()
        if not record_id:
            return

        reply = QMessageBox.question(
            self,
            "Подтверждение",
            f"Удалить запись #{record_id}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.set_status(f"Удаление записи #{record_id}...", AppIcons.DELETE)

    def refresh_data(self):
        """Обновление данных (переопределить в наследнике)"""
        self.set_status("Обновление данных...", AppIcons.REFRESH)


class DatabaseTableWidget(EnhancedTableWidget):
    """Таблица для работы с базой данных"""

    def __init__(self, table_name, db_connection=None, title="", parent=None):
        self.table_name = table_name
        self.db = db_connection
        super().__init__(title or table_name, parent)

    def load_data_from_db(self):
        """Загрузка данных из базы данных"""
        if not self.db:
            self.set_status("Нет подключения к БД", AppIcons.ERROR)
            return

        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            # Простой запрос для получения всех данных
            cursor.execute(f"SELECT * FROM {self.table_name} ORDER BY id")
            data = cursor.fetchall()

            # Получение названий колонок
            columns = [desc[0] for desc in cursor.description]

            cursor.close()
            conn.close()

            self.set_columns(columns)
            self.set_data(data)
            self.set_status(f"Загружено {len(data)} записей", AppIcons.SUCCESS)

        except Exception as e:
            self.set_status(f"Ошибка загрузки: {e}", AppIcons.ERROR)

    def refresh_data(self):
        """Обновление данных из БД"""
        self.load_data_from_db()