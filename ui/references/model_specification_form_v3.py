"""Форма создания модели обуви с выбираемыми параметрами производства"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QFormLayout, QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox,
    QTableWidget, QTableWidgetItem, QPushButton, QTextEdit,
    QLabel, QGroupBox, QCheckBox, QHeaderView, QMessageBox,
    QScrollArea, QGridLayout, QAbstractItemView, QListWidget,
    QListWidgetItem
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from database.connection import DatabaseConnection
import psycopg2.extras
import json
import uuid


class ModelSpecificationFormV3(QDialog):
    """Форма создания/редактирования модели обуви с выбираемыми параметрами"""

    saved = pyqtSignal()

    def __init__(self, parent=None, model_id=None):
        super().__init__(parent)
        self.model_id = model_id
        self.db = DatabaseConnection()

        self.setWindowTitle("Спецификация модели" if model_id else "Новая модель")
        self.setModal(True)
        self.resize(1400, 900)

        self.init_ui()
        self.load_references()

        if model_id:
            self.load_model_data()
            self.load_variants()

    def init_ui(self):
        """Инициализация интерфейса"""
        layout = QVBoxLayout(self)

        # Основная информация
        info_group = QGroupBox("Основная информация")
        info_layout = QFormLayout()

        self.article_input = QLineEdit()
        self.article_input.setPlaceholderText("Например: 001-24")
        info_layout.addRow("Артикул:", self.article_input)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Например: Кроссовки 'Хлынов'")
        info_layout.addRow("Название модели:", self.name_input)

        self.last_code_input = QLineEdit()
        self.last_code_input.setPlaceholderText("Код колодки")
        info_layout.addRow("Колодка:", self.last_code_input)

        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        # Вкладки
        self.tabs = QTabWidget()

        self.cutting_tab = self.create_cutting_tab()
        self.tabs.addTab(self.cutting_tab, "✂️ Детали кроя")

        self.hardware_tab = self.create_hardware_tab()
        self.tabs.addTab(self.hardware_tab, "🔩 Фурнитура")

        self.sole_tab = self.create_sole_tab()
        self.tabs.addTab(self.sole_tab, "👟 Подошва")

        self.variants_tab = self.create_variants_tab()
        self.tabs.addTab(self.variants_tab, "🎨 Варианты и параметры")

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
        self.cutting_consumption_spin.setValue(0)
        self.cutting_consumption_spin.setSuffix(" дм²")
        add_layout.addWidget(QLabel("Расход:"))
        add_layout.addWidget(self.cutting_consumption_spin)

        # Примечание
        self.cutting_notes_input = QLineEdit()
        self.cutting_notes_input.setPlaceholderText("Примечания...")
        add_layout.addWidget(QLabel("Примечание:"))
        add_layout.addWidget(self.cutting_notes_input)

        # Кнопка добавления
        add_cutting_btn = QPushButton("➕ Добавить")
        add_cutting_btn.clicked.connect(self.add_cutting_part)
        add_layout.addWidget(add_cutting_btn)

        layout.addWidget(add_panel)

        # Таблица деталей кроя
        self.cutting_table = QTableWidget()
        self.cutting_table.setColumnCount(5)
        self.cutting_table.setHorizontalHeaderLabels(
            ["Деталь", "Кол-во", "Расход (дм²)", "Примечание", "Удалить"]
        )
        self.cutting_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.cutting_table)

        return widget

    def create_hardware_tab(self):
        """Вкладка фурнитуры"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Информация
        info = QLabel(
            "💡 Фурнитура - вспомогательные элементы обуви. "
            "Выберите из справочника или добавьте вручную"
        )
        info.setWordWrap(True)
        info.setStyleSheet("background: #fff3cd; padding: 10px; border-radius: 5px;")
        layout.addWidget(info)

        # Панель добавления
        add_panel = QGroupBox("Добавить фурнитуру")
        add_layout = QHBoxLayout(add_panel)

        # Выпадающий список фурнитуры
        self.hardware_combo = QComboBox()
        self.hardware_combo.setPlaceholderText("Выберите фурнитуру из справочника...")
        self.hardware_combo.setMinimumWidth(250)
        self.hardware_combo.setEditable(True)
        add_layout.addWidget(QLabel("Фурнитура:"))
        add_layout.addWidget(self.hardware_combo)

        # Количество
        self.hardware_qty_spin = QDoubleSpinBox()
        self.hardware_qty_spin.setRange(0, 999)
        self.hardware_qty_spin.setValue(1)
        add_layout.addWidget(QLabel("Количество:"))
        add_layout.addWidget(self.hardware_qty_spin)

        # Единица измерения
        self.hardware_unit_combo = QComboBox()
        self.hardware_unit_combo.addItems(["шт", "пара", "м", "см", "дм²", "м²", "компл"])
        add_layout.addWidget(QLabel("Ед.изм.:"))
        add_layout.addWidget(self.hardware_unit_combo)

        # Примечание
        self.hardware_notes_input = QLineEdit()
        self.hardware_notes_input.setPlaceholderText("Примечания...")
        add_layout.addWidget(QLabel("Примечание:"))
        add_layout.addWidget(self.hardware_notes_input)

        # Кнопка добавления
        add_hardware_btn = QPushButton("➕ Добавить")
        add_hardware_btn.clicked.connect(self.add_hardware)
        add_layout.addWidget(add_hardware_btn)

        layout.addWidget(add_panel)

        # Таблица фурнитуры
        self.hardware_table = QTableWidget()
        self.hardware_table.setColumnCount(5)
        self.hardware_table.setHorizontalHeaderLabels(
            ["Название", "Кол-во", "Ед.изм.", "Примечание", "Удалить"]
        )
        self.hardware_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.hardware_table)

        return widget

    def create_sole_tab(self):
        """Вкладка подошвы"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Информация
        info = QLabel(
            "💡 Подошвы - элементы низа обуви. "
            "Выберите из справочника подошв и укажите размерный ряд"
        )
        info.setWordWrap(True)
        info.setStyleSheet("background: #d4edda; padding: 10px; border-radius: 5px;")
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
        self.sole_size_input.setPlaceholderText("Например: 35-45")
        add_layout.addWidget(QLabel("Размерный ряд:"))
        add_layout.addWidget(self.sole_size_input)

        # Примечание
        self.sole_notes_input = QLineEdit()
        self.sole_notes_input.setPlaceholderText("Примечания...")
        add_layout.addWidget(QLabel("Примечание:"))
        add_layout.addWidget(self.sole_notes_input)

        # Кнопка добавления
        add_sole_btn = QPushButton("➕ Добавить")
        add_sole_btn.clicked.connect(self.add_sole)
        add_layout.addWidget(add_sole_btn)

        layout.addWidget(add_panel)

        # Таблица подошв
        self.sole_table = QTableWidget()
        self.sole_table.setColumnCount(4)
        self.sole_table.setHorizontalHeaderLabels(
            ["Подошва", "Размерный ряд", "Примечание", "Удалить"]
        )
        self.sole_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.sole_table)

        return widget

    def create_variants_tab(self):
        """Вкладка вариантов исполнения и параметров производства"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Параметры модели
        params_group = QGroupBox("Параметры производства модели")
        params_layout = QGridLayout(params_group)

        # Тип затяжки
        params_layout.addWidget(QLabel("Тип затяжки:"), 0, 0)
        self.lasting_type_combo = QComboBox()
        self.lasting_type_combo.setPlaceholderText("Выберите тип затяжки...")
        params_layout.addWidget(self.lasting_type_combo, 0, 1)

        # Кнопка добавления типа затяжки
        add_lasting_btn = QPushButton("➕")
        add_lasting_btn.setMaximumWidth(30)
        add_lasting_btn.setToolTip("Добавить новый тип затяжки")
        add_lasting_btn.clicked.connect(lambda: self.add_reference_item('lasting'))
        params_layout.addWidget(add_lasting_btn, 0, 2)

        # Доступные перфорации
        params_layout.addWidget(QLabel("Доступные перфорации:"), 1, 0, Qt.AlignmentFlag.AlignTop)
        self.perforations_list = QListWidget()
        self.perforations_list.setMaximumHeight(100)
        self.perforations_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        params_layout.addWidget(self.perforations_list, 1, 1)

        perf_buttons = QVBoxLayout()
        add_perf_btn = QPushButton("➕")
        add_perf_btn.setMaximumWidth(30)
        add_perf_btn.setToolTip("Добавить тип перфорации")
        add_perf_btn.clicked.connect(lambda: self.add_reference_item('perforation'))
        perf_buttons.addWidget(add_perf_btn)
        perf_buttons.addStretch()
        params_layout.addLayout(perf_buttons, 1, 2)

        # Доступные подкладки/стельки
        params_layout.addWidget(QLabel("Доступные подкладки:"), 2, 0, Qt.AlignmentFlag.AlignTop)
        self.linings_list = QListWidget()
        self.linings_list.setMaximumHeight(100)
        self.linings_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        params_layout.addWidget(self.linings_list, 2, 1)

        lining_buttons = QVBoxLayout()
        add_lining_btn = QPushButton("➕")
        add_lining_btn.setMaximumWidth(30)
        add_lining_btn.setToolTip("Добавить тип подкладки")
        add_lining_btn.clicked.connect(lambda: self.add_reference_item('lining'))
        lining_buttons.addWidget(add_lining_btn)
        lining_buttons.addStretch()
        params_layout.addLayout(lining_buttons, 2, 2)

        layout.addWidget(params_group)

        # Информационный блок
        info_layout = QHBoxLayout()

        info_text = QLabel(
            "💡 Управление вариантами модели:\n"
            "• Базовая модель - определяет доступные варианты перфорации и подкладки\n"
            "• Специфические варианты - выбирают конкретную перфорацию и подкладку из доступных"
        )
        info_text.setWordWrap(True)
        info_text.setStyleSheet("background: #e8f4fd; padding: 10px; border-radius: 5px; border: 1px solid #b8dff8;")
        info_layout.addWidget(info_text)

        # Кнопка создания нового специфического варианта
        self.create_variant_btn = QPushButton("➕ Создать специфический вариант")
        self.create_variant_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.create_variant_btn.clicked.connect(self.create_specific_variant)
        info_layout.addWidget(self.create_variant_btn)

        layout.addLayout(info_layout)

        # Таблица существующих вариантов
        variants_group = QGroupBox("Специфические варианты данной модели")
        variants_layout = QVBoxLayout(variants_group)

        self.variants_table = QTableWidget()
        self.variants_table.setColumnCount(7)
        self.variants_table.setHorizontalHeaderLabels([
            "Код", "Название", "Материалов", "Стоимость мат.", "Активен", "Создан", "Действия"
        ])

        header = self.variants_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)

        header.resizeSection(0, 100)
        header.resizeSection(2, 100)
        header.resizeSection(3, 120)
        header.resizeSection(4, 80)
        header.resizeSection(5, 100)
        header.resizeSection(6, 100)

        self.variants_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.variants_table.setAlternatingRowColors(True)
        self.variants_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        variants_layout.addWidget(self.variants_table)
        layout.addWidget(variants_group)

        # Загружаем справочники
        self.load_model_parameters()

        return widget

    def load_model_parameters(self):
        """Загрузка параметров модели из справочников"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

            # Загружаем типы затяжки
            cursor.execute("SELECT id, code, name FROM lasting_types WHERE is_active = true ORDER BY name")
            lasting_types = cursor.fetchall()
            self.lasting_type_combo.clear()
            for lasting in lasting_types:
                self.lasting_type_combo.addItem(f"{lasting['name']} ({lasting['code']})", lasting['id'])

            # Загружаем типы перфорации
            cursor.execute("SELECT id, code, name FROM perforation_types WHERE is_active = true ORDER BY name")
            perforations = cursor.fetchall()
            self.perforations_list.clear()
            for perf in perforations:
                item = QListWidgetItem(f"{perf['name']} ({perf['code']})")
                item.setData(Qt.ItemDataRole.UserRole, perf['id'])
                self.perforations_list.addItem(item)

            # Загружаем типы подкладки
            cursor.execute("SELECT id, code, name FROM lining_types WHERE is_active = true ORDER BY name")
            linings = cursor.fetchall()
            self.linings_list.clear()
            for lining in linings:
                item = QListWidgetItem(f"{lining['name']} ({lining['code']})")
                item.setData(Qt.ItemDataRole.UserRole, lining['id'])
                self.linings_list.addItem(item)

            # Если редактируем модель, загружаем выбранные параметры
            if self.model_id:
                self.load_selected_parameters(cursor)

            cursor.close()
            self.db.put_connection(conn)

        except Exception as e:
            print(f"Ошибка загрузки параметров модели: {e}")

    def load_selected_parameters(self, cursor):
        """Загрузка выбранных параметров для существующей модели"""
        # Загружаем тип затяжки
        cursor.execute("SELECT lasting_type_id FROM models WHERE id = %s", (self.model_id,))
        result = cursor.fetchone()
        if result and result['lasting_type_id']:
            index = self.lasting_type_combo.findData(result['lasting_type_id'])
            if index >= 0:
                self.lasting_type_combo.setCurrentIndex(index)

        # Загружаем выбранные перфорации
        cursor.execute("""
            SELECT perforation_id FROM model_perforations
            WHERE model_id = %s
        """, (self.model_id,))
        selected_perfs = [row['perforation_id'] for row in cursor.fetchall()]

        for i in range(self.perforations_list.count()):
            item = self.perforations_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) in selected_perfs:
                item.setSelected(True)

        # Загружаем выбранные подкладки
        cursor.execute("""
            SELECT lining_id FROM model_linings
            WHERE model_id = %s
        """, (self.model_id,))
        selected_linings = [row['lining_id'] for row in cursor.fetchall()]

        for i in range(self.linings_list.count()):
            item = self.linings_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) in selected_linings:
                item.setSelected(True)

    def add_reference_item(self, ref_type):
        """Добавление нового элемента в справочник"""
        # TODO: Реализовать диалог добавления нового элемента
        QMessageBox.information(self, "В разработке",
                               f"Добавление нового элемента в справочник {ref_type}")

    def load_references(self):
        """Загрузка справочников"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

            # Загрузка деталей кроя
            cursor.execute("SELECT id, code, name FROM reference_cutting_parts WHERE is_active = true ORDER BY name")
            for row in cursor.fetchall():
                self.cutting_part_combo.addItem(f"{row['name']} - {row['code']}", row['id'])

            # Загрузка фурнитуры
            cursor.execute("SELECT id, code, name FROM reference_hardware WHERE is_active = true ORDER BY name")
            for row in cursor.fetchall():
                self.hardware_combo.addItem(f"{row['name']} - {row['code']}", row['id'])

            # Загрузка подошв
            cursor.execute("SELECT id, code, name FROM reference_soles WHERE is_active = true ORDER BY name")
            for row in cursor.fetchall():
                self.sole_combo.addItem(f"{row['name']} - {row['code']}", row['id'])

            cursor.close()
            self.db.put_connection(conn)

        except Exception as e:
            print(f"Ошибка загрузки справочников: {e}")

    def add_cutting_part(self):
        """Добавление детали кроя"""
        if self.cutting_part_combo.currentIndex() < 0:
            QMessageBox.warning(self, "Внимание", "Выберите деталь кроя")
            return

        row = self.cutting_table.rowCount()
        self.cutting_table.insertRow(row)

        self.cutting_table.setItem(row, 0, QTableWidgetItem(self.cutting_part_combo.currentText()))
        self.cutting_table.setItem(row, 1, QTableWidgetItem(str(self.cutting_qty_spin.value())))
        self.cutting_table.setItem(row, 2, QTableWidgetItem(str(self.cutting_consumption_spin.value())))
        self.cutting_table.setItem(row, 3, QTableWidgetItem(self.cutting_notes_input.text()))

        delete_btn = QPushButton("🗑️")
        delete_btn.clicked.connect(lambda: self.delete_row(self.cutting_table, row))
        self.cutting_table.setCellWidget(row, 4, delete_btn)

        # Очистка полей ввода
        self.cutting_consumption_spin.setValue(0)
        self.cutting_notes_input.clear()

    def add_hardware(self):
        """Добавление фурнитуры"""
        if not self.hardware_combo.currentText():
            QMessageBox.warning(self, "Внимание", "Укажите название фурнитуры")
            return

        row = self.hardware_table.rowCount()
        self.hardware_table.insertRow(row)

        self.hardware_table.setItem(row, 0, QTableWidgetItem(self.hardware_combo.currentText()))
        self.hardware_table.setItem(row, 1, QTableWidgetItem(str(self.hardware_qty_spin.value())))
        self.hardware_table.setItem(row, 2, QTableWidgetItem(self.hardware_unit_combo.currentText()))
        self.hardware_table.setItem(row, 3, QTableWidgetItem(self.hardware_notes_input.text()))

        delete_btn = QPushButton("🗑️")
        delete_btn.clicked.connect(lambda: self.delete_row(self.hardware_table, row))
        self.hardware_table.setCellWidget(row, 4, delete_btn)

        # Очистка полей
        self.hardware_notes_input.clear()

    def add_sole(self):
        """Добавление подошвы"""
        if self.sole_combo.currentIndex() < 0:
            QMessageBox.warning(self, "Внимание", "Выберите подошву")
            return

        row = self.sole_table.rowCount()
        self.sole_table.insertRow(row)

        self.sole_table.setItem(row, 0, QTableWidgetItem(self.sole_combo.currentText()))
        self.sole_table.setItem(row, 1, QTableWidgetItem(self.sole_size_input.text()))
        self.sole_table.setItem(row, 2, QTableWidgetItem(self.sole_notes_input.text()))

        delete_btn = QPushButton("🗑️")
        delete_btn.clicked.connect(lambda: self.delete_row(self.sole_table, row))
        self.sole_table.setCellWidget(row, 3, delete_btn)

        # Очистка полей
        self.sole_size_input.clear()
        self.sole_notes_input.clear()

    def delete_row(self, table, row):
        """Удаление строки из таблицы"""
        table.removeRow(row)
        # Обновляем обработчики для кнопок удаления
        for i in range(table.rowCount()):
            btn = table.cellWidget(i, table.columnCount() - 1)
            if btn:
                btn.clicked.disconnect()
                btn.clicked.connect(lambda checked, r=i: self.delete_row(table, r))

    def save_model(self):
        """Сохранение модели"""
        if not self.validate():
            return

        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            if self.model_id:
                # Обновление существующей модели
                cursor.execute("""
                    UPDATE models
                    SET article = %s, name = %s, last_code = %s,
                        lasting_type_id = %s, updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                """, (
                    self.article_input.text(),
                    self.name_input.text(),
                    self.last_code_input.text(),
                    self.lasting_type_combo.currentData(),
                    self.model_id
                ))
            else:
                # Создание новой модели
                cursor.execute("""
                    INSERT INTO models (article, name, last_code, model_type, lasting_type_id)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    self.article_input.text(),
                    self.name_input.text(),
                    self.last_code_input.text(),
                    'Спортивная',
                    self.lasting_type_combo.currentData()
                ))
                self.model_id = cursor.fetchone()[0]

            # Сохраняем параметры модели
            self.save_model_parameters(cursor)

            # Сохраняем компоненты модели
            self.save_model_components(cursor)

            conn.commit()
            cursor.close()
            self.db.put_connection(conn)

            QMessageBox.information(self, "Успешно", "Модель сохранена")
            self.saved.emit()
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить модель: {e}")

    def save_model_parameters(self, cursor):
        """Сохранение параметров модели"""
        # Удаляем старые связи
        cursor.execute("DELETE FROM model_perforations WHERE model_id = %s", (self.model_id,))
        cursor.execute("DELETE FROM model_linings WHERE model_id = %s", (self.model_id,))

        # Сохраняем выбранные перфорации
        for i in range(self.perforations_list.count()):
            item = self.perforations_list.item(i)
            if item.isSelected():
                cursor.execute("""
                    INSERT INTO model_perforations (model_id, perforation_id)
                    VALUES (%s, %s)
                """, (self.model_id, item.data(Qt.ItemDataRole.UserRole)))

        # Сохраняем выбранные подкладки
        for i in range(self.linings_list.count()):
            item = self.linings_list.item(i)
            if item.isSelected():
                cursor.execute("""
                    INSERT INTO model_linings (model_id, lining_id)
                    VALUES (%s, %s)
                """, (self.model_id, item.data(Qt.ItemDataRole.UserRole)))

    def save_model_components(self, cursor):
        """Сохранение компонентов модели"""
        # Удаляем старые компоненты
        cursor.execute("DELETE FROM model_components WHERE model_id = %s", (self.model_id,))

        sort_order = 1

        # Сохраняем детали кроя
        for row in range(self.cutting_table.rowCount()):
            component_name = self.cutting_table.item(row, 0).text()
            quantity = float(self.cutting_table.item(row, 1).text())
            consumption = float(self.cutting_table.item(row, 2).text())
            notes = self.cutting_table.item(row, 3).text()

            cursor.execute("""
                INSERT INTO model_components
                (model_id, component_name, component_group, quantity, consumption, notes, sort_order)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (self.model_id, component_name.split(' - ')[-1] if ' - ' in component_name else component_name,
                  'cutting', quantity, consumption, notes, sort_order))
            sort_order += 1

        # Сохраняем фурнитуру
        for row in range(self.hardware_table.rowCount()):
            component_name = self.hardware_table.item(row, 0).text()
            quantity = float(self.hardware_table.item(row, 1).text())
            unit = self.hardware_table.item(row, 2).text()
            notes = self.hardware_table.item(row, 3).text()

            cursor.execute("""
                INSERT INTO model_components
                (model_id, component_name, component_group, quantity, unit, notes, sort_order)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (self.model_id, component_name.split(' - ')[-1] if ' - ' in component_name else component_name,
                  'hardware', quantity, unit, notes, sort_order))
            sort_order += 1

        # Сохраняем подошвы
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

        if not self.lasting_type_combo.currentData():
            QMessageBox.warning(self, "Ошибка", "Выберите тип затяжки")
            self.tabs.setCurrentIndex(3)
            return False

        return True

    def create_specific_variant(self):
        """Создание специфического варианта модели"""
        if not self.model_id:
            QMessageBox.warning(self, "Внимание", "Сначала сохраните базовую модель")
            return

        from ui.references.model_specific_variant_form import ModelSpecificVariantForm
        dialog = ModelSpecificVariantForm(parent=self, db=self.db, model_id=self.model_id)
        dialog.saved.connect(self.load_variants)
        dialog.exec()

    def load_variants(self):
        """Загрузка списка вариантов модели"""
        if not self.model_id:
            return

        try:
            conn = self.db.get_connection()
            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

            cursor.execute("""
                SELECT uuid, id, variant_code, variant_name, total_material_cost,
                       is_active, created_at,
                       jsonb_array_length(materials) as material_count
                FROM specifications
                WHERE model_id = %s
                ORDER BY created_at DESC
            """, (self.model_id,))

            variants = cursor.fetchall()

            # Очищаем таблицу
            self.variants_table.setRowCount(0)

            for variant in variants:
                row = self.variants_table.rowCount()
                self.variants_table.insertRow(row)

                self.variants_table.setItem(row, 0, QTableWidgetItem(variant['variant_code'] or ''))
                self.variants_table.setItem(row, 1, QTableWidgetItem(variant['variant_name'] or ''))
                self.variants_table.setItem(row, 2, QTableWidgetItem(str(variant['material_count'] or 0)))

                cost = variant['total_material_cost'] or 0
                self.variants_table.setItem(row, 3, QTableWidgetItem(f"{cost:.2f} руб"))

                active = "Да" if variant['is_active'] else "Нет"
                self.variants_table.setItem(row, 4, QTableWidgetItem(active))

                created = variant['created_at'].strftime('%d.%m.%Y') if variant['created_at'] else ''
                self.variants_table.setItem(row, 5, QTableWidgetItem(created))

                # Кнопка действий
                view_btn = QPushButton("👁 Просмотр")
                view_btn.clicked.connect(lambda checked, v_uuid=variant['uuid']: self.view_variant(v_uuid))
                self.variants_table.setCellWidget(row, 6, view_btn)

            cursor.close()
            self.db.put_connection(conn)

        except Exception as e:
            print(f"Ошибка загрузки вариантов: {e}")

    def view_variant(self, variant_id):
        """Просмотр деталей варианта"""
        print("🚨 ВНИМАНИЕ: Вызывается СТАРАЯ model_specification_form_v3.py!")
        print("🚨 Должна использоваться ModelSpecificationFormV5!")
        from ui.references.model_specific_variant_form import ModelSpecificVariantForm
        dialog = ModelSpecificVariantForm(
            parent=self,
            db=self.db,
            model_id=self.model_id,
            variant_id=variant_id,
            read_only=True
        )
        dialog.exec()

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

            # Загрузка компонентов модели
            cursor.execute("""
                SELECT * FROM model_components
                WHERE model_id = %s
                ORDER BY sort_order
            """, (self.model_id,))

            for component in cursor.fetchall():
                if component['component_group'] == 'cutting':
                    row = self.cutting_table.rowCount()
                    self.cutting_table.insertRow(row)
                    self.cutting_table.setItem(row, 0, QTableWidgetItem(component['component_name'] or ''))
                    self.cutting_table.setItem(row, 1, QTableWidgetItem(str(component['quantity'] or 0)))
                    self.cutting_table.setItem(row, 2, QTableWidgetItem(str(component['consumption'] or 0)))
                    self.cutting_table.setItem(row, 3, QTableWidgetItem(component['notes'] or ''))

                    delete_btn = QPushButton("🗑️")
                    delete_btn.clicked.connect(lambda checked, r=row: self.delete_row(self.cutting_table, r))
                    self.cutting_table.setCellWidget(row, 4, delete_btn)

                elif component['component_group'] == 'hardware':
                    row = self.hardware_table.rowCount()
                    self.hardware_table.insertRow(row)
                    self.hardware_table.setItem(row, 0, QTableWidgetItem(component['component_name'] or ''))
                    self.hardware_table.setItem(row, 1, QTableWidgetItem(str(component['quantity'] or 0)))
                    self.hardware_table.setItem(row, 2, QTableWidgetItem(component['unit'] or 'шт'))
                    self.hardware_table.setItem(row, 3, QTableWidgetItem(component['notes'] or ''))

                    delete_btn = QPushButton("🗑️")
                    delete_btn.clicked.connect(lambda checked, r=row: self.delete_row(self.hardware_table, r))
                    self.hardware_table.setCellWidget(row, 4, delete_btn)

                elif component['component_group'] == 'sole':
                    row = self.sole_table.rowCount()
                    self.sole_table.insertRow(row)
                    self.sole_table.setItem(row, 0, QTableWidgetItem(component['component_name'] or ''))
                    self.sole_table.setItem(row, 1, QTableWidgetItem(component['unit'] or ''))
                    self.sole_table.setItem(row, 2, QTableWidgetItem(component['notes'] or ''))

                    delete_btn = QPushButton("🗑️")
                    delete_btn.clicked.connect(lambda checked, r=row: self.delete_row(self.sole_table, r))
                    self.sole_table.setCellWidget(row, 3, delete_btn)

            cursor.close()
            self.db.put_connection(conn)

        except Exception as e:
            print(f"Ошибка загрузки данных модели: {e}")