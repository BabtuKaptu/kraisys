"""Full materials reference view with database integration"""
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDoubleValidator
from ui.base.base_table_v2 import BaseTableWidgetV2
from ui.base.base_form import BaseFormDialog
from database.connection import DatabaseConnection
import psycopg2.extras
import json


class MaterialsTableFullWidget(BaseTableWidgetV2):
    """Полная таблица материалов с интеграцией БД"""

    def __init__(self, parent=None):
        super().__init__('materials', parent)
        self.setWindowTitle("Материалы и комплектующие")

    def get_visible_columns(self):
        """Переопределяем видимые колонки для материалов"""
        return ['code', 'name', 'group_type', 'material_type', 'color',
                'unit', 'price', 'supplier_name', 'is_active']

    def get_column_label(self, column_name):
        """Метки колонок для материалов"""
        labels = {
            'code': 'Код',
            'name': 'Название',
            'name_en': 'Название (англ)',
            'group_type': 'Группа',
            'subgroup': 'Подгруппа',
            'material_type': 'Тип',
            'color': 'Цвет',
            'texture': 'Текстура',
            'thickness': 'Толщина',
            'density': 'Плотность',
            'unit': 'Ед.изм',
            'unit_secondary': 'Ед.изм.2',
            'conversion_factor': 'Коэфф.перевода',
            'price': 'Цена',
            'currency': 'Валюта',
            'supplier_name': 'Поставщик',
            'supplier_code': 'Код поставщика',
            'lead_time_days': 'Срок поставки',
            'min_order_qty': 'Мин.заказ',
            'order_multiplicity': 'Кратность',
            'safety_stock': 'Страх.запас',
            'reorder_point': 'Точка заказа',
            'max_stock': 'Макс.запас',
            'storage_conditions': 'Условия хранения',
            'is_active': 'Активен',
            'is_critical': 'Критичный'
        }
        return labels.get(column_name, column_name.replace('_', ' ').title())

    def get_search_columns(self):
        """Колонки для поиска"""
        return ['code', 'name', 'supplier_name', 'material_type']

    def add_record(self):
        dialog = MaterialFullFormDialog("Новый материал", self)
        if dialog.exec():
            self.refresh_data()

    def edit_record(self):
        record_id = self.get_current_record_id()
        if record_id:
            dialog = MaterialFullFormDialog("Редактирование материала", self)
            dialog.load_data(record_id)
            if dialog.exec():
                self.refresh_data()


class MaterialFullFormDialog(BaseFormDialog):
    """Полная форма редактирования материала"""

    def __init__(self, title: str, parent=None):
        self.record_id = None
        self.db = DatabaseConnection()
        super().__init__(title, parent)
        self.resize(900, 700)

    def create_form_content(self):
        # Табы для группировки
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs)

        # Вкладки
        self.create_main_tab()
        self.create_specs_tab()
        self.create_supply_tab()
        self.create_stock_tab()

    def create_main_tab(self):
        """Основные данные"""
        tab = QWidget()
        layout = QFormLayout(tab)

        # Код
        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("Уникальный код материала")
        layout.addRow("Код:", self.code_input)

        # Название
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Название материала")
        layout.addRow("Название:", self.name_input)

        # Название на английском
        self.name_en_input = QLineEdit()
        self.name_en_input.setPlaceholderText("English name")
        layout.addRow("Название (англ):", self.name_en_input)

        # Группа (используем английские значения из enum)
        self.group_combo = QComboBox()
        # Добавляем пары (отображение, значение для БД)
        self.group_items = [
            ("", None),
            ("Кожа", "LEATHER"),
            ("Подошва", "SOLE"),
            ("Фурнитура", "HARDWARE"),
            ("Подкладка", "LINING"),
            ("Химия", "CHEMICAL"),
            ("Упаковка", "PACKAGING")
        ]
        for display, value in self.group_items:
            self.group_combo.addItem(display, value)
        layout.addRow("Группа:", self.group_combo)

        # Подгруппа
        self.subgroup_input = QLineEdit()
        self.subgroup_input.setPlaceholderText("Подгруппа материала")
        layout.addRow("Подгруппа:", self.subgroup_input)

        # Тип материала
        self.material_type_input = QLineEdit()
        self.material_type_input.setPlaceholderText("Например: натуральная, искусственная")
        layout.addRow("Тип материала:", self.material_type_input)

        # Цвет
        self.color_input = QLineEdit()
        self.color_input.setPlaceholderText("Цвет материала")
        layout.addRow("Цвет:", self.color_input)

        # Активность
        self.is_active_check = QCheckBox()
        self.is_active_check.setChecked(True)
        layout.addRow("Активен:", self.is_active_check)

        # Критичность
        self.is_critical_check = QCheckBox()
        layout.addRow("Критичный материал:", self.is_critical_check)

        self.tabs.addTab(tab, "📋 Основные данные")

    def create_specs_tab(self):
        """Характеристики"""
        tab = QWidget()
        layout = QFormLayout(tab)

        # Текстура
        self.texture_input = QLineEdit()
        self.texture_input.setPlaceholderText("Гладкая, рельефная, замша...")
        layout.addRow("Текстура:", self.texture_input)

        # Толщина
        self.thickness_spin = QDoubleSpinBox()
        self.thickness_spin.setRange(0, 100)
        self.thickness_spin.setDecimals(2)
        self.thickness_spin.setSuffix(" мм")
        layout.addRow("Толщина:", self.thickness_spin)

        # Плотность
        self.density_spin = QDoubleSpinBox()
        self.density_spin.setRange(0, 9999)
        self.density_spin.setDecimals(3)
        self.density_spin.setSuffix(" г/см³")
        layout.addRow("Плотность:", self.density_spin)

        # Единицы измерения
        layout.addRow(QLabel("<b>Единицы измерения:</b>"))

        self.unit_combo = QComboBox()
        self.unit_combo.addItems([
            "дм²", "м²", "м", "кг", "г", "л", "мл",
            "шт", "пара", "компл", "уп"
        ])
        layout.addRow("Основная ед.изм:", self.unit_combo)

        self.unit_secondary_combo = QComboBox()
        self.unit_secondary_combo.addItems([
            "", "дм²", "м²", "м", "кг", "г", "л", "мл",
            "шт", "пара", "компл", "уп"
        ])
        layout.addRow("Дополнительная ед.изм:", self.unit_secondary_combo)

        self.conversion_factor_spin = QDoubleSpinBox()
        self.conversion_factor_spin.setRange(0, 99999)
        self.conversion_factor_spin.setDecimals(4)
        layout.addRow("Коэффициент перевода:", self.conversion_factor_spin)

        # Дополнительные свойства
        layout.addRow(QLabel("<b>Дополнительные свойства (JSON):</b>"))
        self.properties_text = QTextEdit()
        self.properties_text.setMaximumHeight(150)
        self.properties_text.setPlaceholderText('{"ключ": "значение"}')
        layout.addRow(self.properties_text)

        self.tabs.addTab(tab, "📏 Характеристики")

    def create_supply_tab(self):
        """Поставка"""
        tab = QWidget()
        layout = QFormLayout(tab)

        # Цена
        self.price_spin = QDoubleSpinBox()
        self.price_spin.setRange(0, 999999)
        self.price_spin.setDecimals(2)
        self.price_spin.setSuffix(" ₽")
        layout.addRow("Цена:", self.price_spin)

        # Валюта
        self.currency_combo = QComboBox()
        self.currency_combo.addItems(["RUB", "USD", "EUR", "CNY"])
        layout.addRow("Валюта:", self.currency_combo)

        # Поставщик
        layout.addRow(QLabel("<b>Информация о поставщике:</b>"))

        self.supplier_name_input = QLineEdit()
        self.supplier_name_input.setPlaceholderText("Название поставщика")
        layout.addRow("Поставщик:", self.supplier_name_input)

        self.supplier_code_input = QLineEdit()
        self.supplier_code_input.setPlaceholderText("Артикул у поставщика")
        layout.addRow("Код поставщика:", self.supplier_code_input)

        # Сроки и условия
        self.lead_time_spin = QSpinBox()
        self.lead_time_spin.setRange(0, 365)
        self.lead_time_spin.setSuffix(" дней")
        layout.addRow("Срок поставки:", self.lead_time_spin)

        self.min_order_qty_spin = QDoubleSpinBox()
        self.min_order_qty_spin.setRange(0, 99999)
        self.min_order_qty_spin.setDecimals(2)
        layout.addRow("Мин. заказ:", self.min_order_qty_spin)

        self.order_multiplicity_spin = QDoubleSpinBox()
        self.order_multiplicity_spin.setRange(0, 9999)
        self.order_multiplicity_spin.setDecimals(2)
        layout.addRow("Кратность заказа:", self.order_multiplicity_spin)

        self.tabs.addTab(tab, "🚚 Поставка")

    def create_stock_tab(self):
        """Складские параметры"""
        tab = QWidget()
        layout = QFormLayout(tab)

        # Нормативы запасов
        self.safety_stock_spin = QDoubleSpinBox()
        self.safety_stock_spin.setRange(0, 99999)
        self.safety_stock_spin.setDecimals(2)
        layout.addRow("Страховой запас:", self.safety_stock_spin)

        self.reorder_point_spin = QDoubleSpinBox()
        self.reorder_point_spin.setRange(0, 99999)
        self.reorder_point_spin.setDecimals(2)
        layout.addRow("Точка заказа:", self.reorder_point_spin)

        self.max_stock_spin = QDoubleSpinBox()
        self.max_stock_spin.setRange(0, 99999)
        self.max_stock_spin.setDecimals(2)
        layout.addRow("Макс. запас:", self.max_stock_spin)

        # Условия хранения
        layout.addRow(QLabel("<b>Условия хранения:</b>"))
        self.storage_conditions_text = QTextEdit()
        self.storage_conditions_text.setMaximumHeight(100)
        self.storage_conditions_text.setPlaceholderText("Температура, влажность, особые условия...")
        layout.addRow(self.storage_conditions_text)

        self.tabs.addTab(tab, "📦 Склад")

    def save_data(self):
        """Сохранение в БД"""
        if not self.validate():
            return

        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            # Собираем данные
            data = {
                'code': self.code_input.text(),
                'name': self.name_input.text(),
                'name_en': self.name_en_input.text() or None,
                'group_type': self.group_combo.currentData(),  # Берем значение, а не текст
                'subgroup': self.subgroup_input.text() or None,
                'material_type': self.material_type_input.text() or None,
                'color': self.color_input.text() or None,
                'texture': self.texture_input.text() or None,
                'thickness': self.thickness_spin.value() if self.thickness_spin.value() > 0 else None,
                'density': self.density_spin.value() if self.density_spin.value() > 0 else None,
                'unit': self.unit_combo.currentText(),
                'unit_secondary': self.unit_secondary_combo.currentText() or None,
                'conversion_factor': self.conversion_factor_spin.value() if self.conversion_factor_spin.value() > 0 else None,
                'price': self.price_spin.value() if self.price_spin.value() > 0 else None,
                'currency': self.currency_combo.currentText(),
                'supplier_name': self.supplier_name_input.text() or None,
                'supplier_code': self.supplier_code_input.text() or None,
                'lead_time_days': self.lead_time_spin.value() if self.lead_time_spin.value() > 0 else None,
                'min_order_qty': self.min_order_qty_spin.value() if self.min_order_qty_spin.value() > 0 else None,
                'order_multiplicity': self.order_multiplicity_spin.value() if self.order_multiplicity_spin.value() > 0 else None,
                'safety_stock': self.safety_stock_spin.value() if self.safety_stock_spin.value() > 0 else None,
                'reorder_point': self.reorder_point_spin.value() if self.reorder_point_spin.value() > 0 else None,
                'max_stock': self.max_stock_spin.value() if self.max_stock_spin.value() > 0 else None,
                'storage_conditions': self.storage_conditions_text.toPlainText() or None,
                'is_active': self.is_active_check.isChecked(),
                'is_critical': self.is_critical_check.isChecked()
            }

            # Дополнительные свойства
            properties_text = self.properties_text.toPlainText()
            if properties_text:
                try:
                    data['properties'] = json.dumps(json.loads(properties_text))
                except:
                    data['properties'] = json.dumps({})
            else:
                data['properties'] = json.dumps({})

            if self.record_id:
                # Обновление
                set_clause = ', '.join([f"{k} = %s" for k in data.keys()])
                query = f"""
                    UPDATE materials
                    SET {set_clause}, updated_at = NOW()
                    WHERE id = %s
                """
                cursor.execute(query, list(data.values()) + [self.record_id])
            else:
                # Вставка с генерацией UUID
                import uuid
                data['uuid'] = str(uuid.uuid4())
                columns = list(data.keys())
                placeholders = ['%s'] * len(columns)
                query = f"""
                    INSERT INTO materials ({', '.join(columns)}, created_at, updated_at)
                    VALUES ({', '.join(placeholders)}, NOW(), NOW())
                """
                cursor.execute(query, list(data.values()))

            conn.commit()
            cursor.close()
            self.db.put_connection(conn)

            QMessageBox.information(self, "Успешно", "Материал сохранен")
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить: {e}")

    def load_data(self, record_id: int):
        """Загрузка данных"""
        self.record_id = record_id

        try:
            conn = self.db.get_connection()
            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cursor.execute("SELECT * FROM materials WHERE id = %s", (record_id,))
            row = cursor.fetchone()
            cursor.close()
            self.db.put_connection(conn)

            if row:
                # Основные данные
                self.code_input.setText(row['code'] or '')
                self.name_input.setText(row['name'] or '')
                self.name_en_input.setText(row['name_en'] or '')
                # Устанавливаем группу по значению из БД
                group_value = row['group_type']
                if group_value:
                    for i in range(self.group_combo.count()):
                        if self.group_combo.itemData(i) == group_value:
                            self.group_combo.setCurrentIndex(i)
                            break
                self.subgroup_input.setText(row['subgroup'] or '')
                self.material_type_input.setText(row['material_type'] or '')
                self.color_input.setText(row['color'] or '')
                self.is_active_check.setChecked(row['is_active'] if row['is_active'] is not None else True)
                self.is_critical_check.setChecked(row['is_critical'] or False)

                # Характеристики
                self.texture_input.setText(row['texture'] or '')
                if row['thickness']:
                    self.thickness_spin.setValue(float(row['thickness']))
                if row['density']:
                    self.density_spin.setValue(float(row['density']))
                self.unit_combo.setCurrentText(row['unit'] or 'шт')
                self.unit_secondary_combo.setCurrentText(row['unit_secondary'] or '')
                if row['conversion_factor']:
                    self.conversion_factor_spin.setValue(float(row['conversion_factor']))

                # Поставка
                if row['price']:
                    self.price_spin.setValue(float(row['price']))
                self.currency_combo.setCurrentText(row['currency'] or 'RUB')
                self.supplier_name_input.setText(row['supplier_name'] or '')
                self.supplier_code_input.setText(row['supplier_code'] or '')
                if row['lead_time_days']:
                    self.lead_time_spin.setValue(row['lead_time_days'])
                if row['min_order_qty']:
                    self.min_order_qty_spin.setValue(float(row['min_order_qty']))
                if row['order_multiplicity']:
                    self.order_multiplicity_spin.setValue(float(row['order_multiplicity']))

                # Склад
                if row['safety_stock']:
                    self.safety_stock_spin.setValue(float(row['safety_stock']))
                if row['reorder_point']:
                    self.reorder_point_spin.setValue(float(row['reorder_point']))
                if row['max_stock']:
                    self.max_stock_spin.setValue(float(row['max_stock']))
                self.storage_conditions_text.setPlainText(row['storage_conditions'] or '')

                # Свойства
                if row['properties']:
                    props = row['properties'] if isinstance(row['properties'], dict) else json.loads(row['properties'])
                    self.properties_text.setPlainText(json.dumps(props, indent=2, ensure_ascii=False))

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить данные: {e}")

    def validate(self) -> bool:
        """Валидация"""
        if not self.code_input.text():
            QMessageBox.warning(self, "Ошибка", "Укажите код материала")
            self.tabs.setCurrentIndex(0)
            self.code_input.setFocus()
            return False

        if not self.name_input.text():
            QMessageBox.warning(self, "Ошибка", "Укажите название материала")
            self.tabs.setCurrentIndex(0)
            self.name_input.setFocus()
            return False

        return True