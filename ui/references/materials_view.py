"""Materials reference view for PyQt6 application"""
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
from ui.base.base_table import BaseTableWidget
from ui.base.base_form import BaseFormDialog

class MaterialsTableWidget(BaseTableWidget):
    """Таблица материалов"""

    def __init__(self, parent=None):
        super().__init__('materials', parent)
        self.setWindowTitle("Материалы")

        # Фильтр по группам
        self.setup_group_filter()

        # Настройка колонок
        if self.model:
            self.model.setHeaderData(1, Qt.Orientation.Horizontal, "Код")
            self.model.setHeaderData(2, Qt.Orientation.Horizontal, "Название")
            self.model.setHeaderData(3, Qt.Orientation.Horizontal, "Группа")
            self.model.setHeaderData(4, Qt.Orientation.Horizontal, "Ед.изм.")
            self.model.setHeaderData(5, Qt.Orientation.Horizontal, "Цена")

    def setup_group_filter(self):
        """Добавляем фильтр по группам в toolbar"""
        self.group_filter = QComboBox()
        self.group_filter.addItem("Все группы", None)
        self.group_filter.addItems([
            "Кожа", "Подошва", "Фурнитура",
            "Химия", "Упаковка", "Подкладка"
        ])

        self.group_filter.currentIndexChanged.connect(self.filter_by_group)

        # Вставляем после поиска
        toolbar = self.layout().itemAt(0).layout()
        toolbar.insertWidget(1, QLabel("Группа:"))
        toolbar.insertWidget(2, self.group_filter)

    def filter_by_group(self):
        """Фильтрация по группе"""
        group_text = self.group_filter.currentText()
        if group_text != "Все группы":
            self.model.setFilter(f"group_type ILIKE '%{group_text}%'")
        else:
            self.model.setFilter("")
        self.model.select()

    def build_filter_string(self, text: str) -> str:
        return f"code ILIKE '%{text}%' OR name ILIKE '%{text}%'"

    def add_record(self):
        dialog = MaterialFormDialog("Новый материал", self)
        if dialog.exec():
            self.refresh_data()

class MaterialFormDialog(BaseFormDialog):
    """Форма редактирования материала"""

    def __init__(self, title: str, parent=None):
        super().__init__(title, parent)
        self.resize(600, 500)

    def create_form_content(self):
        form_layout = QFormLayout()

        self.code_input = QLineEdit()
        self.name_input = QLineEdit()

        self.group_combo = QComboBox()
        self.group_combo.addItems([
            "Кожа", "Подошва", "Фурнитура",
            "Химия", "Упаковка", "Подкладка"
        ])

        self.unit_combo = QComboBox()
        self.unit_combo.addItems(["шт", "пара", "м", "дм²", "кг", "л", "компл"])

        self.price_input = QDoubleSpinBox()
        self.price_input.setRange(0, 999999)
        self.price_input.setSuffix(" ₽")
        self.price_input.setDecimals(2)

        self.supplier_input = QLineEdit()

        self.safety_stock = QSpinBox()
        self.safety_stock.setRange(0, 9999)
        self.safety_stock.setSuffix(" ед.")

        self.lead_time = QSpinBox()
        self.lead_time.setRange(0, 365)
        self.lead_time.setSuffix(" дней")
        self.lead_time.setValue(7)

        form_layout.addRow("Код:", self.code_input)
        form_layout.addRow("Название:", self.name_input)
        form_layout.addRow("Группа:", self.group_combo)
        form_layout.addRow("Ед. измерения:", self.unit_combo)
        form_layout.addRow("Цена:", self.price_input)
        form_layout.addRow("Поставщик:", self.supplier_input)
        form_layout.addRow("Мин. остаток:", self.safety_stock)
        form_layout.addRow("Срок поставки:", self.lead_time)

        # Добавим описание
        self.description_text = QTextEdit()
        self.description_text.setMaximumHeight(100)
        form_layout.addRow("Описание:", self.description_text)

        self.layout.addLayout(form_layout)

    def save_data(self):
        if not self.validate():
            return

        # В демо-режиме просто закрываем
        QMessageBox.information(self, "Сохранение",
                              f"Материал '{self.code_input.text()}' сохранен (демо-режим)")
        self.accept()

    def validate(self) -> bool:
        if not self.code_input.text():
            QMessageBox.warning(self, "Ошибка", "Укажите код материала")
            return False
        if not self.name_input.text():
            QMessageBox.warning(self, "Ошибка", "Укажите название материала")
            return False
        return True