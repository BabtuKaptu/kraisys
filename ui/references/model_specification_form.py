"""Правильная форма создания модели обуви с заводской структурой учета"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QFormLayout, QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox,
    QTableWidget, QTableWidgetItem, QPushButton, QTextEdit,
    QLabel, QGroupBox, QCheckBox, QHeaderView, QMessageBox,
    QScrollArea, QGridLayout, QSplitter
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from database.connection import DatabaseConnection
import psycopg2.extras
import json
import uuid


class ModelSpecificationForm(QDialog):
    """Форма создания/редактирования модели обуви с правильной структурой"""

    saved = pyqtSignal()

    def __init__(self, model_id=None, parent=None):
        super().__init__(parent)
        self.model_id = model_id
        self.db = DatabaseConnection()

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
            "Для каждой детали укажите примечания (материал, особенности обработки)"
        )
        info.setWordWrap(True)
        info.setStyleSheet("background: #f0f8ff; padding: 10px; border-radius: 5px;")
        layout.addWidget(info)

        # Таблица деталей кроя
        self.cutting_table = QTableWidget()
        self.cutting_table.setColumnCount(4)
        self.cutting_table.setHorizontalHeaderLabels([
            "Деталировка", "Количество", "Примечания", "Удалить"
        ])

        # Настройка ширины колонок
        header = self.cutting_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        header.setDefaultSectionSize(100)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)

        layout.addWidget(self.cutting_table)

        # Кнопки управления
        btn_layout = QHBoxLayout()

        # Кнопки быстрого добавления стандартных деталей
        self.add_union_btn = QPushButton("+ Обсоюзка")
        self.add_union_btn.clicked.connect(lambda: self.add_cutting_part("Обсоюзка"))

        self.add_vamp_btn = QPushButton("+ Союзка")
        self.add_vamp_btn.clicked.connect(lambda: self.add_cutting_part("Союзка"))

        self.add_quarter_btn = QPushButton("+ Берец")
        self.add_quarter_btn.clicked.connect(lambda: self.add_cutting_part("Берец внутренний"))

        self.add_counter_btn = QPushButton("+ Задник")
        self.add_counter_btn.clicked.connect(lambda: self.add_cutting_part("Задинка"))

        self.add_custom_btn = QPushButton("+ Другая деталь")
        self.add_custom_btn.clicked.connect(lambda: self.add_cutting_part(""))

        btn_layout.addWidget(self.add_union_btn)
        btn_layout.addWidget(self.add_vamp_btn)
        btn_layout.addWidget(self.add_quarter_btn)
        btn_layout.addWidget(self.add_counter_btn)
        btn_layout.addWidget(self.add_custom_btn)
        btn_layout.addStretch()

        layout.addLayout(btn_layout)

        return widget

    def create_hardware_tab(self):
        """Вкладка фурнитуры"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        info = QLabel(
            "💡 Фурнитура и комплектующие. "
            "Укажите точные параметры: размеры, количество, материал"
        )
        info.setWordWrap(True)
        info.setStyleSheet("background: #f0f8ff; padding: 10px; border-radius: 5px;")
        layout.addWidget(info)

        # Таблица фурнитуры
        self.hardware_table = QTableWidget()
        self.hardware_table.setColumnCount(4)
        self.hardware_table.setHorizontalHeaderLabels([
            "Наименование", "Количество/Размер", "Примечания", "Удалить"
        ])

        header = self.hardware_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        header.setDefaultSectionSize(150)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)

        layout.addWidget(self.hardware_table)

        # Кнопки быстрого добавления
        btn_layout = QHBoxLayout()

        self.add_laces_btn = QPushButton("+ Шнурки")
        self.add_laces_btn.clicked.connect(lambda: self.add_hardware_item("Шнурки плоские вощеные", "150 см"))

        self.add_hooks_btn = QPushButton("+ Крючки")
        self.add_hooks_btn.clicked.connect(lambda: self.add_hardware_item("Крючки", "8 крючков"))

        self.add_eyelets_btn = QPushButton("+ Петли")
        self.add_eyelets_btn.clicked.connect(lambda: self.add_hardware_item("Петли", "20 шт на пару"))

        self.add_zipper_btn = QPushButton("+ Молния")
        self.add_zipper_btn.clicked.connect(lambda: self.add_hardware_item("Молния", ""))

        self.add_custom_hw_btn = QPushButton("+ Другое")
        self.add_custom_hw_btn.clicked.connect(lambda: self.add_hardware_item("", ""))

        btn_layout.addWidget(self.add_laces_btn)
        btn_layout.addWidget(self.add_hooks_btn)
        btn_layout.addWidget(self.add_eyelets_btn)
        btn_layout.addWidget(self.add_zipper_btn)
        btn_layout.addWidget(self.add_custom_hw_btn)
        btn_layout.addStretch()

        layout.addLayout(btn_layout)

        return widget

    def create_sole_tab(self):
        """Вкладка подошв"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        info = QLabel(
            "💡 Варианты подошв для модели. "
            "Укажите доступные подошвы и их размерные ряды"
        )
        info.setWordWrap(True)
        info.setStyleSheet("background: #f0f8ff; padding: 10px; border-radius: 5px;")
        layout.addWidget(info)

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

        layout.addWidget(self.sole_table)

        # Кнопка добавления
        add_sole_btn = QPushButton("+ Добавить подошву")
        add_sole_btn.clicked.connect(self.add_sole)
        layout.addWidget(add_sole_btn)

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

    def add_cutting_part(self, default_name=""):
        """Добавить деталь кроя"""
        row = self.cutting_table.rowCount()
        self.cutting_table.insertRow(row)

        # Название детали
        if default_name:
            name_combo = QComboBox()
            # Стандартные детали кроя
            parts = [
                "Обсоюзка", "Союзка", "Берец внутренний", "Берец наружный",
                "Настрочной берец внутренний", "Настрочной берец наружный",
                "Задинка", "Мягкий кант", "Вставка 1", "Вставка 2",
                "Глухой клапан", "Язык клапана", "Деталь клапана",
                "Аппликация", "Шлевка кожаная", "Шлевка текстильная"
            ]
            name_combo.addItems(parts)
            name_combo.setCurrentText(default_name)
            name_combo.setEditable(True)
        else:
            name_combo = QLineEdit()
            name_combo.setPlaceholderText("Название детали")

        self.cutting_table.setCellWidget(row, 0, name_combo)

        # Количество
        qty_spin = QSpinBox()
        qty_spin.setRange(1, 20)
        qty_spin.setValue(2)  # По умолчанию пара
        self.cutting_table.setCellWidget(row, 1, qty_spin)

        # Примечания
        notes_edit = QLineEdit()
        if default_name == "Обсоюзка":
            notes_edit.setPlaceholderText("Например: По умолчанию штаферка внутри из красного трикотажа")
        elif "Берец" in default_name:
            notes_edit.setPlaceholderText("Например: На обувь из кожи хорс ИЗУМРУД")
        else:
            notes_edit.setPlaceholderText("Укажите материал, обработку, особенности")

        self.cutting_table.setCellWidget(row, 2, notes_edit)

        # Кнопка удаления
        delete_btn = QPushButton("🗑")
        delete_btn.clicked.connect(lambda: self.cutting_table.removeRow(row))
        self.cutting_table.setCellWidget(row, 3, delete_btn)

    def add_hardware_item(self, default_name="", default_spec=""):
        """Добавить фурнитуру"""
        row = self.hardware_table.rowCount()
        self.hardware_table.insertRow(row)

        # Название
        if default_name:
            name_combo = QComboBox()
            items = [
                "Шнурки плоские вощеные", "Шнурки плоские невощеные",
                "Шнурки круглые", "Крючки", "Петли", "Блочки",
                "Молния", "Липучка", "Пряжка", "Кнопки",
                "Заклепки", "Люверсы"
            ]
            name_combo.addItems(items)
            name_combo.setCurrentText(default_name)
            name_combo.setEditable(True)
        else:
            name_combo = QLineEdit()
            name_combo.setPlaceholderText("Наименование")

        self.hardware_table.setCellWidget(row, 0, name_combo)

        # Количество/размер
        spec_edit = QLineEdit()
        spec_edit.setText(default_spec)
        if "Шнурки" in default_name:
            spec_edit.setPlaceholderText("Например: 150 см")
        elif "Крючки" in default_name:
            spec_edit.setPlaceholderText("Например: 8 крючков")
        elif "Петли" in default_name:
            spec_edit.setPlaceholderText("Например: 20 шт на пару")
        else:
            spec_edit.setPlaceholderText("Количество, размер")

        self.hardware_table.setCellWidget(row, 1, spec_edit)

        # Примечания
        notes_edit = QLineEdit()
        notes_edit.setPlaceholderText("Дополнительные примечания")
        self.hardware_table.setCellWidget(row, 2, notes_edit)

        # Кнопка удаления
        delete_btn = QPushButton("🗑")
        delete_btn.clicked.connect(lambda: self.hardware_table.removeRow(row))
        self.hardware_table.setCellWidget(row, 3, delete_btn)

    def add_sole(self):
        """Добавить подошву"""
        row = self.sole_table.rowCount()
        self.sole_table.insertRow(row)

        # Название подошвы
        name_combo = QComboBox()
        name_combo.addItems([
            "888", "ВОВ", "ВОВ 2", "Мишлен", "ТЭП",
            "Полиуретан", "Резина", "Кожа", "ТПУ"
        ])
        name_combo.setEditable(True)
        self.sole_table.setCellWidget(row, 0, name_combo)

        # Размерный ряд
        size_edit = QLineEdit()
        size_edit.setPlaceholderText("Например: 39-45 или 36-49")
        self.sole_table.setCellWidget(row, 1, size_edit)

        # Примечания
        notes_edit = QLineEdit()
        notes_edit.setPlaceholderText("Цвет, особенности")
        self.sole_table.setCellWidget(row, 2, notes_edit)

        # Кнопка удаления
        delete_btn = QPushButton("🗑")
        delete_btn.clicked.connect(lambda: self.sole_table.removeRow(row))
        self.sole_table.setCellWidget(row, 3, delete_btn)

    def load_reference_data(self):
        """Загрузка справочных данных"""
        # Здесь можно загрузить данные из БД
        pass

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

            # Подготовка данных
            model_data = {
                'article': self.article_input.text(),
                'name': self.name_input.text(),
                'last_code': self.last_code_input.text(),
                'last_type': self.last_type_combo.currentText(),
                'size_min': self.size_min_spin.value(),
                'size_max': self.size_max_spin.value()
            }

            # Сбор деталей кроя
            cutting_parts = []
            for row in range(self.cutting_table.rowCount()):
                name_widget = self.cutting_table.cellWidget(row, 0)
                qty_widget = self.cutting_table.cellWidget(row, 1)
                notes_widget = self.cutting_table.cellWidget(row, 2)

                if name_widget:
                    part = {
                        'name': name_widget.text() if isinstance(name_widget, QLineEdit) else name_widget.currentText(),
                        'quantity': qty_widget.value() if qty_widget else 2,
                        'notes': notes_widget.text() if notes_widget else ''
                    }
                    cutting_parts.append(part)

            # Сбор фурнитуры
            hardware = []
            for row in range(self.hardware_table.rowCount()):
                name_widget = self.hardware_table.cellWidget(row, 0)
                spec_widget = self.hardware_table.cellWidget(row, 1)
                notes_widget = self.hardware_table.cellWidget(row, 2)

                if name_widget:
                    hw = {
                        'name': name_widget.text() if isinstance(name_widget, QLineEdit) else name_widget.currentText(),
                        'specification': spec_widget.text() if spec_widget else '',
                        'notes': notes_widget.text() if notes_widget else ''
                    }
                    hardware.append(hw)

            # Сбор подошв
            soles = []
            for row in range(self.sole_table.rowCount()):
                name_widget = self.sole_table.cellWidget(row, 0)
                size_widget = self.sole_table.cellWidget(row, 1)
                notes_widget = self.sole_table.cellWidget(row, 2)

                if name_widget:
                    sole = {
                        'name': name_widget.text() if isinstance(name_widget, QLineEdit) else name_widget.currentText(),
                        'size_range': size_widget.text() if size_widget else '',
                        'notes': notes_widget.text() if notes_widget else ''
                    }
                    soles.append(sole)

            # Варианты
            variants = {
                'perforation': self.perf_text.toPlainText().split('\n') if self.perf_text.toPlainText() else [],
                'lining': self.lining_text.toPlainText().split('\n') if self.lining_text.toPlainText() else [],
                'other': self.other_variants_text.toPlainText().split('\n') if self.other_variants_text.toPlainText() else []
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

            # Сохранение спецификации
            spec_data = {
                'cutting_parts': json.dumps(cutting_parts, ensure_ascii=False),
                'hardware': json.dumps(hardware, ensure_ascii=False),
                'variants': json.dumps(variants, ensure_ascii=False)
            }

            # Проверяем, есть ли спецификация
            cursor.execute("""
                SELECT id FROM specifications
                WHERE model_id = %s AND is_default = true
            """, (self.model_id,))

            spec_row = cursor.fetchone()

            if spec_row:
                # Обновляем существующую
                cursor.execute("""
                    UPDATE specifications
                    SET cutting_parts = %s, hardware = %s, variants = %s, updated_at = NOW()
                    WHERE id = %s
                """, (spec_data['cutting_parts'], spec_data['hardware'],
                      spec_data['variants'], spec_row[0]))
            else:
                # Создаем новую
                cursor.execute("""
                    INSERT INTO specifications
                    (model_id, version, is_default, is_active, cutting_parts, hardware, variants, uuid)
                    VALUES (%s, 1, true, true, %s, %s, %s, %s)
                """, (self.model_id, spec_data['cutting_parts'], spec_data['hardware'],
                      spec_data['variants'], str(uuid.uuid4())))

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

        return True

    def load_model_data(self):
        """Загрузка данных модели для редактирования"""
        # TODO: Реализовать загрузку данных из БД
        pass