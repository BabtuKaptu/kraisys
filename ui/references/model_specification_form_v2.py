"""Правильная форма создания модели обуви с выбором из справочников"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QFormLayout, QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox,
    QTableWidget, QTableWidgetItem, QPushButton, QTextEdit,
    QLabel, QGroupBox, QCheckBox, QHeaderView, QMessageBox,
    QScrollArea, QGridLayout, QAbstractItemView
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from database.connection import DatabaseConnection
import psycopg2.extras
import json
import uuid


class ModelSpecificationFormV2(QDialog):
    """Форма создания/редактирования модели обуви с выбором из справочников БД"""

    saved = pyqtSignal()

    def __init__(self, model_id=None, parent=None):
        super().__init__(parent)
        self.model_id = model_id
        self.db = DatabaseConnection()

        # Справочники
        self.cutting_parts_list = []  # Список деталей кроя из БД
        self.hardware_list = []  # Список фурнитуры из БД
        self.materials_list = []  # Список всех материалов

        self.setWindowTitle("Карта раскроя модели обуви")
        self.setModal(True)
        self.resize(1400, 900)

        self.setup_ui()
        self.load_reference_data()

        if model_id:
            self.load_model_data()

    def setup_ui(self):
        """Настройка интерфейса"""
        layout = QVBoxLayout(self)

        # Основные данные модели
        header_group = QGroupBox("Основные данные модели")
        header_layout = QGridLayout(header_group)

        # Название и артикул
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Например: Хайкеры М")
        header_layout.addWidget(QLabel("Название:"), 0, 0)
        header_layout.addWidget(self.name_input, 0, 1)

        self.article_input = QLineEdit()
        self.article_input.setPlaceholderText("Артикул модели")
        header_layout.addWidget(QLabel("Артикул:"), 0, 2)
        header_layout.addWidget(self.article_input, 0, 3)

        # Колодка
        self.last_code_input = QLineEdit()
        self.last_code_input.setPlaceholderText("Например: 75")
        header_layout.addWidget(QLabel("Колодка:"), 1, 0)
        header_layout.addWidget(self.last_code_input, 1, 1)

        self.last_type_combo = QComboBox()
        self.last_type_combo.addItems(["Ботиночная", "Туфельная", "Сапожная", "Спортивная"])
        header_layout.addWidget(QLabel("Тип колодки:"), 1, 2)
        header_layout.addWidget(self.last_type_combo, 1, 3)

        # Размерный ряд
        self.size_min_spin = QSpinBox()
        self.size_min_spin.setRange(20, 50)
        self.size_min_spin.setValue(36)
        header_layout.addWidget(QLabel("Размер от:"), 2, 0)
        header_layout.addWidget(self.size_min_spin, 2, 1)

        self.size_max_spin = QSpinBox()
        self.size_max_spin.setRange(20, 50)
        self.size_max_spin.setValue(48)
        header_layout.addWidget(QLabel("Размер до:"), 2, 2)
        header_layout.addWidget(self.size_max_spin, 2, 3)

        layout.addWidget(header_group)

        # Табы для разделов
        self.tabs = QTabWidget()

        # 1. Детали кроя
        self.cutting_tab = self.create_cutting_tab()
        self.tabs.addTab(self.cutting_tab, "✂️ Детали кроя")

        # 2. Фурнитура
        self.hardware_tab = self.create_hardware_tab()
        self.tabs.addTab(self.hardware_tab, "🔧 Фурнитура")

        # 3. Подошвы
        self.sole_tab = self.create_sole_tab()
        self.tabs.addTab(self.sole_tab, "👟 Подошвы")

        # 4. Варианты исполнения
        self.variants_tab = self.create_variants_tab()
        self.tabs.addTab(self.variants_tab, "🎨 Варианты")

        layout.addWidget(self.tabs)

        # Кнопки
        buttons_layout = QHBoxLayout()
        self.save_btn = QPushButton("💾 Сохранить")
        self.save_btn.clicked.connect(self.save_model)
        self.cancel_btn = QPushButton("Отмена")
        self.cancel_btn.clicked.connect(self.reject)

        buttons_layout.addWidget(self.save_btn)
        buttons_layout.addWidget(self.cancel_btn)
        layout.addLayout(buttons_layout)

    def create_cutting_tab(self):
        """Вкладка деталей кроя"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Информация
        info = QLabel(
            "💡 Детали кроя - элементы верха обуви. "
            "Укажите расход материала в дм² и примечания (материал, особенности обработки)"
        )
        info.setWordWrap(True)
        info.setStyleSheet("background: #f0f8ff; padding: 10px; border-radius: 5px;")
        layout.addWidget(info)

        # Панель добавления новой детали
        add_panel = QGroupBox("Добавить деталь кроя")
        add_layout = QHBoxLayout(add_panel)

        # Выпадающий список деталей кроя
        self.cutting_part_combo = QComboBox()
        self.cutting_part_combo.setPlaceholderText("Выберите деталь кроя из справочника...")
        self.cutting_part_combo.setMinimumWidth(250)
        add_layout.addWidget(QLabel("Деталь:"))
        add_layout.addWidget(self.cutting_part_combo)

        # Количество
        self.cutting_qty_spin = QSpinBox()
        self.cutting_qty_spin.setRange(1, 20)
        self.cutting_qty_spin.setValue(2)
        add_layout.addWidget(QLabel("Количество:"))
        add_layout.addWidget(self.cutting_qty_spin)

        # Расход материала
        self.cutting_consumption_spin = QDoubleSpinBox()
        self.cutting_consumption_spin.setRange(0, 999)
        self.cutting_consumption_spin.setDecimals(2)
        self.cutting_consumption_spin.setSuffix(" дм²")
        add_layout.addWidget(QLabel("Расход:"))
        add_layout.addWidget(self.cutting_consumption_spin)

        # Кнопка добавления
        self.add_cutting_btn = QPushButton("➕ Добавить деталь")
        self.add_cutting_btn.clicked.connect(self.add_cutting_part)
        add_layout.addWidget(self.add_cutting_btn)

        add_layout.addStretch()
        layout.addWidget(add_panel)

        # Таблица добавленных деталей кроя
        self.cutting_table = QTableWidget()
        self.cutting_table.setColumnCount(5)
        self.cutting_table.setHorizontalHeaderLabels([
            "Деталировка", "Количество", "Расход (дм²)", "Примечания", "Удалить"
        ])

        # Настройка ширины колонок
        header = self.cutting_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # Деталировка
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)            # Количество
        header.setDefaultSectionSize(100)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)            # Расход
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)          # Примечания
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)            # Удалить

        # Разрешить редактирование всех колонок кроме первой (название детали)
        self.cutting_table.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked | QAbstractItemView.EditTrigger.EditKeyPressed)

        layout.addWidget(self.cutting_table)

        return widget

    def create_hardware_tab(self):
        """Вкладка фурнитуры"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        info = QLabel(
            "💡 Фурнитура и комплектующие. "
            "Выберите из справочника материалов (группа ФУРНИТУРА) и укажите точные параметры"
        )
        info.setWordWrap(True)
        info.setStyleSheet("background: #f0f8ff; padding: 10px; border-radius: 5px;")
        layout.addWidget(info)

        # Панель добавления фурнитуры
        add_panel = QGroupBox("Добавить фурнитуру")
        add_layout = QHBoxLayout(add_panel)

        # Выпадающий список фурнитуры из материалов
        self.hardware_combo = QComboBox()
        self.hardware_combo.setPlaceholderText("Выберите фурнитуру из справочника материалов...")
        self.hardware_combo.setMinimumWidth(350)
        add_layout.addWidget(QLabel("Фурнитура:"))
        add_layout.addWidget(self.hardware_combo)

        # Количество (числовое поле)
        self.hardware_qty_spin = QDoubleSpinBox()
        self.hardware_qty_spin.setRange(0, 9999)
        self.hardware_qty_spin.setDecimals(2)
        self.hardware_qty_spin.setValue(1)
        add_layout.addWidget(QLabel("Количество:"))
        add_layout.addWidget(self.hardware_qty_spin)

        # Кнопка добавления
        self.add_hardware_btn = QPushButton("➕ Добавить фурнитуру")
        self.add_hardware_btn.clicked.connect(self.add_hardware_item)
        add_layout.addWidget(self.add_hardware_btn)

        add_layout.addStretch()
        layout.addWidget(add_panel)

        # Таблица добавленной фурнитуры
        self.hardware_table = QTableWidget()
        self.hardware_table.setColumnCount(5)
        self.hardware_table.setHorizontalHeaderLabels([
            "Наименование", "Количество", "Ед. изм.", "Примечания", "Удалить"
        ])

        header = self.hardware_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # Наименование
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)             # Количество
        header.setDefaultSectionSize(100)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)             # Ед. изм.
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)           # Примечания
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)             # Удалить

        # Разрешить редактирование всех колонок кроме первой (название) и единиц измерения
        self.hardware_table.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked | QAbstractItemView.EditTrigger.EditKeyPressed)

        layout.addWidget(self.hardware_table)

        return widget

    def create_sole_tab(self):
        """Вкладка подошв"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        info = QLabel(
            "💡 Варианты подошв для модели. "
            "Выберите из справочника материалов (группа ПОДОШВА) и укажите размерный ряд"
        )
        info.setWordWrap(True)
        info.setStyleSheet("background: #f0f8ff; padding: 10px; border-radius: 5px;")
        layout.addWidget(info)

        # Панель добавления подошвы
        add_panel = QGroupBox("Добавить подошву")
        add_layout = QHBoxLayout(add_panel)

        # Выпадающий список подошв
        self.sole_combo = QComboBox()
        self.sole_combo.setPlaceholderText("Выберите подошву из справочника...")
        self.sole_combo.setMinimumWidth(300)
        add_layout.addWidget(QLabel("Подошва:"))
        add_layout.addWidget(self.sole_combo)

        # Размерный ряд
        self.sole_size_input = QLineEdit()
        self.sole_size_input.setPlaceholderText("Например: 39-45")
        add_layout.addWidget(QLabel("Размерный ряд:"))
        add_layout.addWidget(self.sole_size_input)

        # Примечания
        self.sole_notes_input = QLineEdit()
        self.sole_notes_input.setPlaceholderText("Цвет, особенности")
        add_layout.addWidget(QLabel("Примечания:"))
        add_layout.addWidget(self.sole_notes_input)

        # Кнопка добавления
        self.add_sole_btn = QPushButton("➕ Добавить подошву")
        self.add_sole_btn.clicked.connect(self.add_sole)
        add_layout.addWidget(self.add_sole_btn)

        add_layout.addStretch()
        layout.addWidget(add_panel)

        # Таблица подошв
        self.sole_table = QTableWidget()
        self.sole_table.setColumnCount(4)
        self.sole_table.setHorizontalHeaderLabels([
            "Название подошвы", "Размерный ряд", "Примечания", "Удалить"
        ])

        header = self.sole_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        header.setDefaultSectionSize(150)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)

        self.sole_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        layout.addWidget(self.sole_table)

        return widget

    def create_variants_tab(self):
        """Вкладка вариантов исполнения"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Перфорация
        perf_group = QGroupBox("Варианты перфорации")
        perf_layout = QVBoxLayout(perf_group)
        self.perf_text = QTextEdit()
        self.perf_text.setPlaceholderText(
            "Укажите варианты перфорации, каждый с новой строки:\n"
            "Полная перфорация: союзка + берец\n"
            "На союзке\n"
            "На берце\n"
            "Без перфорации"
        )
        self.perf_text.setMaximumHeight(100)
        perf_layout.addWidget(self.perf_text)
        layout.addWidget(perf_group)

        # Подкладка/стелька
        lining_group = QGroupBox("Варианты подкладки/стельки")
        lining_layout = QVBoxLayout(lining_group)
        self.lining_text = QTextEdit()
        self.lining_text.setPlaceholderText(
            "Укажите варианты подкладки:\n"
            "Полный подклад: кожподклад\n"
            "Байка\n"
            "Мех\n"
            "Эва + черная стелька 7мм с профилем и надписью"
        )
        self.lining_text.setMaximumHeight(100)
        lining_layout.addWidget(self.lining_text)
        layout.addWidget(lining_group)

        # Другие варианты
        other_group = QGroupBox("Другие варианты исполнения")
        other_layout = QVBoxLayout(other_group)
        self.other_variants_text = QTextEdit()
        self.other_variants_text.setPlaceholderText(
            "Укажите другие варианты:\n"
            "Цвета кожи\n"
            "Типы обработки\n"
            "Специальные исполнения"
        )
        self.other_variants_text.setMaximumHeight(100)
        other_layout.addWidget(self.other_variants_text)
        layout.addWidget(other_group)

        layout.addStretch()

        return widget

    def load_reference_data(self):
        """Загрузка справочных данных из БД"""
        try:
            conn = self.db.get_connection()
            if not conn:
                return

            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

            # Загрузка деталей кроя
            cursor.execute("""
                SELECT id, code, name, category, default_qty, notes
                FROM cutting_parts
                WHERE is_active = true AND is_cutting = true
                ORDER BY category, name
            """)

            self.cutting_parts_list = cursor.fetchall()

            # Заполнение комбобокса деталей кроя
            self.cutting_part_combo.clear()
            self.cutting_part_combo.addItem("", None)

            current_category = None
            for part in self.cutting_parts_list:
                # Группировка по категориям
                if part['category'] != current_category:
                    current_category = part['category']
                    # Добавляем разделитель категории
                    self.cutting_part_combo.addItem(f"--- {current_category or 'ДРУГОЕ'} ---", None)
                    self.cutting_part_combo.model().item(self.cutting_part_combo.count()-1).setEnabled(False)

                display_text = f"{part['code']} - {part['name']}"
                self.cutting_part_combo.addItem(display_text, part)

            # Загрузка фурнитуры из материалов
            cursor.execute("""
                SELECT id, code, name, material_type, unit, price
                FROM materials
                WHERE is_active = true AND group_type = 'HARDWARE'
                ORDER BY name
            """)

            self.hardware_list = cursor.fetchall()

            # Заполнение комбобокса фурнитуры
            self.hardware_combo.clear()
            self.hardware_combo.addItem("", None)

            for hw in self.hardware_list:
                display_text = f"{hw['code']} - {hw['name']}"
                if hw['unit']:
                    display_text += f" ({hw['unit']})"
                self.hardware_combo.addItem(display_text, hw)

            # Загрузка подошв
            cursor.execute("""
                SELECT id, code, name, material_type, unit
                FROM materials
                WHERE is_active = true AND group_type = 'SOLE'
                ORDER BY name
            """)

            sole_list = cursor.fetchall()

            # Заполнение комбобокса подошв
            self.sole_combo.clear()
            self.sole_combo.addItem("", None)

            for sole in sole_list:
                display_text = f"{sole['code']} - {sole['name']}"
                self.sole_combo.addItem(display_text, sole)

            cursor.close()
            self.db.put_connection(conn)

        except Exception as e:
            QMessageBox.warning(self, "Предупреждение", f"Не удалось загрузить справочники: {e}")

    def add_cutting_part(self):
        """Добавить деталь кроя в таблицу"""
        part_data = self.cutting_part_combo.currentData()

        if not part_data:
            QMessageBox.warning(self, "Внимание", "Выберите деталь кроя из списка")
            return

        # Проверка на дубликаты
        for row in range(self.cutting_table.rowCount()):
            if self.cutting_table.item(row, 0).text() == f"{part_data['code']} - {part_data['name']}":
                QMessageBox.warning(self, "Внимание", "Эта деталь уже добавлена")
                return

        row = self.cutting_table.rowCount()
        self.cutting_table.insertRow(row)

        # Деталировка (не редактируемая)
        item_detail = QTableWidgetItem(f"{part_data['code']} - {part_data['name']}")
        item_detail.setFlags(item_detail.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.cutting_table.setItem(row, 0, item_detail)

        # Количество (редактируемое)
        item_qty = QTableWidgetItem(str(self.cutting_qty_spin.value()))
        self.cutting_table.setItem(row, 1, item_qty)

        # Расход (редактируемый)
        item_consumption = QTableWidgetItem(f"{self.cutting_consumption_spin.value():.2f}")
        self.cutting_table.setItem(row, 2, item_consumption)

        # Примечания (редактируемые) - пустое поле по умолчанию
        item_notes = QTableWidgetItem("")
        self.cutting_table.setItem(row, 3, item_notes)

        # Кнопка удаления
        delete_btn = QPushButton("🗑")
        delete_btn.clicked.connect(lambda: self.cutting_table.removeRow(self.cutting_table.currentRow()))
        self.cutting_table.setCellWidget(row, 4, delete_btn)

        # Очистка полей ввода
        self.cutting_part_combo.setCurrentIndex(0)
        self.cutting_qty_spin.setValue(2)
        self.cutting_consumption_spin.setValue(0)

    def add_hardware_item(self):
        """Добавить фурнитуру в таблицу"""
        hw_data = self.hardware_combo.currentData()

        if not hw_data:
            QMessageBox.warning(self, "Внимание", "Выберите фурнитуру из списка")
            return

        row = self.hardware_table.rowCount()
        self.hardware_table.insertRow(row)

        # Наименование (не редактируемое)
        item_name = QTableWidgetItem(f"{hw_data['code']} - {hw_data['name']}")
        item_name.setFlags(item_name.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.hardware_table.setItem(row, 0, item_name)

        # Количество (редактируемое)
        item_qty = QTableWidgetItem(f"{self.hardware_qty_spin.value():.2f}")
        self.hardware_table.setItem(row, 1, item_qty)

        # Единица измерения (не редактируемая)
        unit = hw_data.get('unit', 'шт')
        item_unit = QTableWidgetItem(unit)
        item_unit.setFlags(item_unit.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.hardware_table.setItem(row, 2, item_unit)

        # Примечания (редактируемые) - пустое поле по умолчанию
        item_notes = QTableWidgetItem("")
        self.hardware_table.setItem(row, 3, item_notes)

        # Кнопка удаления
        delete_btn = QPushButton("🗑")
        delete_btn.clicked.connect(lambda: self.hardware_table.removeRow(self.hardware_table.currentRow()))
        self.hardware_table.setCellWidget(row, 4, delete_btn)

        # Очистка полей
        self.hardware_combo.setCurrentIndex(0)
        self.hardware_qty_spin.setValue(1)

    def add_sole(self):
        """Добавить подошву в таблицу"""
        sole_data = self.sole_combo.currentData()

        if not sole_data:
            QMessageBox.warning(self, "Внимание", "Выберите подошву из списка")
            return

        row = self.sole_table.rowCount()
        self.sole_table.insertRow(row)

        # Название
        self.sole_table.setItem(row, 0, QTableWidgetItem(f"{sole_data['code']} - {sole_data['name']}"))

        # Размерный ряд
        size_range = self.sole_size_input.text()
        if not size_range:
            size_range = f"{self.size_min_spin.value()}-{self.size_max_spin.value()}"
        self.sole_table.setItem(row, 1, QTableWidgetItem(size_range))

        # Примечания
        self.sole_table.setItem(row, 2, QTableWidgetItem(self.sole_notes_input.text()))

        # Кнопка удаления
        delete_btn = QPushButton("🗑")
        delete_btn.clicked.connect(lambda: self.sole_table.removeRow(self.sole_table.currentRow()))
        self.sole_table.setCellWidget(row, 3, delete_btn)

        # Очистка полей
        self.sole_combo.setCurrentIndex(0)
        self.sole_size_input.clear()
        self.sole_notes_input.clear()

    def save_model(self):
        """Сохранение модели"""
        if not self.validate():
            return

        try:
            conn = self.db.get_connection()
            if not conn:
                QMessageBox.critical(self, "Ошибка", "Не удалось подключиться к БД")
                return

            cursor = conn.cursor()

            # Подготовка данных модели
            model_data = {
                'article': self.article_input.text(),
                'name': self.name_input.text(),
                'last_code': self.last_code_input.text(),
                'last_type': self.last_type_combo.currentText(),
                'size_min': self.size_min_spin.value(),
                'size_max': self.size_max_spin.value()
            }

            if self.model_id:
                # Обновление существующей модели
                cursor.execute("""
                    UPDATE models
                    SET article = %s, name = %s, last_code = %s, last_type = %s,
                        size_min = %s, size_max = %s, updated_at = NOW()
                    WHERE id = %s
                """, (model_data['article'], model_data['name'], model_data['last_code'],
                      model_data['last_type'], model_data['size_min'], model_data['size_max'],
                      self.model_id))
            else:
                # Создание новой модели
                cursor.execute("""
                    INSERT INTO models (article, name, last_code, last_type, size_min, size_max, uuid)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (model_data['article'], model_data['name'], model_data['last_code'],
                      model_data['last_type'], model_data['size_min'], model_data['size_max'],
                      str(uuid.uuid4())))

                self.model_id = cursor.fetchone()[0]

            # Удаляем старые компоненты
            cursor.execute("DELETE FROM model_components WHERE model_id = %s", (self.model_id,))

            sort_order = 0

            # Сохраняем детали кроя в model_components
            for row in range(self.cutting_table.rowCount()):
                component_name = self.cutting_table.item(row, 0).text()
                quantity = int(self.cutting_table.item(row, 1).text())
                consumption = float(self.cutting_table.item(row, 2).text())  # Теперь это отдельное поле
                notes = self.cutting_table.item(row, 3).text()  # Примечания в 4-й колонке

                cursor.execute("""
                    INSERT INTO model_components
                    (model_id, component_name, component_group, absolute_consumption, unit, notes, sort_order)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (self.model_id, component_name.split(' - ')[-1] if ' - ' in component_name else component_name,
                      'cutting', consumption, 'дм²', notes, sort_order))
                sort_order += 1

            # Сохраняем фурнитуру в model_components
            for row in range(self.hardware_table.rowCount()):
                component_name = self.hardware_table.item(row, 0).text()
                quantity = float(self.hardware_table.item(row, 1).text())
                unit = self.hardware_table.item(row, 2).text()
                notes = self.hardware_table.item(row, 3).text()

                cursor.execute("""
                    INSERT INTO model_components
                    (model_id, component_name, component_group, absolute_consumption, unit, notes, sort_order)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (self.model_id, component_name.split(' - ')[-1] if ' - ' in component_name else component_name,
                      'material', quantity, unit, notes, sort_order))
                sort_order += 1

            # Сохраняем подошвы в model_components
            for row in range(self.sole_table.rowCount()):
                sole_name = self.sole_table.item(row, 0).text()
                size_range = self.sole_table.item(row, 1).text()
                notes = self.sole_table.item(row, 2).text()

                cursor.execute("""
                    INSERT INTO model_components
                    (model_id, component_name, component_group, unit, notes, sort_order)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (self.model_id, sole_name.split(' - ')[-1] if ' - ' in sole_name else sole_name,
                      'sole', size_range, notes, sort_order))
                sort_order += 1

            conn.commit()
            cursor.close()
            self.db.put_connection(conn)

            QMessageBox.information(self, "Успешно", "Модель сохранена")
            self.saved.emit()
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить модель: {e}")

    def validate(self):
        """Валидация формы"""
        if not self.article_input.text():
            QMessageBox.warning(self, "Ошибка", "Укажите артикул модели")
            return False

        if not self.name_input.text():
            QMessageBox.warning(self, "Ошибка", "Укажите название модели")
            return False

        if not self.last_code_input.text():
            QMessageBox.warning(self, "Ошибка", "Укажите колодку")
            return False

        if self.cutting_table.rowCount() == 0:
            QMessageBox.warning(self, "Ошибка", "Добавьте хотя бы одну деталь кроя")
            self.tabs.setCurrentIndex(0)
            return False

        return True

    def load_model_data(self):
        """Загрузка данных модели для редактирования"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

            # Загрузка основных данных модели
            cursor.execute("SELECT * FROM models WHERE id = %s", (self.model_id,))
            model = cursor.fetchone()

            if model:
                self.article_input.setText(model['article'] or '')
                self.name_input.setText(model['name'] or '')
                self.last_code_input.setText(model['last_code'] or '')
                if model['last_type']:
                    self.last_type_combo.setCurrentText(model['last_type'])
                if model['size_min']:
                    self.size_min_spin.setValue(model['size_min'])
                if model['size_max']:
                    self.size_max_spin.setValue(model['size_max'])

            # Загружаем компоненты из model_components
            cursor.execute("""
                SELECT component_name, component_group, absolute_consumption, unit, notes
                FROM model_components
                WHERE model_id = %s
                ORDER BY sort_order, component_group, component_name
            """, (self.model_id,))

            components = cursor.fetchall()

            for comp in components:
                if comp['component_group'] == 'cutting':
                    # Добавляем деталь кроя
                    row = self.cutting_table.rowCount()
                    self.cutting_table.insertRow(row)

                    # Деталировка (не редактируемая)
                    item_detail = QTableWidgetItem(comp['component_name'])
                    item_detail.setFlags(item_detail.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.cutting_table.setItem(row, 0, item_detail)

                    # Количество (редактируемое)
                    self.cutting_table.setItem(row, 1, QTableWidgetItem("2"))  # По умолчанию пара

                    # Расход в отдельной колонке (редактируемый)
                    consumption = comp['absolute_consumption'] if comp['absolute_consumption'] else 0
                    self.cutting_table.setItem(row, 2, QTableWidgetItem(f"{consumption:.2f}"))

                    # Примечания - только текстовые заметки (редактируемые)
                    notes = comp['notes'] or ''
                    # Убираем расход из примечаний если он там есть
                    if 'Расход:' in notes:
                        notes = notes.split('Расход:')[0].strip()
                    self.cutting_table.setItem(row, 3, QTableWidgetItem(notes))

                    delete_btn = QPushButton("🗑")
                    delete_btn.clicked.connect(lambda: self.cutting_table.removeRow(self.cutting_table.currentRow()))
                    self.cutting_table.setCellWidget(row, 4, delete_btn)

                elif comp['component_group'] == 'material':
                    # Добавляем фурнитуру
                    row = self.hardware_table.rowCount()
                    self.hardware_table.insertRow(row)

                    # Наименование (не редактируемое)
                    item_name = QTableWidgetItem(comp['component_name'])
                    item_name.setFlags(item_name.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.hardware_table.setItem(row, 0, item_name)

                    # Количество (редактируемое)
                    quantity = comp['absolute_consumption'] if comp['absolute_consumption'] else 1
                    self.hardware_table.setItem(row, 1, QTableWidgetItem(f"{quantity:.2f}"))

                    # Единица измерения (не редактируемая)
                    unit = comp['unit'] or 'шт'
                    item_unit = QTableWidgetItem(unit)
                    item_unit.setFlags(item_unit.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.hardware_table.setItem(row, 2, item_unit)

                    # Примечания (редактируемые)
                    self.hardware_table.setItem(row, 3, QTableWidgetItem(comp['notes'] or ''))

                    delete_btn = QPushButton("🗑")
                    delete_btn.clicked.connect(lambda: self.hardware_table.removeRow(self.hardware_table.currentRow()))
                    self.hardware_table.setCellWidget(row, 4, delete_btn)

                elif comp['component_group'] == 'sole':
                    # Добавляем подошву
                    row = self.sole_table.rowCount()
                    self.sole_table.insertRow(row)
                    self.sole_table.setItem(row, 0, QTableWidgetItem(comp['component_name']))
                    self.sole_table.setItem(row, 1, QTableWidgetItem(comp['unit'] or ''))
                    self.sole_table.setItem(row, 2, QTableWidgetItem(comp['notes'] or ''))

                    delete_btn = QPushButton("🗑")
                    delete_btn.clicked.connect(lambda: self.sole_table.removeRow(self.sole_table.currentRow()))
                    self.sole_table.setCellWidget(row, 3, delete_btn)

            cursor.close()
            self.db.put_connection(conn)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить данные модели: {e}")