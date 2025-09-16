"""
Форма просмотра и редактирования специфического варианта модели
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


class VariantViewEditForm(QDialog):
    """Форма просмотра и редактирования варианта модели"""

    saved = pyqtSignal()

    def __init__(self, parent=None, db=None, variant_id=None, read_only=False):
        super().__init__(parent)
        print("🚨 ОШИБКА: ЗАГРУЖАЕТСЯ СТАРАЯ упрощенная форма VariantViewEditForm!")
        print("🚨 Должна загружаться ModelSpecificVariantForm с вкладками и выбором материалов!")
        self.db = db
        self.variant_id = variant_id
        self.read_only = read_only
        self.mode = 'view' if read_only else 'edit'  # для обратной совместимости
        self.model_id = None
        self.variant_data = None

        self.setWindowTitle("🚨 СТАРАЯ упрощенная форма - " + ("Просмотр варианта" if read_only else "Редактирование варианта"))
        self.setModal(True)
        self.resize(1200, 800)

        self.init_ui()
        self.load_variant_data()

        # Установка режима только для чтения
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

                # Загружаем детали кроя
                cutting_parts = variant.get('cutting_parts', [])
                print(f"🔍 Исходный cutting_parts: {type(cutting_parts)} = {cutting_parts}")
                if isinstance(cutting_parts, str):
                    print("🔧 Применяем JSON парсинг...")
                    cutting_parts = json.loads(cutting_parts) if cutting_parts else []
                    print(f"✅ После парсинга: {type(cutting_parts)} = {cutting_parts}")
                self.load_cutting_parts(cutting_parts)

                # Загружаем фурнитуру
                hardware = variant.get('hardware', [])
                if isinstance(hardware, str):
                    hardware = json.loads(hardware) if hardware else []
                self.load_hardware(hardware)

                # Загружаем подошву
                sole = variant.get('sole')
                if isinstance(sole, str):
                    sole = json.loads(sole) if sole else None
                self.load_sole(sole)

            cursor.close()
            conn.close()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить вариант: {e}")

    def load_cutting_parts(self, cutting_parts):
        """Загрузка деталей кроя в таблицу"""
        print(f"🔍 load_cutting_parts вызван с: {type(cutting_parts)} = {cutting_parts}")

        if not cutting_parts:
            print("⚠️ cutting_parts пустой, выходим")
            return

        self.cutting_table.setRowCount(len(cutting_parts))

        # Получаем материалы для сопоставления цен
        materials = self.variant_data.get('materials', [])
        material_prices = {}
        if isinstance(materials, list):
            for mat in materials:
                material_prices[mat['id']] = float(mat.get('price', 0))
        elif isinstance(materials, dict):
            for mat_id, mat in materials.items():
                material_prices[int(mat_id)] = float(mat.get('price', 0))

        for row, part in enumerate(cutting_parts):
            # Название детали
            self.cutting_table.setItem(row, 0, QTableWidgetItem(part.get('name', '')))

            # Количество
            self.cutting_table.setItem(row, 1, QTableWidgetItem(str(part.get('quantity', 0))))

            # Материал - проверяем разные форматы данных
            material_text = ""
            material_id = None
            price = 0

            if 'material' in part and part['material']:
                # Новый формат с вложенным объектом material
                material_info = part['material']
                material_text = f"{material_info.get('name', '')} ({material_info.get('code', '')})"
                price = float(material_info.get('price', 0))
                material_id = material_info.get('id')
            elif 'material_name' in part:
                # Старый формат с отдельными полями
                material_text = f"{part.get('material_name', '')} ({part.get('material_code', '')})"
                material_id = part.get('material_id')
                if material_id and material_id in material_prices:
                    price = material_prices[material_id]

            self.cutting_table.setItem(row, 2, QTableWidgetItem(material_text))

            # Расход
            consumption = part.get('consumption', 0)
            if self.mode == 'edit':
                spin_box = QDoubleSpinBox()
                spin_box.setRange(0, 9999)
                spin_box.setValue(float(consumption))
                spin_box.setSuffix(" дм²")
                spin_box.valueChanged.connect(self.calculate_costs)
                self.cutting_table.setCellWidget(row, 3, spin_box)
            else:
                self.cutting_table.setItem(row, 3, QTableWidgetItem(f"{consumption} дм²"))

            # Цена за единицу
            self.cutting_table.setItem(row, 4, QTableWidgetItem(f"{price:.2f}"))

            # Стоимость
            cost = float(consumption) * price
            self.cutting_table.setItem(row, 5, QTableWidgetItem(f"{cost:.2f}"))

            # Примечание
            self.cutting_table.setItem(row, 6, QTableWidgetItem(part.get('notes', '')))

    def load_hardware(self, hardware):
        """Загрузка фурнитуры в таблицу"""
        if not hardware:
            return

        self.hardware_table.setRowCount(len(hardware))

        for row, hw in enumerate(hardware):
            self.hardware_table.setItem(row, 0, QTableWidgetItem(hw.get('name', '')))
            self.hardware_table.setItem(row, 1, QTableWidgetItem(str(hw.get('quantity', 0))))
            self.hardware_table.setItem(row, 2, QTableWidgetItem(hw.get('unit', '')))
            self.hardware_table.setItem(row, 3, QTableWidgetItem(hw.get('notes', '')))

    def load_sole(self, sole_data):
        """Загрузка данных о подошве"""
        if sole_data:
            self.sole_label.setText(f"{sole_data.get('name', '')} ({sole_data.get('code', '')})")
            self.sole_size_label.setText(sole_data.get('size_range', ''))

    def toggle_mode(self):
        """Переключение между режимами просмотра и редактирования"""
        if self.mode == 'view':
            self.mode = 'edit'
            self.mode_btn.setText("👁 Просмотр")
            self.setWindowTitle("Редактирование варианта")
            self.set_readonly(False)

            # Добавляем кнопку сохранения
            self.layout().itemAt(self.layout().count() - 1).widget().clear()
            buttons = self.layout().itemAt(self.layout().count() - 1).widget()
            save_btn = buttons.addButton("Сохранить", QDialogButtonBox.ButtonRole.AcceptRole)
            save_btn.clicked.connect(self.save_variant)

        else:
            self.mode = 'view'
            self.mode_btn.setText("✏️ Редактировать")
            self.setWindowTitle("Просмотр варианта")
            self.set_readonly(True)

    def set_readonly(self, readonly):
        """Установка режима только для чтения"""
        self.variant_name_input.setReadOnly(readonly)
        self.variant_code_input.setReadOnly(readonly)
        self.description_input.setReadOnly(readonly)

        # Для таблиц устанавливаем флаг редактирования
        if readonly:
            self.cutting_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
            self.hardware_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        else:
            self.cutting_table.setEditTriggers(QTableWidget.EditTrigger.AllEditTriggers)
            self.hardware_table.setEditTriggers(QTableWidget.EditTrigger.AllEditTriggers)

    def calculate_costs(self):
        """Пересчет стоимости"""
        total_cost = 0

        for row in range(self.cutting_table.rowCount()):
            # Получаем расход
            consumption_widget = self.cutting_table.cellWidget(row, 3)
            if consumption_widget:
                consumption = consumption_widget.value()
            else:
                consumption_item = self.cutting_table.item(row, 3)
                consumption = float(consumption_item.text().replace(' дм²', '')) if consumption_item else 0

            # Получаем цену
            price_item = self.cutting_table.item(row, 4)
            price = float(price_item.text()) if price_item else 0

            # Рассчитываем стоимость
            cost = consumption * price
            self.cutting_table.setItem(row, 5, QTableWidgetItem(f"{cost:.2f}"))

            total_cost += cost

        self.total_cost_label.setText(f"{total_cost:.2f} руб")

    def save_variant(self):
        """Сохранение изменений варианта"""
        try:
            # Собираем обновленные данные
            cutting_parts = []
            for row in range(self.cutting_table.rowCount()):
                # Получаем расход
                consumption_widget = self.cutting_table.cellWidget(row, 3)
                if consumption_widget:
                    consumption = consumption_widget.value()
                else:
                    consumption_item = self.cutting_table.item(row, 3)
                    consumption = float(consumption_item.text().replace(' дм²', '')) if consumption_item else 0

                part = {
                    'name': self.cutting_table.item(row, 0).text(),
                    'quantity': float(self.cutting_table.item(row, 1).text()),
                    'consumption': consumption,
                    'notes': self.cutting_table.item(row, 6).text() if self.cutting_table.item(row, 6) else ''
                }

                # Добавляем информацию о материале если она есть в исходных данных
                if self.variant_data and self.variant_data.get('cutting_parts'):
                    for orig_part in self.variant_data['cutting_parts']:
                        if orig_part.get('name') == part['name']:
                            # Сохраняем в том же формате, что и в БД
                            if 'material' in orig_part:
                                part['material'] = orig_part['material']
                            else:
                                # Старый формат с отдельными полями
                                part['material_id'] = orig_part.get('material_id')
                                part['material_code'] = orig_part.get('material_code')
                                part['material_name'] = orig_part.get('material_name')
                            break

                cutting_parts.append(part)

            # Собираем фурнитуру
            hardware = []
            for row in range(self.hardware_table.rowCount()):
                hw = {
                    'name': self.hardware_table.item(row, 0).text(),
                    'quantity': float(self.hardware_table.item(row, 1).text()),
                    'unit': self.hardware_table.item(row, 2).text(),
                    'notes': self.hardware_table.item(row, 3).text() if self.hardware_table.item(row, 3) else ''
                }
                hardware.append(hw)

            # Пересчитываем материалы - используем исходный формат materials
            materials = self.variant_data.get('materials', [])
            material_dict = {}
            total_cost = 0

            # Преобразуем materials в словарь для удобства
            if isinstance(materials, list):
                for mat in materials:
                    material_dict[mat['id']] = mat
            elif isinstance(materials, dict):
                material_dict = materials

            # Обнуляем расход
            for mat_id in material_dict:
                if isinstance(material_dict[mat_id], dict):
                    material_dict[mat_id]['total_consumption'] = 0

            # Пересчитываем расход и стоимость
            for part in cutting_parts:
                mat_id = None
                price = 0

                if 'material' in part and part['material']:
                    mat_id = part['material']['id']
                    price = float(part['material'].get('price', 0) or 0)
                elif 'material_id' in part:
                    mat_id = part['material_id']
                    if mat_id in material_dict:
                        price = float(material_dict[mat_id].get('price', 0) or 0)

                if mat_id and mat_id in material_dict:
                    material_dict[mat_id]['total_consumption'] += part['consumption']
                    cost = part['consumption'] * price
                    total_cost += cost

            # Конвертируем обратно в список если нужно
            if isinstance(materials, list):
                materials = list(material_dict.values())
            else:
                materials = material_dict

            # Обновляем в базе данных
            conn = self.db.get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE specifications
                SET variant_name = %s,
                    variant_code = %s,
                    description = %s,
                    cutting_parts = %s,
                    hardware = %s,
                    materials = %s,
                    total_cost = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (
                self.variant_name_input.text(),
                self.variant_code_input.text(),
                self.description_input.toPlainText(),
                json.dumps(cutting_parts, ensure_ascii=False),
                json.dumps(hardware, ensure_ascii=False),
                json.dumps(materials, ensure_ascii=False),
                total_cost,
                self.variant_id
            ))

            conn.commit()
            cursor.close()
            conn.close()

            QMessageBox.information(self, "Успех", "Вариант успешно обновлен")
            self.saved.emit()

            # Переключаемся обратно в режим просмотра
            self.toggle_mode()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить вариант: {e}")