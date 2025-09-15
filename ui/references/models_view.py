"""Models reference view for PyQt6 application"""
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
from PyQt6.QtSql import QSqlTableModel
from ui.base.base_table import BaseTableWidget
from ui.base.base_form import BaseFormDialog
# from models.models import Model
# from services.database import DatabaseService

class ModelsTableWidget(BaseTableWidget):
    """Таблица моделей обуви"""

    def __init__(self, parent=None):
        super().__init__('models', parent)
        self.setWindowTitle("Модели обуви")

        # Настройка отображения колонок
        if self.model:
            self.model.setHeaderData(1, Qt.Orientation.Horizontal, "Артикул")
            self.model.setHeaderData(2, Qt.Orientation.Horizontal, "Название")
            self.model.setHeaderData(3, Qt.Orientation.Horizontal, "Тип")
            self.model.setHeaderData(4, Qt.Orientation.Horizontal, "Категория")
            self.model.setHeaderData(5, Qt.Orientation.Horizontal, "Розничная цена")

    def build_filter_string(self, text: str) -> str:
        return f"article ILIKE '%{text}%' OR name ILIKE '%{text}%'"

    def add_record(self):
        dialog = ModelFormDialog("Новая модель", self)
        if dialog.exec():
            self.refresh_data()

    def edit_record(self):
        record_id = self.get_current_id()
        if record_id:
            dialog = ModelFormDialog("Редактирование модели", self)
            dialog.load_data(record_id)
            if dialog.exec():
                self.refresh_data()

class ModelFormDialog(BaseFormDialog):
    """Форма редактирования модели"""

    def __init__(self, title: str, parent=None):
        self.record_id = None
        super().__init__(title, parent)
        self.resize(800, 600)

    def create_form_content(self):
        # Табы для группировки полей
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        # Вкладка "Основные данные"
        self.create_main_tab()

        # Вкладка "Характеристики"
        self.create_specs_tab()

        # Вкладка "Цены"
        self.create_prices_tab()

    def create_main_tab(self):
        tab = QWidget()
        layout = QFormLayout(tab)

        self.article_input = QLineEdit()
        self.name_input = QLineEdit()
        self.gender_combo = QComboBox()
        self.gender_combo.addItems(["", "Мужская", "Женская", "Унисекс", "Детская"])
        self.type_input = QLineEdit()
        self.category_input = QLineEdit()

        layout.addRow("Артикул:", self.article_input)
        layout.addRow("Название:", self.name_input)
        layout.addRow("Пол:", self.gender_combo)
        layout.addRow("Тип:", self.type_input)
        layout.addRow("Категория:", self.category_input)

        # Размерный ряд
        size_group = QGroupBox("Размерный ряд")
        size_layout = QHBoxLayout(size_group)

        self.size_min = QSpinBox()
        self.size_min.setRange(20, 50)
        self.size_min.setValue(36)

        self.size_max = QSpinBox()
        self.size_max.setRange(20, 50)
        self.size_max.setValue(46)

        size_layout.addWidget(QLabel("От:"))
        size_layout.addWidget(self.size_min)
        size_layout.addWidget(QLabel("До:"))
        size_layout.addWidget(self.size_max)
        size_layout.addStretch()

        layout.addRow(size_group)

        self.tabs.addTab(tab, "Основные данные")

    def create_specs_tab(self):
        tab = QWidget()
        layout = QFormLayout(tab)

        self.last_code_input = QLineEdit()
        self.last_type_combo = QComboBox()
        self.last_type_combo.addItems(["", "Ботиночная", "Туфельная", "Сапожная", "Спортивная"])
        self.assembly_combo = QComboBox()
        self.assembly_combo.addItems(["", "Заготовочно-нашивной", "Клеевой", "Прошивной", "Литьевой"])
        self.sole_type_input = QLineEdit()

        layout.addRow("Код колодки:", self.last_code_input)
        layout.addRow("Тип колодки:", self.last_type_combo)
        layout.addRow("Метод крепления:", self.assembly_combo)
        layout.addRow("Тип подошвы:", self.sole_type_input)

        self.tabs.addTab(tab, "Характеристики")

    def create_prices_tab(self):
        tab = QWidget()
        layout = QFormLayout(tab)

        self.retail_price = QDoubleSpinBox()
        self.retail_price.setRange(0, 999999)
        self.retail_price.setSuffix(" ₽")
        self.retail_price.setDecimals(2)

        self.wholesale_price = QDoubleSpinBox()
        self.wholesale_price.setRange(0, 999999)
        self.wholesale_price.setSuffix(" ₽")
        self.wholesale_price.setDecimals(2)

        layout.addRow("Розничная цена:", self.retail_price)
        layout.addRow("Оптовая цена:", self.wholesale_price)

        # Добавим расчет маржи
        self.margin_label = QLabel("Маржа: 0%")
        layout.addRow(self.margin_label)

        # Обновление маржи при изменении цен
        self.retail_price.valueChanged.connect(self.calculate_margin)
        self.wholesale_price.valueChanged.connect(self.calculate_margin)

        self.tabs.addTab(tab, "Цены")

    def calculate_margin(self):
        """Расчет маржи"""
        if self.wholesale_price.value() > 0:
            margin = ((self.retail_price.value() - self.wholesale_price.value()) /
                     self.wholesale_price.value() * 100)
            self.margin_label.setText(f"Маржа: {margin:.1f}%")
        else:
            self.margin_label.setText("Маржа: 0%")

    def save_data(self):
        if not self.validate():
            return

        # В демо-режиме просто закрываем диалог
        QMessageBox.information(self, "Сохранение",
                              f"Модель '{self.article_input.text()}' сохранена (демо-режим)")
        self.accept()

    def load_data(self, record_id: int):
        """Загрузка данных для редактирования"""
        self.record_id = record_id
        # В демо-режиме загружаем тестовые данные
        self.article_input.setText("TEST-001")
        self.name_input.setText("Тестовая модель")

    def validate(self) -> bool:
        if not self.article_input.text():
            QMessageBox.warning(self, "Ошибка", "Укажите артикул")
            return False
        if not self.name_input.text():
            QMessageBox.warning(self, "Ошибка", "Укажите название")
            return False
        return True