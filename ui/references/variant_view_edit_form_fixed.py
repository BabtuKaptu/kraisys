"""
Форма просмотра и редактирования специфического варианта модели - ИСПРАВЛЕННАЯ ВЕРСИЯ
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QLineEdit, QTableWidget, QTableWidgetItem,
    QGroupBox, QGridLayout, QTextEdit, QMessageBox,
    QDialogButtonBox, QHeaderView, QComboBox, QDoubleSpinBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
import psycopg2.extras
import json
from uuid import uuid4


class VariantViewEditFormFixed(QDialog):
    """Форма просмотра и редактирования варианта модели - ИСПРАВЛЕННАЯ"""

    saved = pyqtSignal()

    def __init__(self, parent=None, db=None, variant_id=None, read_only=False):
        super().__init__(parent)
        self.db = db
        self.variant_id = variant_id
        self.read_only = read_only
        self.mode = 'view' if read_only else 'edit'
        self.model_id = None
        self.variant_data = None

        self.setWindowTitle("Просмотр варианта (ИСПРАВЛЕНО)" if read_only else "Редактирование варианта (ИСПРАВЛЕНО)")
        self.setModal(True)
        self.resize(1200, 800)

        self.init_ui()
        self.load_variant_data()

        if self.read_only:
            self.set_readonly(True)

    def init_ui(self):
        """Инициализация интерфейса"""
        layout = QVBoxLayout(self)

        # Заголовок
        header_layout = QHBoxLayout()
        self.title_label = QLabel()
        self.title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()

        # Кнопка переключения режима
        self.mode_btn = QPushButton("✏️ Редактировать" if self.mode == 'view' else "👁 Просмотр")
        self.mode_btn.clicked.connect(self.toggle_mode)
        header_layout.addWidget(self.mode_btn)

        layout.addLayout(header_layout)

        # Основная информация
        info_group = QGroupBox("Основная информация")
        info_layout = QGridLayout()

        info_layout.addWidget(QLabel("Название варианта:"), 0, 0)
        self.variant_name_input = QLineEdit()
        info_layout.addWidget(self.variant_name_input, 0, 1)

        info_layout.addWidget(QLabel("Код варианта:"), 0, 2)
        self.variant_code_input = QLineEdit()
        info_layout.addWidget(self.variant_code_input, 0, 3)

        info_layout.addWidget(QLabel("Описание:"), 1, 0)
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(60)
        info_layout.addWidget(self.description_input, 1, 1, 1, 3)

        info_layout.addWidget(QLabel("Общая стоимость:"), 2, 0)
        self.total_cost_label = QLabel("0.00 руб")
        self.total_cost_label.setStyleSheet("font-weight: bold; color: #2196F3;")
        info_layout.addWidget(self.total_cost_label, 2, 1)

        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        # Детали кроя
        cutting_group = QGroupBox("Детали кроя")
        cutting_layout = QVBoxLayout()

        self.cutting_table = QTableWidget()
        self.cutting_table.setColumnCount(7)
        self.cutting_table.setHorizontalHeaderLabels([
            "Деталь", "Кол-во", "Материал", "Расход",
            "Цена/ед", "Стоимость", "Примечание"
        ])
        self.cutting_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        cutting_layout.addWidget(self.cutting_table)

        cutting_group.setLayout(cutting_layout)
        layout.addWidget(cutting_group)

        # Фурнитура
        hardware_group = QGroupBox("Фурнитура")
        hardware_layout = QVBoxLayout()

        self.hardware_table = QTableWidget()
        self.hardware_table.setColumnCount(4)
        self.hardware_table.setHorizontalHeaderLabels(["Название", "Кол-во", "Ед.изм.", "Примечание"])
        self.hardware_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        hardware_layout.addWidget(self.hardware_table)

        hardware_group.setLayout(hardware_layout)
        layout.addWidget(hardware_group)

        # Подошва
        sole_group = QGroupBox("Подошва")
        sole_layout = QGridLayout()

        sole_layout.addWidget(QLabel("Подошва:"), 0, 0)
        self.sole_label = QLabel()
        sole_layout.addWidget(self.sole_label, 0, 1)

        sole_layout.addWidget(QLabel("Размерный ряд:"), 0, 2)
        self.sole_size_label = QLabel()
        sole_layout.addWidget(self.sole_size_label, 0, 3)

        sole_group.setLayout(sole_layout)
        layout.addWidget(sole_group)

        # Кнопки
        buttons = QDialogButtonBox()

        if self.mode == 'edit':
            save_btn = buttons.addButton("Сохранить", QDialogButtonBox.ButtonRole.AcceptRole)
            save_btn.clicked.connect(self.save_variant)

        cancel_btn = buttons.addButton("Закрыть", QDialogButtonBox.ButtonRole.RejectRole)
        cancel_btn.clicked.connect(self.reject)

        layout.addWidget(buttons)

    def load_variant_data(self):
        """Загрузка данных варианта"""
        print("🔍 ИСПРАВЛЕННАЯ load_variant_data вызвана")
        if not self.variant_id:
            return

        try:
            conn = self.db.get_connection()
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

            # Загружаем данные варианта
            cursor.execute("""
                SELECT s.*, m.name as model_name, m.article as model_article
                FROM specifications s
                JOIN models m ON s.model_id = m.id
                WHERE s.id = %s
            """, (self.variant_id,))

            variant = cursor.fetchone()

            if variant:
                self.variant_data = variant
                self.model_id = variant['model_id']

                # Заполняем форму
                self.title_label.setText(f"{variant['model_name']} - Вариант: {variant['variant_name'] or 'Без названия'}")
                self.variant_name_input.setText(variant['variant_name'] or '')
                self.variant_code_input.setText(variant['variant_code'] or '')
                self.description_input.setText(variant.get('description', '') or '')

                if variant.get('total_cost'):
                    self.total_cost_label.setText(f"{float(variant['total_cost']):.2f} руб")

                # ИСПРАВЛЕНИЕ: обрабатываем cutting_parts
                cutting_parts = variant.get('cutting_parts', [])
                print(f"🔍 ИСПРАВЛЕННАЯ: cutting_parts тип = {type(cutting_parts)}")
                print(f"🔍 ИСПРАВЛЕННАЯ: cutting_parts = {cutting_parts}")

                # ПРАВИЛЬНАЯ обработка JSON данных
                if isinstance(cutting_parts, str):
                    print("🔧 ИСПРАВЛЕНИЕ: parsing JSON string")
                    try:
                        cutting_parts = json.loads(cutting_parts) if cutting_parts else []
                    except json.JSONDecodeError:
                        print("❌ ОШИБКА парсинга JSON")
                        cutting_parts = []
                elif cutting_parts is None:
                    cutting_parts = []

                self.load_cutting_parts(cutting_parts)

                # Обработка hardware
                hardware = variant.get('hardware', [])
                if isinstance(hardware, str):
                    try:
                        hardware = json.loads(hardware) if hardware else []
                    except json.JSONDecodeError:
                        hardware = []
                elif hardware is None:
                    hardware = []

                self.load_hardware(hardware)

                # Обработка sole
                sole = variant.get('sole')
                if isinstance(sole, str):
                    try:
                        sole = json.loads(sole) if sole else None
                    except json.JSONDecodeError:
                        sole = None

                self.load_sole(sole)

            cursor.close()
            conn.close()

        except Exception as e:
            print(f"❌ ИСПРАВЛЕННАЯ: Ошибка загрузки: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить вариант: {e}")

    def load_cutting_parts(self, cutting_parts):
        """Загрузка деталей кроя в таблицу"""
        print(f"🔍 ИСПРАВЛЕННАЯ load_cutting_parts: {type(cutting_parts)} = {cutting_parts}")

        if not cutting_parts:
            print("⚠️ ИСПРАВЛЕННАЯ: cutting_parts пустой")
            return

        try:
            self.cutting_table.setRowCount(len(cutting_parts))

            for row, part in enumerate(cutting_parts):
                print(f"🔍 ИСПРАВЛЕННАЯ: обрабатываем part[{row}] = {part}, тип = {type(part)}")

                # ИСПРАВЛЕНИЕ: проверяем что part это словарь
                if not isinstance(part, dict):
                    print(f"❌ ИСПРАВЛЕННАЯ: part не словарь: {part}")
                    continue

                # Название детали
                name = part.get('name', '')
                self.cutting_table.setItem(row, 0, QTableWidgetItem(str(name)))

                # Количество
                quantity = part.get('quantity', 0)
                self.cutting_table.setItem(row, 1, QTableWidgetItem(str(quantity)))

                # Материал - ИСПРАВЛЕННАЯ логика отображения
                material_text = ""
                price = 0

                # Получаем материалы для сопоставления цен
                materials = self.variant_data.get('materials', [])
                material_prices = {}
                if isinstance(materials, list):
                    for mat in materials:
                        if isinstance(mat, dict):
                            material_prices[mat.get('id')] = float(mat.get('price', 0))

                if 'material' in part and isinstance(part['material'], dict):
                    material_info = part['material']
                    material_text = f"{material_info.get('name', '')} ({material_info.get('code', '')})"
                    price = float(material_info.get('price', 0))
                elif 'material_name' in part:
                    material_text = f"{part.get('material_name', '')} ({part.get('material_code', '')})"
                    material_id = part.get('material_id')
                    if material_id and material_id in material_prices:
                        price = material_prices[material_id]
                elif 'material' in part and isinstance(part['material'], str):
                    material_text = part['material']
                else:
                    material_text = "Материал не указан"

                self.cutting_table.setItem(row, 2, QTableWidgetItem(material_text))

                # Расход
                consumption = part.get('consumption', 0)
                if self.mode == 'edit':
                    spin_box = QDoubleSpinBox()
                    spin_box.setRange(0, 9999)
                    spin_box.setValue(float(consumption))
                    spin_box.setSuffix(" дм²")
                    self.cutting_table.setCellWidget(row, 3, spin_box)
                else:
                    self.cutting_table.setItem(row, 3, QTableWidgetItem(f"{consumption} дм²"))

                # Цена за единицу
                self.cutting_table.setItem(row, 4, QTableWidgetItem(f"{price:.2f}"))

                # Стоимость
                cost = float(consumption) * price
                self.cutting_table.setItem(row, 5, QTableWidgetItem(f"{cost:.2f}"))

                # Примечание
                notes = part.get('notes', '')
                self.cutting_table.setItem(row, 6, QTableWidgetItem(str(notes)))

            print("✅ ИСПРАВЛЕННАЯ: load_cutting_parts завершена успешно")

        except Exception as e:
            print(f"❌ ИСПРАВЛЕННАЯ: Ошибка в load_cutting_parts: {e}")
            import traceback
            traceback.print_exc()

    def load_hardware(self, hardware):
        """Загрузка фурнитуры в таблицу"""
        if not hardware:
            return

        try:
            self.hardware_table.setRowCount(len(hardware))

            for row, hw in enumerate(hardware):
                if isinstance(hw, dict):
                    self.hardware_table.setItem(row, 0, QTableWidgetItem(hw.get('name', '')))
                    self.hardware_table.setItem(row, 1, QTableWidgetItem(str(hw.get('quantity', 0))))
                    self.hardware_table.setItem(row, 2, QTableWidgetItem(hw.get('unit', '')))
                    self.hardware_table.setItem(row, 3, QTableWidgetItem(hw.get('notes', '')))

        except Exception as e:
            print(f"❌ ИСПРАВЛЕННАЯ: Ошибка в load_hardware: {e}")

    def load_sole(self, sole_data):
        """Загрузка данных о подошве"""
        if sole_data and isinstance(sole_data, dict):
            self.sole_label.setText(f"{sole_data.get('name', '')} ({sole_data.get('code', '')})")
            self.sole_size_label.setText(sole_data.get('size_range', ''))

    def toggle_mode(self):
        """Переключение между режимами просмотра и редактирования"""
        if self.mode == 'view':
            self.mode = 'edit'
            self.mode_btn.setText("👁 Просмотр")
            self.setWindowTitle("Редактирование варианта (ИСПРАВЛЕНО)")
            self.set_readonly(False)
        else:
            self.mode = 'view'
            self.mode_btn.setText("✏️ Редактировать")
            self.setWindowTitle("Просмотр варианта (ИСПРАВЛЕНО)")
            self.set_readonly(True)

    def set_readonly(self, readonly):
        """Установка режима только для чтения"""
        self.variant_name_input.setReadOnly(readonly)
        self.variant_code_input.setReadOnly(readonly)
        self.description_input.setReadOnly(readonly)

        if readonly:
            self.cutting_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
            self.hardware_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        else:
            self.cutting_table.setEditTriggers(QTableWidget.EditTrigger.AllEditTriggers)
            self.hardware_table.setEditTriggers(QTableWidget.EditTrigger.AllEditTriggers)

    def save_variant(self):
        """Сохранение изменений варианта"""
        QMessageBox.information(self, "Информация", "Сохранение в исправленной версии пока не реализовано")