"""Warehouse stock management view"""
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt, QDate, pyqtSignal
from PyQt6.QtGui import QDoubleValidator
from database.connection import DatabaseConnection
import psycopg2.extras
from datetime import datetime, date
import random


class WarehouseWidget(QWidget):
    """Виджет складского учета с партиями"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = DatabaseConnection()
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Заголовок
        header = QHBoxLayout()
        title = QLabel("📦 Складской учет")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        header.addWidget(title)
        header.addStretch()

        # Кнопки действий
        self.btn_receipt = QPushButton("📥 Приход")
        self.btn_issue = QPushButton("📤 Расход")
        self.btn_inventory = QPushButton("📊 Инвентаризация")
        self.btn_report = QPushButton("📑 Отчет")

        self.btn_receipt.clicked.connect(self.open_receipt_dialog)
        self.btn_issue.clicked.connect(self.open_issue_dialog)
        self.btn_inventory.clicked.connect(self.open_inventory_dialog)
        self.btn_report.clicked.connect(self.generate_report)

        header.addWidget(self.btn_receipt)
        header.addWidget(self.btn_issue)
        header.addWidget(self.btn_inventory)
        header.addWidget(self.btn_report)

        layout.addLayout(header)

        # Фильтры
        filter_layout = QHBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Поиск по коду или названию...")
        self.search_input.textChanged.connect(self.filter_data)

        self.warehouse_combo = QComboBox()
        self.warehouse_combo.addItems(["Все склады", "Основной", "Производство", "Готовая продукция"])
        self.warehouse_combo.currentTextChanged.connect(self.filter_data)

        filter_layout.addWidget(self.search_input)
        filter_layout.addWidget(self.warehouse_combo)
        filter_layout.addStretch()

        layout.addLayout(filter_layout)

        # Основная таблица
        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            "Код", "Материал", "Партия", "Количество", "Резерв",
            "Ед.изм", "Цена закупки", "Дата прихода", "Склад", "Место"
        ])

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.doubleClicked.connect(self.view_batch_details)

        layout.addWidget(self.table)

        # Статистика
        stats_layout = QHBoxLayout()
        self.stats_label = QLabel("Позиций: 0 | Общая стоимость: 0 ₽")
        stats_layout.addWidget(self.stats_label)
        stats_layout.addStretch()
        layout.addLayout(stats_layout)

    def load_data(self):
        """Загрузка данных склада"""
        try:
            conn = self.db.get_connection()
            if not conn:
                return

            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cursor.execute("""
                SELECT
                    ws.*,
                    m.code as material_code,
                    m.name as material_name
                FROM warehouse_stock ws
                LEFT JOIN materials m ON ws.material_id = m.id
                ORDER BY ws.receipt_date DESC
            """)

            stocks = cursor.fetchall()
            cursor.close()
            self.db.put_connection(conn)

            self.update_table(stocks)

        except Exception as e:
            print(f"Error loading warehouse data: {e}")

    def update_table(self, stocks):
        """Обновление таблицы"""
        self.table.setRowCount(len(stocks))

        total_value = 0
        for row, stock in enumerate(stocks):
            self.table.setItem(row, 0, QTableWidgetItem(stock['material_code'] or ""))
            self.table.setItem(row, 1, QTableWidgetItem(stock['material_name'] or ""))
            self.table.setItem(row, 2, QTableWidgetItem(stock['batch_number'] or ""))

            qty = float(stock['quantity'] or 0)
            self.table.setItem(row, 3, QTableWidgetItem(f"{qty:.2f}"))

            reserved = float(stock['reserved_qty'] or 0)
            self.table.setItem(row, 4, QTableWidgetItem(f"{reserved:.2f}"))

            self.table.setItem(row, 5, QTableWidgetItem(stock['unit'] or ""))

            price = float(stock['purchase_price'] or 0)
            self.table.setItem(row, 6, QTableWidgetItem(f"{price:.2f} ₽"))
            total_value += qty * price

            if stock['receipt_date']:
                self.table.setItem(row, 7, QTableWidgetItem(str(stock['receipt_date'])))

            self.table.setItem(row, 8, QTableWidgetItem(stock['warehouse_code'] or "Основной"))
            self.table.setItem(row, 9, QTableWidgetItem(stock['location'] or ""))

        self.stats_label.setText(f"Позиций: {len(stocks)} | Общая стоимость: {total_value:,.2f} ₽")

    def filter_data(self):
        """Фильтрация данных"""
        search_text = self.search_input.text().lower()
        warehouse = self.warehouse_combo.currentText()

        for row in range(self.table.rowCount()):
            show = True

            # Поиск по коду и названию
            if search_text:
                code = self.table.item(row, 0).text().lower()
                name = self.table.item(row, 1).text().lower()
                batch = self.table.item(row, 2).text().lower()
                if search_text not in code and search_text not in name and search_text not in batch:
                    show = False

            # Фильтр по складу
            if warehouse != "Все склады":
                wh_cell = self.table.item(row, 8).text()
                if wh_cell != warehouse:
                    show = False

            self.table.setRowHidden(row, not show)

    def open_receipt_dialog(self):
        """Открыть диалог прихода"""
        dialog = ReceiptDialog(self)
        if dialog.exec():
            self.load_data()

    def open_issue_dialog(self):
        """Открыть диалог расхода"""
        dialog = IssueDialog(self)
        if dialog.exec():
            self.load_data()

    def open_inventory_dialog(self):
        """Открыть диалог инвентаризации"""
        QMessageBox.information(self, "В разработке", "Инвентаризация будет доступна в следующей версии")

    def generate_report(self):
        """Генерация отчета"""
        QMessageBox.information(self, "В разработке", "Отчеты будут доступны в следующей версии")

    def view_batch_details(self):
        """Просмотр деталей партии"""
        row = self.table.currentRow()
        if row >= 0:
            batch = self.table.item(row, 2).text()
            material = self.table.item(row, 1).text()
            QMessageBox.information(self, "Информация о партии",
                                  f"Партия: {batch}\nМатериал: {material}")


class ReceiptDialog(QDialog):
    """Диалог оформления прихода"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = DatabaseConnection()
        self.setWindowTitle("📥 Приход на склад")
        self.setModal(True)
        self.resize(800, 600)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Информация о поставке
        info_group = QGroupBox("Информация о поставке")
        info_layout = QFormLayout(info_group)

        # Генерация номера партии
        self.batch_number = self.generate_batch_number()
        self.batch_label = QLabel(f"<b>{self.batch_number}</b>")
        info_layout.addRow("Номер партии:", self.batch_label)

        # Дата
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        info_layout.addRow("Дата прихода:", self.date_edit)

        # Поставщик
        self.supplier_input = QLineEdit()
        self.supplier_input.setPlaceholderText("Название поставщика")
        info_layout.addRow("Поставщик:", self.supplier_input)

        # Документ
        self.document_input = QLineEdit()
        self.document_input.setPlaceholderText("Номер накладной")
        info_layout.addRow("Документ:", self.document_input)

        layout.addWidget(info_group)

        # Таблица позиций
        positions_group = QGroupBox("Позиции прихода")
        pos_layout = QVBoxLayout(positions_group)

        # Кнопки управления
        btn_layout = QHBoxLayout()
        self.btn_add_position = QPushButton("➕ Добавить позицию")
        self.btn_remove_position = QPushButton("➖ Удалить позицию")
        self.btn_add_position.clicked.connect(self.add_position)
        self.btn_remove_position.clicked.connect(self.remove_position)

        btn_layout.addWidget(self.btn_add_position)
        btn_layout.addWidget(self.btn_remove_position)
        btn_layout.addStretch()
        pos_layout.addLayout(btn_layout)

        # Таблица
        self.positions_table = QTableWidget()
        self.positions_table.setColumnCount(7)
        self.positions_table.setHorizontalHeaderLabels([
            "Материал", "Количество", "Ед.изм", "Цена", "Сумма", "Склад", "Место"
        ])
        pos_layout.addWidget(self.positions_table)

        layout.addWidget(positions_group)

        # Итоговая сумма
        total_layout = QHBoxLayout()
        total_layout.addStretch()
        self.total_label = QLabel("Итого: 0.00 ₽")
        self.total_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        total_layout.addWidget(self.total_label)
        layout.addLayout(total_layout)

        # Кнопки
        buttons = QHBoxLayout()
        self.btn_save = QPushButton("💾 Сохранить")
        self.btn_cancel = QPushButton("Отмена")

        self.btn_save.clicked.connect(self.save_receipt)
        self.btn_cancel.clicked.connect(self.reject)

        buttons.addWidget(self.btn_save)
        buttons.addWidget(self.btn_cancel)
        layout.addLayout(buttons)

        # Добавляем первую строку
        self.add_position()

    def generate_batch_number(self):
        """Генерация уникального номера партии (10 цифр)"""
        timestamp = datetime.now().strftime("%y%m%d")  # 6 цифр: ГГММДД
        random_part = str(random.randint(1000, 9999))  # 4 цифры
        return f"{timestamp}{random_part}"

    def add_position(self):
        """Добавить позицию"""
        row = self.positions_table.rowCount()
        self.positions_table.insertRow(row)

        # Материал
        material_combo = QComboBox()
        self.load_materials(material_combo)
        self.positions_table.setCellWidget(row, 0, material_combo)

        # Количество
        qty_spin = QDoubleSpinBox()
        qty_spin.setRange(0, 99999)
        qty_spin.setDecimals(2)
        qty_spin.valueChanged.connect(self.calculate_totals)
        self.positions_table.setCellWidget(row, 1, qty_spin)

        # Единица измерения
        unit_combo = QComboBox()
        unit_combo.addItems(["дм²", "м²", "м", "кг", "шт", "пара", "компл"])
        self.positions_table.setCellWidget(row, 2, unit_combo)

        # Цена
        price_spin = QDoubleSpinBox()
        price_spin.setRange(0, 999999)
        price_spin.setDecimals(2)
        price_spin.setSuffix(" ₽")
        price_spin.valueChanged.connect(self.calculate_totals)
        self.positions_table.setCellWidget(row, 3, price_spin)

        # Сумма (только чтение)
        sum_label = QLabel("0.00 ₽")
        sum_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.positions_table.setCellWidget(row, 4, sum_label)

        # Склад
        warehouse_combo = QComboBox()
        warehouse_combo.addItems(["Основной", "Производство", "Готовая продукция"])
        self.positions_table.setCellWidget(row, 5, warehouse_combo)

        # Место
        location_input = QLineEdit()
        location_input.setPlaceholderText("Стеллаж/ячейка")
        self.positions_table.setCellWidget(row, 6, location_input)

    def remove_position(self):
        """Удалить позицию"""
        current_row = self.positions_table.currentRow()
        if current_row >= 0:
            self.positions_table.removeRow(current_row)
            self.calculate_totals()

    def load_materials(self, combo):
        """Загрузка списка материалов"""
        try:
            conn = self.db.get_connection()
            if not conn:
                return

            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cursor.execute("""
                SELECT id, code, name
                FROM materials
                WHERE is_active = true
                ORDER BY name
            """)

            combo.addItem("", None)
            for mat in cursor.fetchall():
                combo.addItem(f"{mat['code']} - {mat['name']}", mat['id'])

            cursor.close()
            self.db.put_connection(conn)

        except Exception as e:
            print(f"Error loading materials: {e}")

    def calculate_totals(self):
        """Расчет итоговой суммы"""
        total = 0
        for row in range(self.positions_table.rowCount()):
            qty_widget = self.positions_table.cellWidget(row, 1)
            price_widget = self.positions_table.cellWidget(row, 3)
            sum_widget = self.positions_table.cellWidget(row, 4)

            if qty_widget and price_widget and sum_widget:
                qty = qty_widget.value()
                price = price_widget.value()
                row_sum = qty * price
                sum_widget.setText(f"{row_sum:.2f} ₽")
                total += row_sum

        self.total_label.setText(f"Итого: {total:,.2f} ₽")

    def save_receipt(self):
        """Сохранение прихода"""
        if self.positions_table.rowCount() == 0:
            QMessageBox.warning(self, "Ошибка", "Добавьте хотя бы одну позицию")
            return

        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            receipt_date = self.date_edit.date().toPyDate()

            for row in range(self.positions_table.rowCount()):
                material_combo = self.positions_table.cellWidget(row, 0)
                material_id = material_combo.currentData()

                if not material_id:
                    continue

                qty = self.positions_table.cellWidget(row, 1).value()
                unit = self.positions_table.cellWidget(row, 2).currentText()
                price = self.positions_table.cellWidget(row, 3).value()
                warehouse = self.positions_table.cellWidget(row, 5).currentText()
                location = self.positions_table.cellWidget(row, 6).text()

                # Проверяем, есть ли уже такая партия
                cursor.execute("""
                    SELECT id, quantity FROM warehouse_stock
                    WHERE material_id = %s AND batch_number = %s
                """, (material_id, self.batch_number))

                existing = cursor.fetchone()

                if existing:
                    # Обновляем количество
                    cursor.execute("""
                        UPDATE warehouse_stock
                        SET quantity = quantity + %s,
                            last_receipt_date = %s,
                            updated_at = NOW()
                        WHERE id = %s
                    """, (qty, receipt_date, existing[0]))
                else:
                    # Создаем новую запись
                    cursor.execute("""
                        INSERT INTO warehouse_stock
                        (material_id, warehouse_code, location, quantity, reserved_qty,
                         unit, batch_number, receipt_date, purchase_price,
                         last_receipt_date, updated_at)
                        VALUES (%s, %s, %s, %s, 0, %s, %s, %s, %s, %s, NOW())
                    """, (material_id, warehouse, location, qty, unit,
                          self.batch_number, receipt_date, price, receipt_date))

            conn.commit()
            cursor.close()
            self.db.put_connection(conn)

            QMessageBox.information(self, "Успешно",
                                  f"Приход оформлен\nПартия: {self.batch_number}")
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить: {e}")


class IssueDialog(QDialog):
    """Диалог оформления расхода"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = DatabaseConnection()
        self.setWindowTitle("📤 Расход со склада")
        self.setModal(True)
        self.resize(800, 500)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Выбор материала и партии
        select_group = QGroupBox("Выбор материала")
        select_layout = QFormLayout(select_group)

        # Материал
        self.material_combo = QComboBox()
        self.load_materials()
        self.material_combo.currentIndexChanged.connect(self.load_batches)
        select_layout.addRow("Материал:", self.material_combo)

        # Партия
        self.batch_combo = QComboBox()
        self.batch_combo.currentIndexChanged.connect(self.show_batch_info)
        select_layout.addRow("Партия:", self.batch_combo)

        # Информация о партии
        self.batch_info = QLabel("Выберите партию для просмотра информации")
        self.batch_info.setStyleSheet("padding: 10px; background: #f0f0f0; border-radius: 5px;")
        select_layout.addRow("Информация:", self.batch_info)

        layout.addWidget(select_group)

        # Параметры расхода
        issue_group = QGroupBox("Параметры расхода")
        issue_layout = QFormLayout(issue_group)

        # Количество
        self.qty_spin = QDoubleSpinBox()
        self.qty_spin.setRange(0, 99999)
        self.qty_spin.setDecimals(2)
        issue_layout.addRow("Количество:", self.qty_spin)

        # Назначение
        self.purpose_combo = QComboBox()
        self.purpose_combo.addItems(["Производство", "Брак", "Возврат поставщику", "Прочее"])
        issue_layout.addRow("Назначение:", self.purpose_combo)

        # Документ
        self.document_input = QLineEdit()
        self.document_input.setPlaceholderText("Номер документа")
        issue_layout.addRow("Документ:", self.document_input)

        # Дата
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        issue_layout.addRow("Дата расхода:", self.date_edit)

        layout.addWidget(issue_group)

        # Кнопки
        buttons = QHBoxLayout()
        self.btn_save = QPushButton("💾 Оформить расход")
        self.btn_cancel = QPushButton("Отмена")

        self.btn_save.clicked.connect(self.save_issue)
        self.btn_cancel.clicked.connect(self.reject)

        buttons.addWidget(self.btn_save)
        buttons.addWidget(self.btn_cancel)
        layout.addLayout(buttons)

    def load_materials(self):
        """Загрузка материалов с остатками"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

            cursor.execute("""
                SELECT DISTINCT m.id, m.code, m.name
                FROM materials m
                INNER JOIN warehouse_stock ws ON ws.material_id = m.id
                WHERE ws.quantity > 0
                ORDER BY m.name
            """)

            self.material_combo.addItem("", None)
            for mat in cursor.fetchall():
                self.material_combo.addItem(f"{mat['code']} - {mat['name']}", mat['id'])

            cursor.close()
            self.db.put_connection(conn)

        except Exception as e:
            print(f"Error loading materials: {e}")

    def load_batches(self):
        """Загрузка партий для выбранного материала"""
        self.batch_combo.clear()
        material_id = self.material_combo.currentData()

        if not material_id:
            return

        try:
            conn = self.db.get_connection()
            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

            cursor.execute("""
                SELECT id, batch_number, quantity, reserved_qty,
                       purchase_price, receipt_date, warehouse_code
                FROM warehouse_stock
                WHERE material_id = %s AND quantity > 0
                ORDER BY receipt_date  -- FIFO
            """, (material_id,))

            self.batch_combo.addItem("", None)
            for batch in cursor.fetchall():
                available = float(batch['quantity']) - float(batch['reserved_qty'] or 0)
                text = f"Партия {batch['batch_number']} | Доступно: {available:.2f}"
                self.batch_combo.addItem(text, batch)

            cursor.close()
            self.db.put_connection(conn)

        except Exception as e:
            print(f"Error loading batches: {e}")

    def show_batch_info(self):
        """Показать информацию о партии"""
        batch_data = self.batch_combo.currentData()

        if not batch_data:
            self.batch_info.setText("Выберите партию")
            self.qty_spin.setMaximum(0)
            return

        available = float(batch_data['quantity']) - float(batch_data['reserved_qty'] or 0)

        info = f"""
        Партия: {batch_data['batch_number']}
        Количество: {batch_data['quantity']:.2f}
        Резерв: {batch_data['reserved_qty'] or 0:.2f}
        Доступно: {available:.2f}
        Цена закупки: {batch_data['purchase_price']:.2f} ₽
        Дата прихода: {batch_data['receipt_date']}
        Склад: {batch_data['warehouse_code']}
        """

        self.batch_info.setText(info)
        self.qty_spin.setMaximum(available)

    def save_issue(self):
        """Сохранение расхода"""
        batch_data = self.batch_combo.currentData()

        if not batch_data:
            QMessageBox.warning(self, "Ошибка", "Выберите партию")
            return

        qty = self.qty_spin.value()
        if qty <= 0:
            QMessageBox.warning(self, "Ошибка", "Укажите количество")
            return

        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            # Уменьшаем количество на складе
            cursor.execute("""
                UPDATE warehouse_stock
                SET quantity = quantity - %s,
                    last_issue_date = %s,
                    updated_at = NOW()
                WHERE id = %s
            """, (qty, self.date_edit.date().toPyDate(), batch_data['id']))

            conn.commit()
            cursor.close()
            self.db.put_connection(conn)

            QMessageBox.information(self, "Успешно",
                                  f"Расход оформлен\nПартия: {batch_data['batch_number']}\nКоличество: {qty:.2f}")
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить: {e}")