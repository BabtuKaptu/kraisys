"""Model components management dialog"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QComboBox, QSpinBox, QDoubleSpinBox, QCheckBox,
    QLabel, QLineEdit, QTextEdit, QMessageBox, QHeaderView, QTabWidget,
    QWidget, QGroupBox, QGridLayout
)
from PyQt6.QtCore import Qt
import psycopg2.extras
from database.connection import DatabaseConnection


class ModelComponentsDialog(QDialog):
    """Диалог управления компонентами модели"""

    def __init__(self, model_id: int, model_article: str = "", parent=None):
        super().__init__(parent)
        self.model_id = model_id
        self.model_article = model_article
        self.db = DatabaseConnection()

        # Данные
        self.cutting_parts = []
        self.materials = []
        self.components = []

        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        """Настройка интерфейса"""
        self.setWindowTitle(f"Компоненты модели {self.model_article}")
        self.setModal(True)
        self.resize(1200, 700)

        layout = QVBoxLayout(self)

        # Табы для разных типов компонентов
        self.tabs = QTabWidget()

        # Вкладка деталей кроя
        self.cutting_tab = QWidget()
        self.setup_cutting_tab()
        self.tabs.addTab(self.cutting_tab, "Детали кроя")

        # Вкладка материалов
        self.materials_tab = QWidget()
        self.setup_materials_tab()
        self.tabs.addTab(self.materials_tab, "Материалы и фурнитура")

        # Вкладка дополнительных компонентов
        self.custom_tab = QWidget()
        self.setup_custom_tab()
        self.tabs.addTab(self.custom_tab, "Дополнительные компоненты")

        layout.addWidget(self.tabs)

        # Кнопки
        buttons = QHBoxLayout()
        self.btn_save = QPushButton("💾 Сохранить")
        self.btn_calculate = QPushButton("📊 Рассчитать себестоимость")
        self.btn_close = QPushButton("Закрыть")

        self.btn_save.clicked.connect(self.save_components)
        self.btn_calculate.clicked.connect(self.calculate_costs)
        self.btn_close.clicked.connect(self.close)

        buttons.addWidget(self.btn_save)
        buttons.addWidget(self.btn_calculate)
        buttons.addStretch()
        buttons.addWidget(self.btn_close)

        layout.addLayout(buttons)

    def setup_cutting_tab(self):
        """Настройка вкладки деталей кроя"""
        layout = QVBoxLayout(self.cutting_tab)

        # Панель инструментов
        toolbar = QHBoxLayout()

        self.btn_add_cutting = QPushButton("➕ Добавить деталь")
        self.btn_remove_cutting = QPushButton("➖ Удалить")
        self.btn_add_cutting.clicked.connect(self.add_cutting_part)
        self.btn_remove_cutting.clicked.connect(self.remove_cutting_part)

        toolbar.addWidget(self.btn_add_cutting)
        toolbar.addWidget(self.btn_remove_cutting)
        toolbar.addStretch()

        layout.addLayout(toolbar)

        # Таблица деталей кроя
        self.cutting_table = QTableWidget()
        self.cutting_table.setColumnCount(5)
        self.cutting_table.setHorizontalHeaderLabels([
            "Код", "Название", "Количество", "Единица", "Примечание"
        ])

        header = self.cutting_table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

        layout.addWidget(self.cutting_table)

    def setup_materials_tab(self):
        """Настройка вкладки материалов"""
        layout = QVBoxLayout(self.materials_tab)

        # Панель инструментов
        toolbar = QHBoxLayout()

        self.btn_add_material = QPushButton("➕ Добавить материал")
        self.btn_remove_material = QPushButton("➖ Удалить")
        self.btn_add_material.clicked.connect(self.add_material)
        self.btn_remove_material.clicked.connect(self.remove_material)

        toolbar.addWidget(self.btn_add_material)
        toolbar.addWidget(self.btn_remove_material)
        toolbar.addStretch()

        layout.addLayout(toolbar)

        # Таблица материалов
        self.materials_table = QTableWidget()
        self.materials_table.setColumnCount(6)
        self.materials_table.setHorizontalHeaderLabels([
            "Код", "Название", "Расход %", "Абс. расход", "Единица", "Опционально"
        ])

        header = self.materials_table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

        layout.addWidget(self.materials_table)

    def setup_custom_tab(self):
        """Настройка вкладки дополнительных компонентов"""
        layout = QVBoxLayout(self.custom_tab)

        # Панель инструментов
        toolbar = QHBoxLayout()

        self.btn_add_custom = QPushButton("➕ Добавить компонент")
        self.btn_remove_custom = QPushButton("➖ Удалить")
        self.btn_add_custom.clicked.connect(self.add_custom_component)
        self.btn_remove_custom.clicked.connect(self.remove_custom_component)

        toolbar.addWidget(self.btn_add_custom)
        toolbar.addWidget(self.btn_remove_custom)
        toolbar.addStretch()

        layout.addLayout(toolbar)

        # Таблица кастомных компонентов
        self.custom_table = QTableWidget()
        self.custom_table.setColumnCount(5)
        self.custom_table.setHorizontalHeaderLabels([
            "Название", "Группа", "Расход", "Единица", "Примечание"
        ])

        header = self.custom_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)

        layout.addWidget(self.custom_table)

    def load_data(self):
        """Загрузка данных"""
        self.load_cutting_parts()
        self.load_materials()
        self.load_model_components()

    def load_cutting_parts(self):
        """Загрузка справочника деталей кроя"""
        try:
            conn = self.db.get_connection()
            if not conn:
                return

            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cursor.execute("""
                SELECT id, code, name, category, default_qty, unit, notes
                FROM cutting_parts
                WHERE is_active = true AND is_cutting = true
                ORDER BY code
            """)

            self.cutting_parts = cursor.fetchall()
            cursor.close()
            self.db.put_connection(conn)

        except Exception as e:
            print(f"Error loading cutting parts: {e}")

    def load_materials(self):
        """Загрузка справочника материалов"""
        try:
            conn = self.db.get_connection()
            if not conn:
                return

            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cursor.execute("""
                SELECT id, code, name, material_type, unit, price
                FROM materials
                WHERE is_active = true
                ORDER BY name
            """)

            self.materials = cursor.fetchall()
            cursor.close()
            self.db.put_connection(conn)

        except Exception as e:
            print(f"Error loading materials: {e}")

    def load_model_components(self):
        """Загрузка компонентов модели"""
        try:
            conn = self.db.get_connection()
            if not conn:
                return

            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cursor.execute("""
                SELECT id, component_name, component_group,
                       consumption_percent, absolute_consumption,
                       unit, is_optional, notes
                FROM model_components
                WHERE model_id = %s
                ORDER BY sort_order, component_name
            """, (self.model_id,))

            components = cursor.fetchall()
            cursor.close()
            self.db.put_connection(conn)

            # Распределяем компоненты по таблицам
            for comp in components:
                if comp['component_group'] == 'cutting':
                    self.add_cutting_to_table(comp)
                elif comp['component_group'] == 'material':
                    self.add_material_to_table(comp)
                else:
                    self.add_custom_to_table(comp)

        except Exception as e:
            print(f"Error loading model components: {e}")

    def add_cutting_to_table(self, component):
        """Добавить деталь кроя в таблицу"""
        row = self.cutting_table.rowCount()
        self.cutting_table.insertRow(row)

        # Находим деталь в справочнике
        part_info = None
        for part in self.cutting_parts:
            if part['name'] == component['component_name']:
                part_info = part
                break

        self.cutting_table.setItem(row, 0, QTableWidgetItem(
            part_info['code'] if part_info else ""
        ))
        self.cutting_table.setItem(row, 1, QTableWidgetItem(
            component['component_name']
        ))

        # Количество
        qty_spin = QSpinBox()
        qty_spin.setMinimum(1)
        qty_spin.setMaximum(100)
        qty_spin.setValue(int(component['absolute_consumption'] or 1))
        self.cutting_table.setCellWidget(row, 2, qty_spin)

        self.cutting_table.setItem(row, 3, QTableWidgetItem(
            component['unit'] or "шт"
        ))
        self.cutting_table.setItem(row, 4, QTableWidgetItem(
            component['notes'] or ""
        ))

    def add_material_to_table(self, component):
        """Добавить материал в таблицу"""
        row = self.materials_table.rowCount()
        self.materials_table.insertRow(row)

        # Находим материал в справочнике
        mat_info = None
        for mat in self.materials:
            if mat['name'] == component['component_name']:
                mat_info = mat
                break

        self.materials_table.setItem(row, 0, QTableWidgetItem(
            mat_info['code'] if mat_info else ""
        ))
        self.materials_table.setItem(row, 1, QTableWidgetItem(
            component['component_name']
        ))

        # Процентный расход
        percent_spin = QDoubleSpinBox()
        percent_spin.setMinimum(0)
        percent_spin.setMaximum(200)
        percent_spin.setSuffix(" %")
        percent_spin.setValue(float(component['consumption_percent'] or 0))
        self.materials_table.setCellWidget(row, 2, percent_spin)

        # Абсолютный расход
        abs_spin = QDoubleSpinBox()
        abs_spin.setMinimum(0)
        abs_spin.setMaximum(1000)
        abs_spin.setDecimals(3)
        abs_spin.setValue(float(component['absolute_consumption'] or 0))
        self.materials_table.setCellWidget(row, 3, abs_spin)

        self.materials_table.setItem(row, 4, QTableWidgetItem(
            component['unit'] or ""
        ))

        # Опционально
        optional_check = QCheckBox()
        optional_check.setChecked(component['is_optional'] or False)
        self.materials_table.setCellWidget(row, 5, optional_check)

    def add_custom_to_table(self, component):
        """Добавить кастомный компонент в таблицу"""
        row = self.custom_table.rowCount()
        self.custom_table.insertRow(row)

        self.custom_table.setItem(row, 0, QTableWidgetItem(
            component['component_name']
        ))
        self.custom_table.setItem(row, 1, QTableWidgetItem(
            component['component_group'] or "other"
        ))

        # Расход
        consumption_spin = QDoubleSpinBox()
        consumption_spin.setMinimum(0)
        consumption_spin.setMaximum(1000)
        consumption_spin.setDecimals(3)
        consumption_spin.setValue(
            float(component['absolute_consumption'] or 0)
        )
        self.custom_table.setCellWidget(row, 2, consumption_spin)

        self.custom_table.setItem(row, 3, QTableWidgetItem(
            component['unit'] or ""
        ))
        self.custom_table.setItem(row, 4, QTableWidgetItem(
            component['notes'] or ""
        ))

    def add_cutting_part(self):
        """Добавить деталь кроя"""
        dialog = CuttingPartSelectionDialog(self.cutting_parts, self)
        if dialog.exec():
            selected = dialog.get_selected()
            if selected:
                row = self.cutting_table.rowCount()
                self.cutting_table.insertRow(row)

                self.cutting_table.setItem(row, 0, QTableWidgetItem(selected['code']))
                self.cutting_table.setItem(row, 1, QTableWidgetItem(selected['name']))

                qty_spin = QSpinBox()
                qty_spin.setMinimum(1)
                qty_spin.setMaximum(100)
                qty_spin.setValue(selected['default_qty'] or 1)
                self.cutting_table.setCellWidget(row, 2, qty_spin)

                self.cutting_table.setItem(row, 3, QTableWidgetItem(selected['unit'] or "шт"))
                self.cutting_table.setItem(row, 4, QTableWidgetItem(selected['notes'] or ""))

    def remove_cutting_part(self):
        """Удалить деталь кроя"""
        row = self.cutting_table.currentRow()
        if row >= 0:
            self.cutting_table.removeRow(row)

    def add_material(self):
        """Добавить материал"""
        dialog = MaterialSelectionDialog(self.materials, self)
        if dialog.exec():
            selected = dialog.get_selected()
            if selected:
                row = self.materials_table.rowCount()
                self.materials_table.insertRow(row)

                self.materials_table.setItem(row, 0, QTableWidgetItem(selected['code']))
                self.materials_table.setItem(row, 1, QTableWidgetItem(selected['name']))

                percent_spin = QDoubleSpinBox()
                percent_spin.setMinimum(0)
                percent_spin.setMaximum(200)
                percent_spin.setSuffix(" %")
                self.materials_table.setCellWidget(row, 2, percent_spin)

                abs_spin = QDoubleSpinBox()
                abs_spin.setMinimum(0)
                abs_spin.setMaximum(1000)
                abs_spin.setDecimals(3)
                self.materials_table.setCellWidget(row, 3, abs_spin)

                self.materials_table.setItem(row, 4, QTableWidgetItem(selected['unit'] or ""))

                optional_check = QCheckBox()
                self.materials_table.setCellWidget(row, 5, optional_check)

    def remove_material(self):
        """Удалить материал"""
        row = self.materials_table.currentRow()
        if row >= 0:
            self.materials_table.removeRow(row)

    def add_custom_component(self):
        """Добавить кастомный компонент"""
        row = self.custom_table.rowCount()
        self.custom_table.insertRow(row)

        self.custom_table.setItem(row, 0, QTableWidgetItem(""))
        self.custom_table.setItem(row, 1, QTableWidgetItem("other"))

        consumption_spin = QDoubleSpinBox()
        consumption_spin.setMinimum(0)
        consumption_spin.setMaximum(1000)
        consumption_spin.setDecimals(3)
        self.custom_table.setCellWidget(row, 2, consumption_spin)

        self.custom_table.setItem(row, 3, QTableWidgetItem(""))
        self.custom_table.setItem(row, 4, QTableWidgetItem(""))

    def remove_custom_component(self):
        """Удалить кастомный компонент"""
        row = self.custom_table.currentRow()
        if row >= 0:
            self.custom_table.removeRow(row)

    def save_components(self):
        """Сохранить компоненты"""
        try:
            conn = self.db.get_connection()
            if not conn:
                return

            cursor = conn.cursor()

            # Удаляем старые компоненты
            cursor.execute("DELETE FROM model_components WHERE model_id = %s", (self.model_id,))

            sort_order = 0

            # Сохраняем детали кроя
            for row in range(self.cutting_table.rowCount()):
                name = self.cutting_table.item(row, 1).text()
                qty_widget = self.cutting_table.cellWidget(row, 2)
                qty = qty_widget.value() if qty_widget else 1
                unit = self.cutting_table.item(row, 3).text()
                notes = self.cutting_table.item(row, 4).text()

                cursor.execute("""
                    INSERT INTO model_components
                    (model_id, component_name, component_group, absolute_consumption,
                     unit, notes, sort_order)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (self.model_id, name, 'cutting', qty, unit, notes, sort_order))
                sort_order += 1

            # Сохраняем материалы
            for row in range(self.materials_table.rowCount()):
                name = self.materials_table.item(row, 1).text()
                percent_widget = self.materials_table.cellWidget(row, 2)
                percent = percent_widget.value() if percent_widget else 0
                abs_widget = self.materials_table.cellWidget(row, 3)
                abs_val = abs_widget.value() if abs_widget else 0
                unit = self.materials_table.item(row, 4).text()
                optional_widget = self.materials_table.cellWidget(row, 5)
                is_optional = optional_widget.isChecked() if optional_widget else False

                cursor.execute("""
                    INSERT INTO model_components
                    (model_id, component_name, component_group, consumption_percent,
                     absolute_consumption, unit, is_optional, sort_order)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (self.model_id, name, 'material', percent, abs_val, unit,
                      is_optional, sort_order))
                sort_order += 1

            # Сохраняем кастомные компоненты
            for row in range(self.custom_table.rowCount()):
                name = self.custom_table.item(row, 0).text()
                group = self.custom_table.item(row, 1).text()
                consumption_widget = self.custom_table.cellWidget(row, 2)
                consumption = consumption_widget.value() if consumption_widget else 0
                unit = self.custom_table.item(row, 3).text()
                notes = self.custom_table.item(row, 4).text()

                cursor.execute("""
                    INSERT INTO model_components
                    (model_id, component_name, component_group, absolute_consumption,
                     unit, notes, sort_order)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (self.model_id, name, group, consumption, unit, notes, sort_order))
                sort_order += 1

            conn.commit()
            cursor.close()
            self.db.put_connection(conn)

            QMessageBox.information(self, "Успешно", "Компоненты сохранены")

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить: {e}")

    def calculate_costs(self):
        """Рассчитать себестоимость"""
        total_material_cost = 0
        details = []

        try:
            conn = self.db.get_connection()
            if not conn:
                return

            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

            # Расчет стоимости материалов
            for row in range(self.materials_table.rowCount()):
                name = self.materials_table.item(row, 1).text()
                abs_widget = self.materials_table.cellWidget(row, 3)
                consumption = abs_widget.value() if abs_widget else 0

                # Получаем цену материала
                cursor.execute("""
                    SELECT price FROM materials
                    WHERE name = %s AND is_active = true
                """, (name,))
                result = cursor.fetchone()

                if result and result['price']:
                    cost = float(result['price']) * consumption
                    total_material_cost += cost
                    details.append(f"{name}: {consumption:.3f} x {result['price']:.2f} = {cost:.2f}")

            cursor.close()
            self.db.put_connection(conn)

            # Показываем результат
            msg = f"Себестоимость материалов: {total_material_cost:.2f} руб.\n\n"
            msg += "Детализация:\n" + "\n".join(details)

            QMessageBox.information(self, "Расчет себестоимости", msg)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось рассчитать: {e}")


class CuttingPartSelectionDialog(QDialog):
    """Диалог выбора детали кроя"""

    def __init__(self, cutting_parts, parent=None):
        super().__init__(parent)
        self.cutting_parts = cutting_parts
        self.selected = None
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Выбор детали кроя")
        self.setModal(True)
        self.resize(600, 400)

        layout = QVBoxLayout(self)

        # Поиск
        self.search = QLineEdit()
        self.search.setPlaceholderText("Поиск по коду или названию...")
        self.search.textChanged.connect(self.filter_parts)
        layout.addWidget(self.search)

        # Таблица
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Код", "Название", "Категория", "Кол-во"])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.doubleClicked.connect(self.accept)

        self.populate_table()
        layout.addWidget(self.table)

        # Кнопки
        buttons = QHBoxLayout()
        self.btn_ok = QPushButton("Выбрать")
        self.btn_cancel = QPushButton("Отмена")

        self.btn_ok.clicked.connect(self.accept)
        self.btn_cancel.clicked.connect(self.reject)

        buttons.addWidget(self.btn_ok)
        buttons.addWidget(self.btn_cancel)
        layout.addLayout(buttons)

    def populate_table(self):
        self.table.setRowCount(len(self.cutting_parts))
        for row, part in enumerate(self.cutting_parts):
            self.table.setItem(row, 0, QTableWidgetItem(part['code'] or ""))
            self.table.setItem(row, 1, QTableWidgetItem(part['name'] or ""))
            self.table.setItem(row, 2, QTableWidgetItem(part['category'] or ""))
            self.table.setItem(row, 3, QTableWidgetItem(str(part['default_qty'] or 1)))

    def filter_parts(self, text):
        for row in range(self.table.rowCount()):
            match = False
            for col in range(2):  # Поиск по коду и названию
                item = self.table.item(row, col)
                if item and text.lower() in item.text().lower():
                    match = True
                    break
            self.table.setRowHidden(row, not match)

    def accept(self):
        row = self.table.currentRow()
        if row >= 0:
            self.selected = self.cutting_parts[row]
        super().accept()

    def get_selected(self):
        return self.selected


class MaterialSelectionDialog(QDialog):
    """Диалог выбора материала"""

    def __init__(self, materials, parent=None):
        super().__init__(parent)
        self.materials = materials
        self.selected = None
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("Выбор материала")
        self.setModal(True)
        self.resize(700, 400)

        layout = QVBoxLayout(self)

        # Поиск
        self.search = QLineEdit()
        self.search.setPlaceholderText("Поиск по коду или названию...")
        self.search.textChanged.connect(self.filter_materials)
        layout.addWidget(self.search)

        # Таблица
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Код", "Название", "Тип", "Единица", "Цена"])
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.doubleClicked.connect(self.accept)

        self.populate_table()
        layout.addWidget(self.table)

        # Кнопки
        buttons = QHBoxLayout()
        self.btn_ok = QPushButton("Выбрать")
        self.btn_cancel = QPushButton("Отмена")

        self.btn_ok.clicked.connect(self.accept)
        self.btn_cancel.clicked.connect(self.reject)

        buttons.addWidget(self.btn_ok)
        buttons.addWidget(self.btn_cancel)
        layout.addLayout(buttons)

    def populate_table(self):
        self.table.setRowCount(len(self.materials))
        for row, mat in enumerate(self.materials):
            self.table.setItem(row, 0, QTableWidgetItem(mat['code'] or ""))
            self.table.setItem(row, 1, QTableWidgetItem(mat['name'] or ""))
            self.table.setItem(row, 2, QTableWidgetItem(mat['material_type'] or ""))
            self.table.setItem(row, 3, QTableWidgetItem(mat['unit'] or ""))
            price = f"{mat['price']:.2f}" if mat['price'] else ""
            self.table.setItem(row, 4, QTableWidgetItem(price))

    def filter_materials(self, text):
        for row in range(self.table.rowCount()):
            match = False
            for col in range(2):  # Поиск по коду и названию
                item = self.table.item(row, col)
                if item and text.lower() in item.text().lower():
                    match = True
                    break
            self.table.setRowHidden(row, not match)

    def accept(self):
        row = self.table.currentRow()
        if row >= 0:
            self.selected = self.materials[row]
        super().accept()

    def get_selected(self):
        return self.selected