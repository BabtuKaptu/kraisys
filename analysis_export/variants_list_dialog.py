"""Диалог для просмотра списка вариантов модели"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QMessageBox, QHeaderView
)
from PyQt6.QtCore import Qt, pyqtSignal
import psycopg2.extras


class VariantsListDialog(QDialog):
    """Диалог для просмотра и управления вариантами модели"""

    variant_selected = pyqtSignal(int)  # Сигнал при выборе варианта для редактирования

    def __init__(self, model_id, db, parent=None):
        super().__init__(parent)
        from debug_logger import log_debug

        log_debug(f"🏗️ VariantsListDialog INIT: получен model_id={model_id}")

        self.model_id = model_id
        self.db = db

        log_debug(f"🏗️ VariantsListDialog: установлен self.model_id={self.model_id}")

        self.setWindowTitle("Варианты модели")
        self.setModal(True)
        self.resize(800, 400)

        self.setup_ui()
        self.load_variants()

    def setup_ui(self):
        """Настройка интерфейса"""
        layout = QVBoxLayout(self)

        # Заголовок
        self.header_label = QLabel("Загрузка...")
        layout.addWidget(self.header_label)

        # Таблица вариантов
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "ID", "Название", "Код", "По умолчанию",
            "Стоимость материалов", "Активен"
        ])

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)

        header.resizeSection(0, 50)

        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.doubleClicked.connect(self.edit_variant)

        layout.addWidget(self.table)

        # Кнопки управления
        buttons_layout = QHBoxLayout()

        self.add_btn = QPushButton("➕ Добавить вариант")
        self.add_btn.clicked.connect(self.add_variant)
        buttons_layout.addWidget(self.add_btn)

        self.edit_btn = QPushButton("✏️ Редактировать")
        self.edit_btn.clicked.connect(self.edit_variant)
        buttons_layout.addWidget(self.edit_btn)

        self.view_btn = QPushButton("👁 Просмотр")
        self.view_btn.clicked.connect(self.view_variant)
        buttons_layout.addWidget(self.view_btn)

        self.delete_btn = QPushButton("🗑 Удалить")
        self.delete_btn.clicked.connect(self.delete_variant)
        buttons_layout.addWidget(self.delete_btn)

        buttons_layout.addStretch()

        self.close_btn = QPushButton("Закрыть")
        self.close_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(self.close_btn)

        layout.addLayout(buttons_layout)

    def load_variants(self):
        """Загрузка списка вариантов"""
        conn = self.db.get_connection()
        if not conn:
            return

        try:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

            # Загружаем информацию о модели
            cursor.execute("""
                SELECT name, article FROM models WHERE id = %s
            """, (self.model_id,))
            model = cursor.fetchone()

            if model:
                self.header_label.setText(
                    f"Варианты модели: {model['name']} ({model['article']})"
                )

            # Загружаем варианты
            cursor.execute("""
                SELECT id, variant_name, variant_code, is_default,
                       total_material_cost, is_active
                FROM specifications
                WHERE model_id = %s
                ORDER BY is_default DESC, created_at DESC
            """, (self.model_id,))

            variants = cursor.fetchall()

            self.table.setRowCount(0)
            for variant in variants:
                row = self.table.rowCount()
                self.table.insertRow(row)

                # ID
                self.table.setItem(row, 0, QTableWidgetItem(str(variant['id'])))

                # Название
                name = variant['variant_name'] or "Базовый вариант"
                self.table.setItem(row, 1, QTableWidgetItem(name))

                # Код
                code = variant['variant_code'] or "-"
                self.table.setItem(row, 2, QTableWidgetItem(code))

                # По умолчанию
                default = "✓" if variant['is_default'] else ""
                self.table.setItem(row, 3, QTableWidgetItem(default))

                # Стоимость
                cost = f"{variant['total_material_cost']:.2f}" if variant['total_material_cost'] else "-"
                self.table.setItem(row, 4, QTableWidgetItem(cost))

                # Активен
                active = "✓" if variant['is_active'] else "✗"
                self.table.setItem(row, 5, QTableWidgetItem(active))

            cursor.close()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки вариантов: {e}")

    def add_variant(self):
        """Добавить новый вариант"""
        from debug_logger import log_debug

        log_debug("🚀 ВЫЗВАН add_variant()")
        log_debug(f"🎯 VariantsListDialog.add_variant: передаем model_id={self.model_id}")

        from ui.references.model_specification_form_v5 import ModelSpecificationFormV5

        dialog = ModelSpecificationFormV5(
            model_id=self.model_id,
            is_variant=True,  # Новый вариант всегда является специфическим вариантом
            parent=self
        )
        dialog.saved.connect(self.load_variants)
        dialog.exec()

    def edit_variant(self):
        """Редактировать выбранный вариант"""
        from debug_logger import log_debug

        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Внимание", "Выберите вариант для редактирования")
            return

        variant_id = int(self.table.item(current_row, 0).text())
        log_debug(f"🎯 edit_variant: получен variant_id={variant_id} из строки {current_row}")

        # Проверяем, базовый ли это вариант
        is_default = self.table.item(current_row, 3).text() == "✓"
        log_debug(f"🎯 edit_variant: is_default={is_default} (значит is_variant={not is_default})")

        log_debug(f"🎯 edit_variant: вызываем ModelSpecificationFormV5 с model_id={self.model_id}, is_variant={not is_default}, variant_id={variant_id}")

        # Для всех вариантов используем одну и ту же форму
        from ui.references.model_specification_form_v5 import ModelSpecificationFormV5
        dialog = ModelSpecificationFormV5(
            model_id=self.model_id,  # ID базовой модели
            is_variant=not is_default,  # True для специфического варианта, False для базового
            variant_id=variant_id,  # ID конкретного варианта для редактирования
            parent=self
        )

        dialog.saved.connect(self.load_variants)
        dialog.exec()

    def view_variant(self):
        """Просмотр варианта"""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Внимание", "Выберите вариант для просмотра")
            return

        variant_id = int(self.table.item(current_row, 0).text())

        # Проверяем, базовый ли это вариант
        is_default = self.table.item(current_row, 3).text() == "✓"

        from ui.references.model_specification_form_v5 import ModelSpecificationFormV5
        dialog = ModelSpecificationFormV5(
            model_id=self.model_id,  # ID базовой модели
            is_variant=not is_default,  # True для специфического варианта, False для базового
            variant_id=variant_id,  # ID конкретного варианта для просмотра
            parent=self
        )
        dialog.exec()

    def delete_variant(self):
        """Удалить вариант"""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Внимание", "Выберите вариант для удаления")
            return

        # Проверяем, не базовый ли это вариант
        is_default = self.table.item(current_row, 3).text() == "✓"
        if is_default:
            QMessageBox.warning(self, "Внимание", "Нельзя удалить базовый вариант модели")
            return

        variant_name = self.table.item(current_row, 1).text()
        reply = QMessageBox.question(
            self,
            "Подтверждение",
            f"Удалить вариант '{variant_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            variant_id = int(self.table.item(current_row, 0).text())

            conn = self.db.get_connection()
            if conn:
                try:
                    cursor = conn.cursor()
                    cursor.execute("""
                        DELETE FROM specifications WHERE id = %s
                    """, (variant_id,))
                    conn.commit()
                    cursor.close()

                    self.load_variants()
                    QMessageBox.information(self, "Успех", "Вариант удален")

                except Exception as e:
                    conn.rollback()
                    QMessageBox.critical(self, "Ошибка", f"Ошибка удаления: {e}")