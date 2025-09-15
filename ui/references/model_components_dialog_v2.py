"""Model components management dialog v2 - with proper cutting parts logic"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QComboBox, QSpinBox, QDoubleSpinBox, QCheckBox,
    QLabel, QLineEdit, QTextEdit, QMessageBox, QHeaderView, QTabWidget,
    QWidget, QGroupBox, QGridLayout, QTreeWidget, QTreeWidgetItem,
    QSplitter
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
import psycopg2.extras
from database.connection import DatabaseConnection


class ModelComponentsDialogV2(QDialog):
    """Улучшенный диалог управления компонентами модели"""

    def __init__(self, model_id: int, model_article: str = "", parent=None):
        super().__init__(parent)
        self.model_id = model_id
        self.model_article = model_article
        self.db = DatabaseConnection()

        # Данные
        self.cutting_parts_dict = {}  # Справочник деталей кроя
        self.materials_dict = {}      # Справочник материалов

        self.setup_ui()
        self.load_reference_data()
        self.load_model_components()
        self.calculate_totals()

    def setup_ui(self):
        """Настройка интерфейса"""
        self.setWindowTitle(f"Компоненты модели {self.model_article}")
        self.setModal(True)
        self.resize(1400, 800)

        layout = QVBoxLayout(self)

        # Заголовок с общей информацией
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel(f"<b>Модель: {self.model_article}</b>"))
        header_layout.addStretch()

        # Общий расход кожи
        self.total_leather_label = QLabel("Общий расход кожи: 0.0 дм²")
        self.total_leather_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #2b6cb0;")
        header_layout.addWidget(self.total_leather_label)

        layout.addLayout(header_layout)

        # Табы для разных типов компонентов
        self.tabs = QTabWidget()

        # Вкладка деталей кроя - САМАЯ ВАЖНАЯ
        self.cutting_tab = QWidget()
        self.setup_cutting_tab()
        self.tabs.addTab(self.cutting_tab, "✂️ Детали кроя")

        # Вкладка материалов
        self.materials_tab = QWidget()
        self.setup_materials_tab()
        self.tabs.addTab(self.materials_tab, "🧵 Материалы и фурнитура")

        layout.addWidget(self.tabs)

        # Кнопки
        buttons = QHBoxLayout()
        self.btn_save = QPushButton("💾 Сохранить")
        self.btn_calculate = QPushButton("📊 Пересчитать")
        self.btn_close = QPushButton("Закрыть")

        self.btn_save.clicked.connect(self.save_components)
        self.btn_calculate.clicked.connect(self.calculate_totals)
        self.btn_close.clicked.connect(self.close)

        buttons.addWidget(self.btn_save)
        buttons.addWidget(self.btn_calculate)
        buttons.addStretch()
        buttons.addWidget(self.btn_close)

        layout.addLayout(buttons)

    def setup_cutting_tab(self):
        """Настройка вкладки деталей кроя"""
        layout = QVBoxLayout(self.cutting_tab)

        # Информационная панель
        info_label = QLabel(
            "💡 <b>Детали кроя</b> - элементы верха обуви, выкраиваемые из кожи.\n"
            "Для каждой детали укажите количество (обычно 2 для парной обуви) и расход материала в дм²."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("background: #f0f8ff; padding: 10px; border-radius: 5px;")
        layout.addWidget(info_label)

        # Разделитель для выбора детали и таблицы
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Левая панель - выбор деталей из справочника
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        left_layout.addWidget(QLabel("<b>Справочник деталей кроя:</b>"))

        # Поиск
        self.cutting_search = QLineEdit()
        self.cutting_search.setPlaceholderText("🔍 Поиск детали...")
        self.cutting_search.textChanged.connect(self.filter_cutting_parts)
        left_layout.addWidget(self.cutting_search)

        # Дерево деталей кроя по категориям
        self.cutting_tree = QTreeWidget()
        self.cutting_tree.setHeaderLabel("Детали кроя")
        self.cutting_tree.itemDoubleClicked.connect(self.add_cutting_from_tree)
        left_layout.addWidget(self.cutting_tree)

        splitter.addWidget(left_panel)

        # Правая панель - таблица выбранных деталей
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        # Панель инструментов
        toolbar = QHBoxLayout()
        self.btn_remove_cutting = QPushButton("➖ Удалить выбранное")
        self.btn_clear_cutting = QPushButton("🗑 Очистить все")
        self.btn_remove_cutting.clicked.connect(self.remove_cutting_part)
        self.btn_clear_cutting.clicked.connect(self.clear_cutting_parts)

        toolbar.addWidget(self.btn_remove_cutting)
        toolbar.addWidget(self.btn_clear_cutting)
        toolbar.addStretch()
        right_layout.addLayout(toolbar)

        # Таблица деталей кроя модели
        self.cutting_table = QTableWidget()
        self.cutting_table.setColumnCount(6)
        self.cutting_table.setHorizontalHeaderLabels([
            "Код", "Название", "Кол-во (шт)", "Расход кожи (дм²)", "Примечание", "ID"
        ])

        # Настройка ширины колонок
        header = self.cutting_table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self.cutting_table.setColumnHidden(5, True)  # Скрываем ID

        # Подключаем сигнал изменения для автоматического пересчета
        self.cutting_table.cellChanged.connect(self.on_cutting_cell_changed)

        right_layout.addWidget(self.cutting_table)

        # Итоговая информация
        self.cutting_total_label = QLabel("Итого деталей: 0 | Общий расход кожи: 0.0 дм²")
        self.cutting_total_label.setStyleSheet("font-weight: bold; padding: 5px;")
        right_layout.addWidget(self.cutting_total_label)

        splitter.addWidget(right_panel)
        splitter.setSizes([400, 800])

        layout.addWidget(splitter)

    def setup_materials_tab(self):
        """Настройка вкладки материалов"""
        layout = QVBoxLayout(self.materials_tab)

        # Информация
        info_label = QLabel(
            "💡 <b>Материалы и фурнитура</b> - дополнительные материалы для производства.\n"
            "Укажите процентный или абсолютный расход."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("background: #f0f8ff; padding: 10px; border-radius: 5px;")
        layout.addWidget(info_label)

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

    def load_reference_data(self):
        """Загрузка справочников"""
        try:
            conn = self.db.get_connection()
            if not conn:
                return

            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

            # Загружаем детали кроя
            cursor.execute("""
                SELECT id, code, name, category, default_qty, unit, notes
                FROM cutting_parts
                WHERE is_active = true AND is_cutting = true
                ORDER BY category, name
            """)

            # Группируем по категориям
            categories = {}
            for part in cursor.fetchall():
                cat = part['category'] or 'OTHER'
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append(part)
                self.cutting_parts_dict[part['id']] = part

            # Заполняем дерево деталей кроя
            self.cutting_tree.clear()
            for category, parts in sorted(categories.items()):
                cat_item = QTreeWidgetItem(self.cutting_tree, [category])
                cat_item.setExpanded(False)
                font = QFont()
                font.setBold(True)
                cat_item.setFont(0, font)

                for part in parts:
                    part_item = QTreeWidgetItem(cat_item)
                    part_item.setText(0, f"{part['code']} - {part['name']}")
                    part_item.setData(0, Qt.ItemDataRole.UserRole, part)
                    if part['notes']:
                        part_item.setToolTip(0, part['notes'])

            # Загружаем материалы
            cursor.execute("""
                SELECT id, code, name, material_type, unit, price
                FROM materials
                WHERE is_active = true
                ORDER BY name
            """)

            for mat in cursor.fetchall():
                self.materials_dict[mat['id']] = mat

            cursor.close()
            self.db.put_connection(conn)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить справочники: {e}")

    def load_model_components(self):
        """Загрузка компонентов модели"""
        if not self.model_id:
            return

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
                    self.add_cutting_to_table_from_db(comp)
                elif comp['component_group'] == 'material':
                    self.add_material_to_table_from_db(comp)

        except Exception as e:
            print(f"Error loading model components: {e}")

    def add_cutting_to_table_from_db(self, component):
        """Добавить деталь кроя из БД в таблицу"""
        row = self.cutting_table.rowCount()
        self.cutting_table.insertRow(row)

        # Находим деталь в справочнике
        part_info = None
        for part_id, part in self.cutting_parts_dict.items():
            if part['name'] == component['component_name']:
                part_info = part
                break

        # Код
        self.cutting_table.setItem(row, 0, QTableWidgetItem(
            part_info['code'] if part_info else ""
        ))

        # Название
        self.cutting_table.setItem(row, 1, QTableWidgetItem(
            component['component_name']
        ))

        # Количество штук
        qty_spin = QSpinBox()
        qty_spin.setMinimum(1)
        qty_spin.setMaximum(100)
        # Если в БД сохранено количество штук < 10, используем его, иначе берем default
        if component['absolute_consumption'] and component['absolute_consumption'] < 10:
            qty_spin.setValue(int(component['absolute_consumption']))
        else:
            qty_spin.setValue(part_info['default_qty'] if part_info else 2)
        qty_spin.valueChanged.connect(self.calculate_totals)
        self.cutting_table.setCellWidget(row, 2, qty_spin)

        # РАСХОД КОЖИ - самое важное поле!
        consumption_spin = QDoubleSpinBox()
        consumption_spin.setMinimum(0)
        consumption_spin.setMaximum(999)
        consumption_spin.setDecimals(2)
        consumption_spin.setSuffix(" дм²")
        # Если расход больше 10, значит это старые данные где сохранен расход
        if component['absolute_consumption'] and component['absolute_consumption'] >= 10:
            consumption_spin.setValue(float(component['absolute_consumption']))
        consumption_spin.valueChanged.connect(self.calculate_totals)
        self.cutting_table.setCellWidget(row, 3, consumption_spin)

        # Примечание
        self.cutting_table.setItem(row, 4, QTableWidgetItem(
            component['notes'] or ""
        ))

        # ID компонента (скрытое)
        self.cutting_table.setItem(row, 5, QTableWidgetItem(
            str(component['id']) if component.get('id') else ""
        ))

    def add_material_to_table_from_db(self, component):
        """Добавить материал из БД в таблицу"""
        row = self.materials_table.rowCount()
        self.materials_table.insertRow(row)

        # Находим материал в справочнике
        mat_info = None
        for mat_id, mat in self.materials_dict.items():
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

    def filter_cutting_parts(self, text):
        """Фильтрация деталей кроя"""
        text = text.lower()
        for i in range(self.cutting_tree.topLevelItemCount()):
            category_item = self.cutting_tree.topLevelItem(i)
            category_visible = False

            for j in range(category_item.childCount()):
                part_item = category_item.child(j)
                part_text = part_item.text(0).lower()

                if text in part_text:
                    part_item.setHidden(False)
                    category_visible = True
                else:
                    part_item.setHidden(True)

            # Раскрываем категорию если есть совпадения
            if category_visible and text:
                category_item.setExpanded(True)

    def add_cutting_from_tree(self, item, column):
        """Добавить деталь кроя из дерева"""
        if item.parent() is None:  # Это категория, а не деталь
            return

        part_data = item.data(0, Qt.ItemDataRole.UserRole)
        if not part_data:
            return

        # Проверяем, нет ли уже такой детали
        for row in range(self.cutting_table.rowCount()):
            if self.cutting_table.item(row, 0).text() == part_data['code']:
                QMessageBox.warning(self, "Внимание",
                                  f"Деталь {part_data['name']} уже добавлена")
                return

        # Добавляем в таблицу
        row = self.cutting_table.rowCount()
        self.cutting_table.insertRow(row)

        # Код
        self.cutting_table.setItem(row, 0, QTableWidgetItem(part_data['code']))

        # Название
        self.cutting_table.setItem(row, 1, QTableWidgetItem(part_data['name']))

        # Количество (по умолчанию)
        qty_spin = QSpinBox()
        qty_spin.setMinimum(1)
        qty_spin.setMaximum(100)
        qty_spin.setValue(part_data['default_qty'] or 2)
        qty_spin.valueChanged.connect(self.calculate_totals)
        self.cutting_table.setCellWidget(row, 2, qty_spin)

        # РАСХОД КОЖИ - пустое, нужно заполнить!
        consumption_spin = QDoubleSpinBox()
        consumption_spin.setMinimum(0)
        consumption_spin.setMaximum(999)
        consumption_spin.setDecimals(2)
        consumption_spin.setSuffix(" дм²")
        consumption_spin.setStyleSheet("background-color: #ffffcc;")  # Подсветка
        consumption_spin.valueChanged.connect(self.calculate_totals)
        self.cutting_table.setCellWidget(row, 3, consumption_spin)

        # Примечание
        self.cutting_table.setItem(row, 4, QTableWidgetItem(part_data['notes'] or ""))

        # ID (пустое для новой детали)
        self.cutting_table.setItem(row, 5, QTableWidgetItem(""))

        self.calculate_totals()

    def remove_cutting_part(self):
        """Удалить деталь кроя"""
        row = self.cutting_table.currentRow()
        if row >= 0:
            self.cutting_table.removeRow(row)
            self.calculate_totals()

    def clear_cutting_parts(self):
        """Очистить все детали кроя"""
        if self.cutting_table.rowCount() > 0:
            reply = QMessageBox.question(self, "Подтверждение",
                                        "Удалить все детали кроя?",
                                        QMessageBox.StandardButton.Yes |
                                        QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.cutting_table.setRowCount(0)
                self.calculate_totals()

    def on_cutting_cell_changed(self, row, column):
        """Обработка изменения ячейки таблицы"""
        # Автоматический пересчет при изменении
        self.calculate_totals()

    def add_material(self):
        """Добавить материал"""
        dialog = MaterialSelectionDialog(self.materials_dict, self)
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

    def calculate_totals(self):
        """Расчет итогов"""
        total_leather = 0.0
        total_parts = 0

        # Считаем расход кожи по деталям кроя
        for row in range(self.cutting_table.rowCount()):
            consumption_widget = self.cutting_table.cellWidget(row, 3)
            if consumption_widget:
                total_leather += consumption_widget.value()
                total_parts += 1

        # Обновляем метки
        self.cutting_total_label.setText(
            f"Итого деталей: {total_parts} | Общий расход кожи: {total_leather:.2f} дм²"
        )
        self.total_leather_label.setText(f"Общий расход кожи: {total_leather:.2f} дм²")

        # Подсветка если расход не указан
        for row in range(self.cutting_table.rowCount()):
            consumption_widget = self.cutting_table.cellWidget(row, 3)
            if consumption_widget and consumption_widget.value() == 0:
                consumption_widget.setStyleSheet("background-color: #ffcccc;")
            elif consumption_widget:
                consumption_widget.setStyleSheet("")

    def save_components(self):
        """Сохранение компонентов"""
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
                code = self.cutting_table.item(row, 0).text()
                name = self.cutting_table.item(row, 1).text()
                qty_widget = self.cutting_table.cellWidget(row, 2)
                consumption_widget = self.cutting_table.cellWidget(row, 3)
                notes = self.cutting_table.item(row, 4).text()

                if not consumption_widget or consumption_widget.value() == 0:
                    QMessageBox.warning(self, "Внимание",
                                      f"Не указан расход кожи для детали '{name}'")
                    continue

                # ВАЖНО: сохраняем РАСХОД КОЖИ в absolute_consumption!
                cursor.execute("""
                    INSERT INTO model_components
                    (model_id, component_name, component_group,
                     absolute_consumption, unit, notes, sort_order)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (self.model_id, name, 'cutting',
                      consumption_widget.value(), 'дм²',
                      notes or f"Кол-во: {qty_widget.value() if qty_widget else 2} шт",
                      sort_order))
                sort_order += 1

            # Сохраняем материалы
            for row in range(self.materials_table.rowCount()):
                name = self.materials_table.item(row, 1).text()
                percent_widget = self.materials_table.cellWidget(row, 2)
                abs_widget = self.materials_table.cellWidget(row, 3)
                unit = self.materials_table.item(row, 4).text()
                optional_widget = self.materials_table.cellWidget(row, 5)

                cursor.execute("""
                    INSERT INTO model_components
                    (model_id, component_name, component_group, consumption_percent,
                     absolute_consumption, unit, is_optional, sort_order)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (self.model_id, name, 'material',
                      percent_widget.value() if percent_widget else 0,
                      abs_widget.value() if abs_widget else 0,
                      unit, optional_widget.isChecked() if optional_widget else False,
                      sort_order))
                sort_order += 1

            # Обновляем общий расход кожи в модели
            total_leather = 0.0
            for row in range(self.cutting_table.rowCount()):
                consumption_widget = self.cutting_table.cellWidget(row, 3)
                if consumption_widget:
                    total_leather += consumption_widget.value()

            cursor.execute("""
                UPDATE models
                SET base_leather_norm = %s,
                    updated_at = NOW()
                WHERE id = %s
            """, (total_leather, self.model_id))

            conn.commit()
            cursor.close()
            self.db.put_connection(conn)

            QMessageBox.information(self, "Успешно",
                                  f"Компоненты сохранены\nОбщий расход кожи: {total_leather:.2f} дм²")

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


class MaterialSelectionDialog(QDialog):
    """Диалог выбора материала"""

    def __init__(self, materials_dict, parent=None):
        super().__init__(parent)
        self.materials_dict = materials_dict
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
        materials_list = list(self.materials_dict.values())
        self.table.setRowCount(len(materials_list))

        for row, mat in enumerate(materials_list):
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
            materials_list = list(self.materials_dict.values())
            self.selected = materials_list[row]
        super().accept()

    def get_selected(self):
        return self.selected