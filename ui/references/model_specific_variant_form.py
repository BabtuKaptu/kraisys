"""
Форма создания специфического варианта модели с выбором материалов для каждой детали
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QLineEdit, QComboBox, QGroupBox, QTabWidget,
    QWidget, QHeaderView, QAbstractItemView, QMessageBox, QSpinBox,
    QDoubleSpinBox
)
from PyQt6.QtCore import Qt, pyqtSignal
import psycopg2
import psycopg2.extras
import uuid
import json

class ModelSpecificVariantForm(QDialog):
    """Форма создания специфического варианта модели"""

    saved = pyqtSignal()

    def __init__(self, parent=None, db=None, model_id=None):
        super().__init__(parent)
        self.db = db
        self.model_id = model_id
        self.base_model_data = None
        self.variant_id = None

        self.setWindowTitle("Создание специфического варианта модели")
        self.setModal(True)
        self.resize(1200, 700)

        self.init_ui()
        self.load_references()

        if self.model_id:
            self.load_base_model()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Информация о базовой модели
        info_group = QGroupBox("Базовая модель")
        info_layout = QHBoxLayout()

        self.model_info_label = QLabel("Загрузка...")
        info_layout.addWidget(self.model_info_label)
        info_layout.addStretch()

        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        # Информация о варианте
        variant_group = QGroupBox("Специфический вариант")
        variant_layout = QHBoxLayout()

        variant_layout.addWidget(QLabel("Название варианта:"))
        self.variant_name_input = QLineEdit()
        self.variant_name_input.setPlaceholderText("Например: Летняя коллекция 2024")
        variant_layout.addWidget(self.variant_name_input)

        variant_layout.addWidget(QLabel("Код варианта:"))
        self.variant_code_input = QLineEdit()
        self.variant_code_input.setPlaceholderText("Например: VAR-001")
        variant_layout.addWidget(self.variant_code_input)

        variant_group.setLayout(variant_layout)
        layout.addWidget(variant_group)

        # Вкладки для компонентов
        self.tabs = QTabWidget()

        # Вкладка деталей кроя с выбором материалов
        self.cutting_tab = self.create_cutting_tab()
        self.tabs.addTab(self.cutting_tab, "🔨 Детали кроя с материалами")

        # Вкладка фурнитуры
        self.hardware_tab = self.create_hardware_tab()
        self.tabs.addTab(self.hardware_tab, "🔩 Фурнитура")

        # Вкладка подошв
        self.sole_tab = self.create_sole_tab()
        self.tabs.addTab(self.sole_tab, "👟 Подошвы")

        layout.addWidget(self.tabs)

        # Кнопки управления
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        self.save_btn = QPushButton("💾 Сохранить вариант")
        self.save_btn.clicked.connect(self.save_variant)
        buttons_layout.addWidget(self.save_btn)

        self.cancel_btn = QPushButton("Отмена")
        self.cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(self.cancel_btn)

        layout.addLayout(buttons_layout)

    def create_cutting_tab(self):
        """Вкладка деталей кроя с выбором материалов"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        info = QLabel(
            "💡 Выберите конкретный материал для каждой детали кроя. "
            "Это позволит точно рассчитать себестоимость и создать спецификацию для производства."
        )
        info.setWordWrap(True)
        info.setStyleSheet("background: #f0f8ff; padding: 10px; border-radius: 5px;")
        layout.addWidget(info)

        # Таблица деталей кроя с материалами
        self.cutting_table = QTableWidget()
        self.cutting_table.setColumnCount(6)
        self.cutting_table.setHorizontalHeaderLabels([
            "Деталь кроя", "Количество", "Материал", "Расход (дм²)", "Цена за дм²", "Стоимость"
        ])

        header = self.cutting_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)

        header.resizeSection(1, 100)
        header.resizeSection(3, 100)
        header.resizeSection(4, 100)
        header.resizeSection(5, 120)

        layout.addWidget(self.cutting_table)

        # Итоговая стоимость материалов
        total_layout = QHBoxLayout()
        total_layout.addStretch()
        total_layout.addWidget(QLabel("Итого стоимость материалов:"))
        self.total_material_cost_label = QLabel("0.00 руб")
        self.total_material_cost_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        total_layout.addWidget(self.total_material_cost_label)
        layout.addLayout(total_layout)

        return widget

    def create_hardware_tab(self):
        """Вкладка фурнитуры"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        info = QLabel(
            "💡 Фурнитура и комплектующие для данного варианта модели."
        )
        info.setWordWrap(True)
        info.setStyleSheet("background: #f0f8ff; padding: 10px; border-radius: 5px;")
        layout.addWidget(info)

        # Таблица фурнитуры
        self.hardware_table = QTableWidget()
        self.hardware_table.setColumnCount(5)
        self.hardware_table.setHorizontalHeaderLabels([
            "Наименование", "Количество", "Ед. изм.", "Цена за ед.", "Стоимость"
        ])

        header = self.hardware_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)

        self.hardware_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        layout.addWidget(self.hardware_table)

        return widget

    def create_sole_tab(self):
        """Вкладка подошв"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        info = QLabel(
            "💡 Выберите конкретную подошву для данного варианта модели."
        )
        info.setWordWrap(True)
        info.setStyleSheet("background: #f0f8ff; padding: 10px; border-radius: 5px;")
        layout.addWidget(info)

        # Выбор подошвы
        sole_layout = QHBoxLayout()
        sole_layout.addWidget(QLabel("Подошва:"))

        self.sole_combo = QComboBox()
        self.sole_combo.setMinimumWidth(400)
        sole_layout.addWidget(self.sole_combo)

        sole_layout.addWidget(QLabel("Размерный ряд:"))
        self.sole_size_label = QLabel("")
        sole_layout.addWidget(self.sole_size_label)

        sole_layout.addStretch()
        layout.addLayout(sole_layout)

        layout.addStretch()

        return widget

    def load_references(self):
        """Загрузка справочников"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

            # Загрузка материалов (кожи и подкладка)
            cursor.execute("""
                SELECT id, code, name, material_type, unit, price
                FROM materials
                WHERE is_active = true
                AND group_type IN ('LEATHER', 'LINING')
                ORDER BY material_type, name
            """)

            self.materials_list = cursor.fetchall()

            # Загрузка подошв
            cursor.execute("""
                SELECT id, code, name, unit, price
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
                if sole['price']:
                    display_text += f" ({sole['price']} руб)"
                self.sole_combo.addItem(display_text, sole)

            cursor.close()
            self.db.put_connection(conn)

        except Exception as e:
            QMessageBox.warning(self, "Предупреждение", f"Не удалось загрузить справочники: {e}")

    def load_base_model(self):
        """Загрузка данных базовой модели"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

            # Загрузка основных данных модели
            cursor.execute("SELECT * FROM models WHERE id = %s", (self.model_id,))
            model = cursor.fetchone()

            if model:
                self.base_model_data = model
                self.model_info_label.setText(
                    f"Артикул: {model['article']} | "
                    f"Название: {model['name']} | "
                    f"Колодка: {model['last_code']} | "
                    f"Размеры: {model['size_min']}-{model['size_max']}"
                )

                # Загружаем компоненты модели
                cursor.execute("""
                    SELECT component_name, component_group, absolute_consumption, unit, notes
                    FROM model_components
                    WHERE model_id = %s
                    ORDER BY sort_order
                """, (self.model_id,))

                components = cursor.fetchall()

                # Заполняем таблицу деталей кроя
                for comp in components:
                    if comp['component_group'] == 'cutting':
                        row = self.cutting_table.rowCount()
                        self.cutting_table.insertRow(row)

                        # Деталь кроя
                        self.cutting_table.setItem(row, 0, QTableWidgetItem(comp['component_name']))

                        # Количество (по умолчанию пара)
                        self.cutting_table.setItem(row, 1, QTableWidgetItem("2"))

                        # Комбобокс для выбора материала
                        material_combo = QComboBox()
                        material_combo.addItem("Выберите материал...", None)

                        for mat in self.materials_list:
                            display_text = f"{mat['code']} - {mat['name']} ({mat['material_type']})"
                            if mat['price']:
                                display_text += f" - {mat['price']} руб/{mat['unit']}"
                            material_combo.addItem(display_text, mat)

                        material_combo.currentIndexChanged.connect(self.calculate_costs)
                        self.cutting_table.setCellWidget(row, 2, material_combo)

                        # Расход
                        consumption = comp['absolute_consumption'] if comp['absolute_consumption'] else 0
                        self.cutting_table.setItem(row, 3, QTableWidgetItem(f"{consumption:.2f}"))

                        # Цена за единицу (будет заполнена при выборе материала)
                        self.cutting_table.setItem(row, 4, QTableWidgetItem("0.00"))

                        # Стоимость (будет рассчитана)
                        self.cutting_table.setItem(row, 5, QTableWidgetItem("0.00"))

                    elif comp['component_group'] == 'material':
                        # Добавляем фурнитуру
                        row = self.hardware_table.rowCount()
                        self.hardware_table.insertRow(row)

                        self.hardware_table.setItem(row, 0, QTableWidgetItem(comp['component_name']))
                        quantity = comp['absolute_consumption'] if comp['absolute_consumption'] else 1
                        self.hardware_table.setItem(row, 1, QTableWidgetItem(f"{quantity:.2f}"))
                        self.hardware_table.setItem(row, 2, QTableWidgetItem(comp['unit'] or 'шт'))
                        self.hardware_table.setItem(row, 3, QTableWidgetItem("0.00"))
                        self.hardware_table.setItem(row, 4, QTableWidgetItem("0.00"))

                    elif comp['component_group'] == 'sole':
                        # Устанавливаем размерный ряд для подошвы
                        self.sole_size_label.setText(comp['unit'] or '')

            cursor.close()
            self.db.put_connection(conn)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить данные модели: {e}")

    def calculate_costs(self):
        """Расчет стоимости материалов"""
        total_cost = 0

        for row in range(self.cutting_table.rowCount()):
            material_combo = self.cutting_table.cellWidget(row, 2)
            if material_combo and material_combo.currentData():
                material = material_combo.currentData()

                # Получаем расход
                consumption_item = self.cutting_table.item(row, 3)
                consumption = float(consumption_item.text()) if consumption_item else 0

                # Получаем цену материала
                price = material.get('price', 0) or 0

                # Записываем цену за единицу
                self.cutting_table.setItem(row, 4, QTableWidgetItem(f"{price:.2f}"))

                # Рассчитываем стоимость
                cost = consumption * price
                self.cutting_table.setItem(row, 5, QTableWidgetItem(f"{cost:.2f}"))

                total_cost += cost

        self.total_material_cost_label.setText(f"{total_cost:.2f} руб")

    def validate(self):
        """Валидация формы"""
        if not self.variant_name_input.text():
            QMessageBox.warning(self, "Ошибка", "Укажите название варианта")
            return False

        if not self.variant_code_input.text():
            QMessageBox.warning(self, "Ошибка", "Укажите код варианта")
            return False

        # Проверка выбора материалов для всех деталей кроя
        for row in range(self.cutting_table.rowCount()):
            material_combo = self.cutting_table.cellWidget(row, 2)
            if not material_combo or not material_combo.currentData():
                detail_name = self.cutting_table.item(row, 0).text()
                QMessageBox.warning(self, "Ошибка", f"Выберите материал для детали: {detail_name}")
                return False

        return True

    def save_variant(self):
        """Сохранение специфического варианта в БД"""
        if not self.validate():
            return

        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            # Подготовка данных для сохранения
            cutting_parts = []
            materials = {}
            total_cost = 0

            # Собираем данные о деталях кроя и материалах
            for row in range(self.cutting_table.rowCount()):
                part_name = self.cutting_table.item(row, 0).text()
                quantity = int(self.cutting_table.item(row, 1).text())
                material_combo = self.cutting_table.cellWidget(row, 2)
                material = material_combo.currentData()
                consumption = float(self.cutting_table.item(row, 3).text())

                cutting_part = {
                    "name": part_name,
                    "quantity": quantity,
                    "consumption": consumption,
                    "material_id": material['id'],
                    "material_code": material['code'],
                    "material_name": material['name']
                }
                cutting_parts.append(cutting_part)

                # Добавляем материал в список
                if material['id'] not in materials:
                    materials[material['id']] = {
                        "id": material['id'],
                        "code": material['code'],
                        "name": material['name'],
                        "type": material['material_type'],
                        "unit": material['unit'],
                        "price": material.get('price', 0),
                        "total_consumption": 0
                    }
                materials[material['id']]['total_consumption'] += consumption

                # Считаем общую стоимость
                cost = consumption * (material.get('price', 0) or 0)
                total_cost += cost

            # Собираем данные о фурнитуре
            hardware = []
            for row in range(self.hardware_table.rowCount()):
                hw = {
                    "name": self.hardware_table.item(row, 0).text(),
                    "quantity": float(self.hardware_table.item(row, 1).text()),
                    "unit": self.hardware_table.item(row, 2).text()
                }
                hardware.append(hw)

            # Данные о подошве
            sole_data = self.sole_combo.currentData()
            sole_info = None
            if sole_data:
                sole_info = {
                    "id": sole_data['id'],
                    "code": sole_data['code'],
                    "name": sole_data['name'],
                    "size_range": self.sole_size_label.text()
                }

            # Сохраняем в таблицу specifications
            cursor.execute("""
                INSERT INTO specifications (
                    uuid, model_id, variant_name, variant_code,
                    is_default, is_active, materials, cutting_parts, hardware,
                    total_material_cost, created_at, updated_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                RETURNING id
            """, (
                str(uuid.uuid4()),
                self.model_id,
                self.variant_name_input.text(),
                self.variant_code_input.text(),
                False,  # Это не базовый вариант
                True,   # Активен
                json.dumps(list(materials.values())),
                json.dumps(cutting_parts),
                json.dumps(hardware),
                total_cost
            ))

            self.variant_id = cursor.fetchone()[0]

            conn.commit()
            cursor.close()
            self.db.put_connection(conn)

            QMessageBox.information(self, "Успешно",
                f"Специфический вариант '{self.variant_name_input.text()}' сохранен.\n"
                f"Общая стоимость материалов: {total_cost:.2f} руб")

            self.saved.emit()
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить вариант: {e}")