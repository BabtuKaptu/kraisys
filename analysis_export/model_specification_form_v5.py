"""Форма создания модели обуви с отдельной вкладкой для параметров модели"""
import json
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QFormLayout, QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox,
    QTableWidget, QTableWidgetItem, QPushButton, QTextEdit,
    QLabel, QGroupBox, QCheckBox, QHeaderView, QMessageBox,
    QScrollArea, QGridLayout, QAbstractItemView, QListWidget,
    QListWidgetItem, QDialogButtonBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from database.connection import DatabaseConnection
import psycopg2.extras
import json
import uuid


class ModelSpecificationFormV5(QDialog):
    """Форма создания/редактирования модели обуви с вкладкой параметров"""

    saved = pyqtSignal()

    def __init__(self, model_id=None, is_variant=False, variant_id=None, parent=None):
        super().__init__(parent)
        from debug_logger import log_debug

        log_debug(f"🏗️ ModelSpecificationFormV5 INIT: model_id={model_id}, is_variant={is_variant}, variant_id={variant_id}")
        self.model_id = model_id
        self.is_variant = is_variant  # Флаг: базовая модель или специфический вариант
        log_debug(f"🏗️ После установки: self.model_id={self.model_id}")
        self.base_model_id = None  # ID базовой модели для вариантов
        self.base_model_data = None  # Данные базовой модели
        self.specification_id = variant_id  # ID спецификации для редактирования существующего варианта
        log_debug(f"🏗️ self.specification_id установлен в: {self.specification_id}")

        # ВАЖНАЯ ПРОВЕРКА: variant_id должен быть передан для редактирования вариантов
        if is_variant and variant_id:
            log_debug(f"✅ ХОРОШО: Для редактирования варианта получен variant_id={variant_id}")
        elif is_variant and not variant_id:
            if model_id:
                log_debug(f"ℹ️ СОЗДАНИЕ: Создание нового варианта для базовой модели model_id={model_id}")
            else:
                log_debug(f"❌ ОШИБКА: is_variant=True но variant_id=None и model_id=None")
        else:
            log_debug(f"ℹ️ БАЗОВАЯ МОДЕЛЬ: Работа с базовой моделью model_id={model_id}")
        self.db = DatabaseConnection()

        # Справочники
        self.cutting_parts_list = []
        self.hardware_list = []
        self.materials_list = []
        self.perforation_types = []
        self.lining_types = []
        self.lasting_types = []

        title = "Специфический вариант модели" if is_variant else "Карта раскроя модели обуви"
        self.setWindowTitle(title)
        self.setModal(True)
        self.resize(1400, 750)
        self.setMinimumSize(1200, 550)

        self.setup_ui()
        self.load_reference_data()

        from debug_logger import log_debug

        log_debug(f"🔍 Перед загрузкой данных: self.model_id={self.model_id}, is_variant={self.is_variant}, variant_id={variant_id}")

        # Загружаем данные для редактирования существующего варианта
        if self.is_variant and variant_id:
            log_debug("📝 Ветка: Редактирование существующего варианта")
            self.load_variant_for_editing(variant_id)
        elif self.is_variant and model_id and not variant_id:
            # Новый вариант - загружаем данные базовой модели
            log_debug(f"🔄 Ветка: Создание нового варианта для базовой модели ID={model_id}")
            log_debug(f"📊 Текущие значения: self.model_id={self.model_id}, self.specification_id={self.specification_id}")
            self.load_base_model_data(model_id)
        elif model_id and not self.is_variant:
            # Редактирование базовой модели (НЕ создание варианта!)
            log_debug(f"🔄 Ветка: Редактирование базовой модели ID={model_id}")
            self.load_model_data()
        else:
            log_debug(f"❓ Неопределенная ветка: model_id={model_id}, is_variant={self.is_variant}, variant_id={variant_id}")

    def setup_ui(self):
        """Настройка интерфейса"""
        main_layout = QVBoxLayout(self)

        # Создаем основной виджет с прокруткой
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Виджет-контейнер для прокручиваемого содержимого
        scroll_widget = QWidget()
        layout = QVBoxLayout(scroll_widget)

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

        # Поля для варианта (показываются только для вариантов)
        self.variant_name_label = QLabel("Название варианта:")
        self.variant_name_input = QLineEdit()
        self.variant_name_input.setPlaceholderText("Например: Летняя коллекция")
        header_layout.addWidget(self.variant_name_label, 1, 0)
        header_layout.addWidget(self.variant_name_input, 1, 1)

        self.variant_article_label = QLabel("Код варианта:")
        self.variant_article_input = QLineEdit()
        self.variant_article_input.setPlaceholderText("VAR-001")
        header_layout.addWidget(self.variant_article_label, 1, 2)
        header_layout.addWidget(self.variant_article_input, 1, 3)

        # Изначально скрываем поля варианта
        self.variant_name_label.setVisible(False)
        self.variant_name_input.setVisible(False)
        self.variant_article_label.setVisible(False)
        self.variant_article_input.setVisible(False)

        # Колодка
        self.last_code_input = QLineEdit()
        self.last_code_input.setPlaceholderText("Например: 75")
        header_layout.addWidget(QLabel("Колодка:"), 2, 0)
        header_layout.addWidget(self.last_code_input, 2, 1)

        self.last_type_combo = QComboBox()
        self.last_type_combo.addItems(["Ботиночная", "Туфельная", "Сапожная", "Спортивная"])
        header_layout.addWidget(QLabel("Тип колодки:"), 2, 2)
        header_layout.addWidget(self.last_type_combo, 2, 3)

        # Размерный ряд
        self.size_min_spin = QSpinBox()
        self.size_min_spin.setRange(20, 50)
        self.size_min_spin.setValue(36)
        header_layout.addWidget(QLabel("Размер от:"), 3, 0)
        header_layout.addWidget(self.size_min_spin, 3, 1)

        self.size_max_spin = QSpinBox()
        self.size_max_spin.setRange(20, 50)
        self.size_max_spin.setValue(48)
        header_layout.addWidget(QLabel("Размер до:"), 3, 2)
        header_layout.addWidget(self.size_max_spin, 3, 3)

        # Тип затяжки
        self.lasting_combo = QComboBox()
        self.lasting_combo.addItem("Не выбрано", None)
        header_layout.addWidget(QLabel("Тип затяжки:"), 4, 0)
        header_layout.addWidget(self.lasting_combo, 4, 1)

        layout.addWidget(header_group)

        # Табы для разделов
        self.tabs = QTabWidget()

        # 1. НОВАЯ ВКЛАДКА: Параметры модели
        self.parameters_tab = self.create_parameters_tab()
        self.tabs.addTab(self.parameters_tab, "⚙️ Параметры модели")

        # 2. Детали кроя/Подошвы
        self.cutting_tab = self.create_cutting_tab()
        self.tabs.addTab(self.cutting_tab, "✂️ Детали кроя/Подошвы")

        # 3. Варианты исполнения
        self.variants_tab = self.create_variants_tab()
        self.tabs.addTab(self.variants_tab, "🎨 Варианты")

        layout.addWidget(self.tabs)

        # Устанавливаем виджет в область прокрутки
        scroll_area.setWidget(scroll_widget)
        main_layout.addWidget(scroll_area)

        # Кнопки (остаются внизу, не прокручиваются)
        buttons_layout = QHBoxLayout()
        self.save_btn = QPushButton("💾 Сохранить")
        self.save_btn.clicked.connect(self.save_model)
        self.cancel_btn = QPushButton("Отмена")
        self.cancel_btn.clicked.connect(self.reject)

        buttons_layout.addStretch()
        buttons_layout.addWidget(self.save_btn)
        buttons_layout.addWidget(self.cancel_btn)

        main_layout.addLayout(buttons_layout)

        # Первичная настройка видимости без заполнения полей (заполнение произойдет после загрузки данных)
        if self.is_variant:
            # Показываем поля для варианта
            self.variant_name_label.setVisible(True)
            self.variant_name_input.setVisible(True)
            self.variant_article_label.setVisible(True)
            self.variant_article_input.setVisible(True)
        else:
            # Скрываем поля для варианта
            self.variant_name_label.setVisible(False)
            self.variant_name_input.setVisible(False)
            self.variant_article_label.setVisible(False)
            self.variant_article_input.setVisible(False)

    def setup_field_visibility(self):
        """Настройка видимости полей в зависимости от режима (базовая модель vs вариант)"""
        from debug_logger import log_debug

        if self.is_variant:
            # Показываем поля для варианта
            self.variant_name_label.setVisible(True)
            self.variant_name_input.setVisible(True)
            self.variant_article_label.setVisible(True)
            self.variant_article_input.setVisible(True)

            # Заполняем название варианта по умолчанию если это новый вариант
            current_text = self.variant_name_input.text()
            if not self.specification_id and (not current_text or current_text == "Новый вариант"):
                model_name = self.name_input.text()
                default_name = f"{model_name} - Вариант" if model_name else "Новый вариант"
                log_debug(f"🏷️ setup_field_visibility: model_name='{model_name}', updating variant name from '{current_text}' to '{default_name}'")
                self.variant_name_input.setText(default_name)
            else:
                log_debug(f"🏷️ setup_field_visibility: не заполняем поле (specification_id={self.specification_id}, current_text='{current_text}')")
        else:
            # Скрываем поля для варианта
            self.variant_name_label.setVisible(False)
            self.variant_name_input.setVisible(False)
            self.variant_article_label.setVisible(False)
            self.variant_article_input.setVisible(False)

    def create_parameters_tab(self):
        """Создание вкладки параметров модели"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Информационное сообщение
        info_label = QLabel()
        if self.is_variant:
            info_label.setText(
                "💡 Для специфического варианта выберите один конкретный вариант для каждого параметра"
            )
        else:
            info_label.setText(
                "💡 Для базовой модели можно выбрать несколько вариантов для каждого параметра из справочников. "
                "Используйте кнопки \"Добавить\" для выбора из справочника."
            )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("background: #f0f8ff; padding: 10px; border-radius: 5px;")
        layout.addWidget(info_label)

        # Для базовых моделей - таблицы с выбором из справочников
        if not self.is_variant:
            # Варианты перфорации
            perf_group = QGroupBox("Варианты перфорации")
            perf_layout = QVBoxLayout(perf_group)

            # Кнопки управления
            perf_buttons = QHBoxLayout()
            add_perf_btn = QPushButton("Добавить")
            remove_perf_btn = QPushButton("Удалить")
            add_perf_btn.clicked.connect(self.add_perforation)
            remove_perf_btn.clicked.connect(self.remove_perforation)
            perf_buttons.addWidget(add_perf_btn)
            perf_buttons.addWidget(remove_perf_btn)
            perf_buttons.addStretch()
            perf_layout.addLayout(perf_buttons)

            # Таблица вариантов перфорации
            self.perforation_table = QTableWidget()
            self.perforation_table.setColumnCount(2)
            self.perforation_table.setHorizontalHeaderLabels(["Название", "Описание"])
            self.perforation_table.horizontalHeader().setStretchLastSection(True)

            # Настройки высоты строк для предотвращения наложения
            self.perforation_table.verticalHeader().setDefaultSectionSize(35)
            self.perforation_table.verticalHeader().setMinimumSectionSize(35)

            perf_layout.addWidget(self.perforation_table)
            layout.addWidget(perf_group)

            # Варианты подкладки/стельки
            lining_group = QGroupBox("Варианты подкладки/стельки")
            lining_layout = QVBoxLayout(lining_group)

            # Кнопки управления
            lining_buttons = QHBoxLayout()
            add_lining_btn = QPushButton("Добавить")
            remove_lining_btn = QPushButton("Удалить")
            add_lining_btn.clicked.connect(self.add_lining)
            remove_lining_btn.clicked.connect(self.remove_lining)
            lining_buttons.addWidget(add_lining_btn)
            lining_buttons.addWidget(remove_lining_btn)
            lining_buttons.addStretch()
            lining_layout.addLayout(lining_buttons)

            # Таблица вариантов подкладки
            self.lining_table = QTableWidget()
            self.lining_table.setColumnCount(2)
            self.lining_table.setHorizontalHeaderLabels(["Название", "Описание"])
            self.lining_table.horizontalHeader().setStretchLastSection(True)

            # Настройки высоты строк для предотвращения наложения
            self.lining_table.verticalHeader().setDefaultSectionSize(35)
            self.lining_table.verticalHeader().setMinimumSectionSize(35)

            lining_layout.addWidget(self.lining_table)
            layout.addWidget(lining_group)

        else:
            # Для специфических вариантов - комбобоксы
            params_group = QGroupBox("Параметры исполнения")
            params_layout = QGridLayout(params_group)

            # Варианты перфорации
            params_layout.addWidget(QLabel("Вариант перфорации:"), 0, 0)
            self.perforation_combo = QComboBox()
            self.perforation_combo.addItem("Не выбрано", None)
            params_layout.addWidget(self.perforation_combo, 0, 1)

            # Варианты подкладки/стельки
            params_layout.addWidget(QLabel("Вариант подкладки/стельки:"), 1, 0)
            self.lining_combo = QComboBox()
            self.lining_combo.addItem("Не выбрано", None)
            params_layout.addWidget(self.lining_combo, 1, 1)

            # Дополнительные параметры для специфического варианта
            params_layout.addWidget(QLabel("Сезон:"), 2, 0)
            self.season_combo = QComboBox()
            self.season_combo.addItems(["Весна-Лето", "Осень-Зима", "Демисезон", "Всесезон"])
            params_layout.addWidget(self.season_combo, 2, 1)

            params_layout.addWidget(QLabel("Артикул варианта:"), 3, 0)
            self.variant_article_input = QLineEdit()
            self.variant_article_input.setPlaceholderText("Например: VAR-001")
            params_layout.addWidget(self.variant_article_input, 3, 1)

            layout.addWidget(params_group)


        # Фурнитура
        hardware_group = QGroupBox("Фурнитура")
        hardware_layout = QVBoxLayout(hardware_group)

        # Кнопки управления
        hardware_buttons = QHBoxLayout()
        self.add_hardware_btn = QPushButton("➕ Добавить фурнитуру")
        self.add_hardware_btn.clicked.connect(self.add_hardware)
        self.remove_hardware_btn = QPushButton("➖ Удалить выбранное")
        self.remove_hardware_btn.clicked.connect(self.remove_hardware)
        hardware_buttons.addWidget(self.add_hardware_btn)
        hardware_buttons.addWidget(self.remove_hardware_btn)
        hardware_buttons.addStretch()
        hardware_layout.addLayout(hardware_buttons)

        # Таблица фурнитуры
        self.hardware_table = QTableWidget()
        self.hardware_table.setColumnCount(4)
        self.hardware_table.setHorizontalHeaderLabels([
            "Фурнитура", "Количество", "Единица", "Примечание"
        ])

        header = self.hardware_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)

        header.resizeSection(1, 100)
        header.resizeSection(2, 100)

        # Настройки высоты строк для предотвращения наложения
        self.hardware_table.verticalHeader().setDefaultSectionSize(35)
        self.hardware_table.verticalHeader().setMinimumSectionSize(35)

        hardware_layout.addWidget(self.hardware_table)
        layout.addWidget(hardware_group)


        layout.addStretch()
        return widget

    def add_perforation(self):
        """Добавить вариант перфорации"""
        try:
            # Проверяем доступность справочных данных
            if not hasattr(self, 'perforation_types') or not self.perforation_types:
                QMessageBox.warning(self, "Предупреждение",
                    "Справочник типов перфорации не загружен.\n"
                    "Проверьте подключение к базе данных и наличие таблицы perforation_types.")
                return

            # Создаем диалог выбора из справочника
            dialog = QDialog(self)
            dialog.setWindowTitle("Выберите вариант перфорации")
            dialog.setModal(True)
            layout = QVBoxLayout(dialog)

            # Комбобокс с вариантами
            combo = QComboBox()
            combo.addItem("Выберите...", None)

            # Загружаем варианты из справочника
            for perf in self.perforation_types:
                # Проверяем, не добавлен ли уже этот вариант
                already_added = False
                for row in range(self.perforation_table.rowCount()):
                    if self.perforation_table.item(row, 0) and self.perforation_table.item(row, 0).data(Qt.ItemDataRole.UserRole) == perf['id']:
                        already_added = True
                        break
                if not already_added:
                    combo.addItem(f"{perf['code']} - {perf['name']}", perf)

            layout.addWidget(combo)

            # Кнопки
            buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addWidget(buttons)

            if dialog.exec() == QDialog.DialogCode.Accepted:
                perf_data = combo.currentData()
                if perf_data:
                    # Добавляем в таблицу
                    row = self.perforation_table.rowCount()
                    self.perforation_table.insertRow(row)

                    item_name = QTableWidgetItem(perf_data['name'])
                    item_name.setData(Qt.ItemDataRole.UserRole, perf_data['id'])
                    self.perforation_table.setItem(row, 0, item_name)

                    self.perforation_table.setItem(row, 1, QTableWidgetItem(perf_data.get('description', '')))

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при добавлении варианта перфорации: {e}")

    def remove_perforation(self):
        """Удалить выбранный вариант перфорации"""
        current_row = self.perforation_table.currentRow()
        if current_row >= 0:
            self.perforation_table.removeRow(current_row)

    def add_lining(self):
        """Добавить вариант подкладки"""
        try:
            # Проверяем доступность справочных данных
            if not hasattr(self, 'lining_types') or not self.lining_types:
                QMessageBox.warning(self, "Предупреждение",
                    "Справочник типов подкладки не загружен.\n"
                    "Проверьте подключение к базе данных и наличие таблицы lining_types.")
                return

            # Создаем диалог выбора из справочника
            dialog = QDialog(self)
            dialog.setWindowTitle("Выберите вариант подкладки")
            dialog.setModal(True)
            layout = QVBoxLayout(dialog)

            # Комбобокс с вариантами
            combo = QComboBox()
            combo.addItem("Выберите...", None)

            # Загружаем варианты из справочника
            for lining in self.lining_types:
                # Проверяем, не добавлен ли уже этот вариант
                already_added = False
                for row in range(self.lining_table.rowCount()):
                    if self.lining_table.item(row, 0) and self.lining_table.item(row, 0).data(Qt.ItemDataRole.UserRole) == lining['id']:
                        already_added = True
                        break
                if not already_added:
                    combo.addItem(f"{lining['code']} - {lining['name']}", lining)

            layout.addWidget(combo)

            # Кнопки
            buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addWidget(buttons)

            if dialog.exec() == QDialog.DialogCode.Accepted:
                lining_data = combo.currentData()
                if lining_data:
                    # Добавляем в таблицу
                    row = self.lining_table.rowCount()
                    self.lining_table.insertRow(row)

                    item_name = QTableWidgetItem(lining_data['name'])
                    item_name.setData(Qt.ItemDataRole.UserRole, lining_data['id'])
                    self.lining_table.setItem(row, 0, item_name)

                    self.lining_table.setItem(row, 1, QTableWidgetItem(lining_data.get('description', '')))

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при добавлении варианта подкладки: {e}")

    def remove_lining(self):
        """Удалить выбранный вариант подкладки"""
        current_row = self.lining_table.currentRow()
        if current_row >= 0:
            self.lining_table.removeRow(current_row)

    def select_all_items(self, list_widget):
        """Выбрать все элементы в списке"""
        for i in range(list_widget.count()):
            item = list_widget.item(i)
            item.setSelected(True)

    def create_cutting_tab(self):
        """Вкладка деталей кроя и подошв"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # === ДЕТАЛИ КРОЯ ===
        cutting_group = QGroupBox("Детали кроя")
        cutting_layout = QVBoxLayout(cutting_group)

        # Кнопки управления деталями кроя
        cutting_btn_layout = QHBoxLayout()
        self.add_cutting_btn = QPushButton("➕ Добавить деталь")
        self.add_cutting_btn.clicked.connect(self.add_cutting_part)
        self.remove_cutting_btn = QPushButton("➖ Удалить выбранное")
        self.remove_cutting_btn.clicked.connect(self.remove_cutting_part)
        cutting_btn_layout.addWidget(self.add_cutting_btn)
        cutting_btn_layout.addWidget(self.remove_cutting_btn)
        cutting_btn_layout.addStretch()
        cutting_layout.addLayout(cutting_btn_layout)

        # Таблица деталей кроя
        self.cutting_table = QTableWidget()
        if self.is_variant:
            self.cutting_table.setColumnCount(5)
            self.cutting_table.setHorizontalHeaderLabels([
                "Деталь кроя", "Количество", "Расход (дм²)", "Материал (конкретный)", "Примечание"
            ])
        else:
            self.cutting_table.setColumnCount(5)
            self.cutting_table.setHorizontalHeaderLabels([
                "Деталь кроя", "Количество", "Расход (дм²)", "Материал (база)", "Примечание"
            ])

        cutting_header = self.cutting_table.horizontalHeader()
        cutting_header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        cutting_header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        cutting_header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        cutting_header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        cutting_header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        cutting_header.resizeSection(1, 100)
        cutting_header.resizeSection(2, 120)

        # Настройки высоты строк для предотвращения наложения
        self.cutting_table.verticalHeader().setDefaultSectionSize(35)
        self.cutting_table.verticalHeader().setMinimumSectionSize(35)

        cutting_layout.addWidget(self.cutting_table)
        layout.addWidget(cutting_group)

        # === ПОДОШВЫ ===
        soles_group = QGroupBox("Подошвы")
        soles_layout = QVBoxLayout(soles_group)

        # Кнопки управления подошвами
        soles_btn_layout = QHBoxLayout()
        self.add_sole_btn = QPushButton("➕ Добавить подошву")
        self.add_sole_btn.clicked.connect(self.add_sole)
        self.remove_sole_btn = QPushButton("➖ Удалить выбранную")
        self.remove_sole_btn.clicked.connect(self.remove_sole)
        soles_btn_layout.addWidget(self.add_sole_btn)
        soles_btn_layout.addWidget(self.remove_sole_btn)
        soles_btn_layout.addStretch()
        soles_layout.addLayout(soles_btn_layout)

        # Таблица подошв
        self.soles_table = QTableWidget()
        self.soles_table.setColumnCount(5)
        self.soles_table.setHorizontalHeaderLabels([
            "Материал", "Толщина (мм)", "Цвет", "Высота каблука (мм)", "Высота платформы (мм)"
        ])

        soles_header = self.soles_table.horizontalHeader()
        soles_header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        soles_header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        soles_header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        soles_header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        soles_header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        soles_header.resizeSection(1, 120)
        soles_header.resizeSection(3, 130)
        soles_header.resizeSection(4, 140)

        # Настройки высоты строк для предотвращения наложения
        self.soles_table.verticalHeader().setDefaultSectionSize(35)
        self.soles_table.verticalHeader().setMinimumSectionSize(35)

        soles_layout.addWidget(self.soles_table)
        layout.addWidget(soles_group)

        return widget


    def add_sole(self):
        """Добавить подошву"""
        from ui.references.sole_dialog import SoleDialog

        dialog = SoleDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            sole_data = dialog.get_sole_data()

            row = self.soles_table.rowCount()
            self.soles_table.insertRow(row)

            # Создаем виджеты для ячеек
            material_item = QTableWidgetItem(sole_data.get('material', ''))
            # Сохраняем ID материала в UserRole для последующего использования
            if sole_data.get('material_id'):
                material_item.setData(Qt.ItemDataRole.UserRole, sole_data['material_id'])

            thickness_item = QTableWidgetItem(str(sole_data.get('thickness', 0)))
            color_item = QTableWidgetItem(sole_data.get('color', ''))
            heel_height_item = QTableWidgetItem(str(sole_data.get('heel_height', 0)))
            platform_height_item = QTableWidgetItem(str(sole_data.get('platform_height', 0)))

            self.soles_table.setItem(row, 0, material_item)
            self.soles_table.setItem(row, 1, thickness_item)
            self.soles_table.setItem(row, 2, color_item)
            self.soles_table.setItem(row, 3, heel_height_item)
            self.soles_table.setItem(row, 4, platform_height_item)

    def remove_sole(self):
        """Удалить выбранную подошву"""
        current_row = self.soles_table.currentRow()
        if current_row >= 0:
            reply = QMessageBox.question(
                self,
                "Подтверждение",
                "Удалить выбранную подошву?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.soles_table.removeRow(current_row)

    def create_variants_tab(self):
        """Вкладка вариантов модели обуви"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Заголовок
        header = QHBoxLayout()
        title = QLabel("Варианты модели обуви")
        title.setStyleSheet("font-size: 14px; font-weight: bold;")
        header.addWidget(title)
        header.addStretch()
        layout.addLayout(header)

        # Информация
        info = QLabel(
            "Управление вариантами модели. Каждый вариант имеет свой состав материалов, "
            "перфорацию, подкладку и стоимость."
        )
        info.setWordWrap(True)
        info.setStyleSheet("color: gray; margin: 10px 0;")
        layout.addWidget(info)

        # Таблица вариантов
        self.variants_table = QTableWidget()
        self.variants_table.setColumnCount(7)
        self.variants_table.setHorizontalHeaderLabels([
            "ID", "Название", "Код", "Перфорация", "Подкладка",
            "Стоимость материалов", "Активен"
        ])

        header = self.variants_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(0, 50)
        header.resizeSection(6, 80)

        self.variants_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.variants_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.variants_table.doubleClicked.connect(self.edit_variant)

        # Настройки высоты строк для предотвращения наложения
        self.variants_table.verticalHeader().setDefaultSectionSize(35)
        self.variants_table.verticalHeader().setMinimumSectionSize(35)

        layout.addWidget(self.variants_table)

        # Кнопки
        btn_layout = QHBoxLayout()
        add_variant_btn = QPushButton("➕ Создать вариант")
        add_variant_btn.clicked.connect(self.add_variant)

        edit_variant_btn = QPushButton("✏️ Редактировать")
        edit_variant_btn.clicked.connect(self.edit_variant)

        view_variant_btn = QPushButton("👁 Просмотр")
        view_variant_btn.clicked.connect(self.view_variant)

        remove_variant_btn = QPushButton("🗑 Удалить")
        remove_variant_btn.clicked.connect(self.remove_variant)

        refresh_btn = QPushButton("🔄 Обновить")
        refresh_btn.clicked.connect(self.load_variants)

        btn_layout.addWidget(add_variant_btn)
        btn_layout.addWidget(edit_variant_btn)
        btn_layout.addWidget(view_variant_btn)
        btn_layout.addWidget(remove_variant_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(refresh_btn)

        layout.addLayout(btn_layout)

        # Загружаем варианты при инициализации
        if self.model_id:
            self.load_variants()

        return widget

    def load_reference_data(self):
        """Загрузка справочных данных"""
        conn = self.db.get_connection()
        if not conn:
            return

        try:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

            # Загружаем типы перфорации
            cursor.execute("SELECT id, code, name FROM perforation_types WHERE is_active = true")
            self.perforation_types = cursor.fetchall()

            # Загружаем типы подкладки
            cursor.execute("SELECT id, code, name FROM lining_types WHERE is_active = true")
            self.lining_types = cursor.fetchall()

            # Загружаем типы затяжки
            cursor.execute("SELECT id, code, name FROM lasting_types WHERE is_active = true")
            self.lasting_types = cursor.fetchall()

            # Загружаем детали раскроя
            cursor.execute("SELECT id, code, name, category FROM cutting_parts WHERE is_active = true ORDER BY category, name")
            self.cutting_parts = cursor.fetchall()

            # Загружаем фурнитуру (материалы разных групп, которые могут использоваться как фурнитура)
            cursor.execute("""
                SELECT id, name, code FROM materials
                WHERE (group_type = 'HARDWARE' OR name LIKE '%блочки%' OR name LIKE '%люверсы%'
                       OR name LIKE '%крючки%' OR name LIKE '%шнурки%' OR name LIKE '%Блочки%'
                       OR name LIKE '%Люверсы%' OR name LIKE '%Крючки%' OR name LIKE '%Шнурки%'
                       OR code LIKE '%BLOCHKI%' OR code LIKE '%KRYUCHKI%')
                AND is_active = true
                ORDER BY name
            """)
            self.hardware_list = cursor.fetchall()

            # Заполняем виджеты
            if self.is_variant:
                # Для специфического варианта - НЕ заполляем комбобоксы здесь
                # Они будут заполнены в load_base_model_options() с правильной фильтрацией
                pass
            else:
                # Для базовой модели сохраняем типы для использования в диалогах добавления
                pass

            # Тип затяжки - всегда комбобокс
            for lasting in self.lasting_types:
                self.lasting_combo.addItem(lasting['name'], lasting['id'])

            cursor.close()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки справочников: {e}")
        finally:
            # Обязательно возвращаем соединение в пул
            if conn:
                self.db.put_connection(conn)

    def load_base_model_for_variant(self, model_id):
        """Загрузка данных базовой модели для создания/редактирования варианта"""
        print(f"🔍 load_base_model_for_variant: model_id = {model_id}")

        try:
            conn = self.db.get_connection()
            if not conn:
                return

            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

            # Ищем базовую спецификацию для этой модели
            cursor.execute("""
                SELECT * FROM specifications
                WHERE model_id = %s AND is_default = true
                LIMIT 1
            """, (model_id,))

            base_spec = cursor.fetchone()

            if base_spec:
                self.base_model_data = dict(base_spec)
                self.base_model_id = base_spec['id']
                print(f"✅ Загружена базовая спецификация ID={self.base_model_id}")

                # Загружаем опции и элементы раскроя
                self.load_base_model_options()
                self.load_cutting_parts_from_base_model()

            else:
                print(f"❌ Базовая спецификация для модели {model_id} не найдена")

            cursor.close()
            self.db.put_connection(conn)

        except Exception as e:
            print(f"❌ Ошибка загрузки базовой модели для варианта: {e}")

    def load_base_model_data(self):
        """Загрузка данных базовой модели для вариантов"""
        print(f"🔍 load_base_model_data: base_model_id = {getattr(self, 'base_model_id', 'НЕТ')}")

        if not self.base_model_id:
            print("❌ base_model_id отсутствует")
            return

        conn = self.db.get_connection()
        if not conn:
            print("❌ Нет соединения с БД")
            return

        try:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

            # Загружаем данные базовой модели
            cursor.execute("""
                SELECT * FROM specifications
                WHERE id = %s
            """, (self.base_model_id,))

            model = cursor.fetchone()
            if model:
                self.base_model_data = dict(model)
                print(f"✅ Загружены данные базовой модели ID={self.base_model_id}")
                print(f"🔍 cutting_parts в base_model_data: {self.base_model_data.get('cutting_parts')}")

                # Для специфического варианта загружаем только те варианты,
                # которые есть в базовой модели
                if self.is_variant:
                    from debug_logger import log_debug
                    log_debug(f"🔧 Вызываем load_base_model_options() для варианта")
                    self.load_base_model_options()
                    log_debug(f"🔧 Вызываем load_cutting_parts_from_base_model() для варианта")
                    # Автоматически загружаем элементы раскроя из базовой модели
                    self.load_cutting_parts_from_base_model()
            else:
                print(f"❌ Базовая модель с ID={self.base_model_id} не найдена")

        except Exception as e:
            print(f"❌ Ошибка загрузки данных базовой модели: {e}")
        finally:
            if conn:
                self.db.put_connection(conn)

    def load_base_model_options(self):
        """Загружает варианты только из базовой модели для комбобоксов"""
        from debug_logger import log_debug
        log_debug(f"🔍 load_base_model_options: base_model_data = {bool(self.base_model_data)}")

        if not self.base_model_data:
            log_debug("❌ base_model_data отсутствует, выходим")
            return

        # Очищаем комбобоксы перед заполнением
        self.perforation_combo.clear()
        self.lining_combo.clear()

        self.perforation_combo.addItem("Не выбрано", None)
        self.lining_combo.addItem("Не выбрано", None)

        # Для вариантов заполняем ВСЕ доступные опции
        if self.is_variant:
            # Сначала убедимся что у нас есть reference data
            if not hasattr(self, 'perforation_types') or not self.perforation_types:
                log_debug("🔄 Загружаем reference data для комбобоксов варианта")
                self.load_reference_data()

            log_debug(f"🎨 Заполняем комбобоксы для варианта: перфораций={len(getattr(self, 'perforation_types', []))}, подкладок={len(getattr(self, 'lining_types', []))}")

            # Заполняем ВСЕ типы перфорации (пользователь сам выберет нужный)
            if hasattr(self, 'perforation_types'):
                for perf_type in self.perforation_types:
                    self.perforation_combo.addItem(perf_type['name'], perf_type['id'])

            # Заполняем ВСЕ типы подкладки
            if hasattr(self, 'lining_types'):
                for lining_type in self.lining_types:
                    self.lining_combo.addItem(lining_type['name'], lining_type['id'])

            log_debug(f"✅ Комбобоксы заполнены: перфорация={self.perforation_combo.count()}, подкладка={self.lining_combo.count()}")
        else:
            # Для базовых моделей - старая логика с фильтрацией
            # Проверяем perforation_ids из базовой модели
            perforation_ids = self.base_model_data.get('perforation_ids') if self.base_model_data else None
            if perforation_ids:
                if isinstance(perforation_ids, str):
                    try:
                        perforation_ids = json.loads(perforation_ids)
                    except:
                        perforation_ids = []

                if isinstance(perforation_ids, list):
                    # Загружаем названия перфораций по ID
                    for perf_type in self.perforation_types:
                        if perf_type['id'] in perforation_ids:
                            self.perforation_combo.addItem(perf_type['name'], perf_type['id'])

            # Проверяем lining_ids из базовой модели
            lining_ids = self.base_model_data.get('lining_ids') if self.base_model_data else None
            if lining_ids:
                if isinstance(lining_ids, str):
                    try:
                        lining_ids = json.loads(lining_ids)
                    except:
                        lining_ids = []

                if isinstance(lining_ids, list):
                    # Загружаем названия подкладок по ID
                    for lining_type in self.lining_types:
                        if lining_type['id'] in lining_ids:
                            self.lining_combo.addItem(lining_type['name'], lining_type['id'])

    def load_cutting_parts_from_base_model(self):
        """Загружает все элементы раскроя из базовой модели в таблицу варианта"""
        if not self.base_model_data:
            print("❌ Нет данных базовой модели для загрузки элементов раскроя")
            return

        cutting_parts_json = self.base_model_data.get('cutting_parts')
        if not cutting_parts_json:
            print("ℹ️ В базовой модели нет элементов раскроя")
            return

        try:
            import json
            cutting_parts = json.loads(cutting_parts_json) if isinstance(cutting_parts_json, str) else cutting_parts_json
            print(f"✅ Загружаем {len(cutting_parts)} элементов раскроя из базовой модели")

            # Очищаем таблицу
            self.cutting_table.setRowCount(0)

            # Добавляем все элементы из базовой модели
            for part in cutting_parts:
                row = self.cutting_table.rowCount()
                self.cutting_table.insertRow(row)

                # Название детали (нередактируемое - из базовой модели)
                part_item = QTableWidgetItem(part.get('name', ''))
                part_item.setFlags(part_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                part_item.setBackground(Qt.GlobalColor.lightGray)  # Отличаем базовые элементы
                self.cutting_table.setItem(row, 0, part_item)

                # Количество
                qty_spin = QSpinBox()
                qty_spin.setRange(1, 100)
                qty_spin.setValue(part.get('quantity', 1))
                self.cutting_table.setCellWidget(row, 1, qty_spin)

                # Расход (дм²) - берем из базовой модели
                consumption_spin = QDoubleSpinBox()
                consumption_spin.setRange(0.1, 999.9)
                consumption_spin.setValue(part.get('consumption', 1.0))
                consumption_spin.setDecimals(1)
                consumption_spin.setSuffix(" дм²")
                self.cutting_table.setCellWidget(row, 2, consumption_spin)

                # Материал - конкретный выбор для варианта
                material_combo = QComboBox()
                material_combo.addItem("Выберите материал...", None)
                self.load_leather_fabric_materials(material_combo)
                self.cutting_table.setCellWidget(row, 3, material_combo)

                # Примечание
                self.cutting_table.setItem(row, 4, QTableWidgetItem(part.get('notes', '')))

        except Exception as e:
            print(f"❌ Ошибка загрузки элементов раскроя из базовой модели: {e}")

    def add_cutting_part(self):
        """Добавить деталь кроя"""
        if self.is_variant:
            self.add_cutting_part_variant()
        else:
            self.add_cutting_part_base()

    def add_cutting_part_base(self):
        """Добавить деталь кроя для базовой модели"""
        try:
            # Проверяем доступность справочных данных
            if not hasattr(self, 'cutting_parts') or not self.cutting_parts:
                QMessageBox.warning(self, "Предупреждение",
                    "Справочник деталей раскроя не загружен.\n"
                    "Проверьте подключение к базе данных и наличие таблицы cutting_parts.")
                return

            # Создаем диалог выбора из справочника
            dialog = QDialog(self)
            dialog.setWindowTitle("Выберите деталь раскроя")
            dialog.setModal(True)
            layout = QVBoxLayout(dialog)

            # Комбобокс с вариантами
            combo = QComboBox()
            combo.addItem("Выберите...", None)

            # Загружаем варианты из справочника
            for cutting_part in self.cutting_parts:
                # Проверяем, не добавлена ли уже эта деталь
                already_added = False
                for row in range(self.cutting_table.rowCount()):
                    if self.cutting_table.item(row, 0) and self.cutting_table.item(row, 0).data(Qt.ItemDataRole.UserRole) == cutting_part['id']:
                        already_added = True
                        break
                if not already_added:
                    display_text = f"{cutting_part['code']} - {cutting_part['name']}"
                    if cutting_part.get('category'):
                        display_text += f" ({cutting_part['category']})"
                    combo.addItem(display_text, cutting_part)

            layout.addWidget(combo)

            # Кнопки
            buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addWidget(buttons)

            if dialog.exec() == QDialog.DialogCode.Accepted:
                cutting_data = combo.currentData()
                if cutting_data:
                    # Добавляем в таблицу
                    row = self.cutting_table.rowCount()
                    self.cutting_table.insertRow(row)

                    # Название детали с сохранением ID
                    item_name = QTableWidgetItem(cutting_data['name'])
                    item_name.setData(Qt.ItemDataRole.UserRole, cutting_data['id'])
                    self.cutting_table.setItem(row, 0, item_name)

                    # Количество
                    qty_spin = QSpinBox()
                    qty_spin.setRange(1, 100)
                    qty_spin.setValue(2)
                    self.cutting_table.setCellWidget(row, 1, qty_spin)

                    # Расход (дм²)
                    consumption_spin = QDoubleSpinBox()
                    consumption_spin.setRange(0.1, 999.9)
                    consumption_spin.setValue(1.0)
                    consumption_spin.setDecimals(1)
                    consumption_spin.setSuffix(" дм²")
                    self.cutting_table.setCellWidget(row, 2, consumption_spin)

                    # Материал (текст для базовой модели)
                    self.cutting_table.setItem(row, 3, QTableWidgetItem("Кожа/Замша"))

                    # Примечание
                    self.cutting_table.setItem(row, 4, QTableWidgetItem(""))

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при добавлении детали раскроя: {e}")

    def add_cutting_part_variant(self):
        """Добавить дополнительную деталь кроя для варианта из справочника"""
        print(f"🔍 add_cutting_part_variant: добавление из справочника cutting_parts")

        # Проверяем доступность справочных данных
        if not hasattr(self, 'cutting_parts') or not self.cutting_parts:
            QMessageBox.warning(self, "Предупреждение",
                "Справочник деталей раскроя не загружен.\n"
                "Проверьте подключение к базе данных и наличие таблицы cutting_parts.")
            return

        # Создаем диалог выбора из справочника
        dialog = QDialog(self)
        dialog.setWindowTitle("Выберите дополнительную деталь раскроя")
        dialog.setModal(True)
        layout = QVBoxLayout(dialog)

        # Комбобокс с вариантами из справочника
        combo = QComboBox()
        combo.addItem("Выберите...", None)

        # Загружаем варианты из справочника cutting_parts
        for cutting_part in self.cutting_parts:
            # Проверяем, не добавлена ли уже эта деталь
            already_added = False
            for row in range(self.cutting_table.rowCount()):
                item = self.cutting_table.item(row, 0)
                if item and item.text() == cutting_part['name']:
                    already_added = True
                    break

            if not already_added:
                display_text = f"{cutting_part['code']} - {cutting_part['name']}"
                if cutting_part.get('category'):
                    display_text += f" ({cutting_part['category']})"
                combo.addItem(display_text, cutting_part)

        layout.addWidget(QLabel("Дополнительная деталь кроя:"))
        layout.addWidget(combo)

        # Кнопки
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            cutting_data = combo.currentData()
            if cutting_data:
                self.add_cutting_part_from_catalog(cutting_data)

    def add_cutting_part_from_catalog(self, cutting_data):
        """Добавляет дополнительную деталь кроя из справочника в таблицу варианта"""
        row = self.cutting_table.rowCount()
        self.cutting_table.insertRow(row)

        # Название детали с сохранением ID (редактируемое - дополнительное)
        item_name = QTableWidgetItem(cutting_data['name'])
        item_name.setData(Qt.ItemDataRole.UserRole, cutting_data['id'])
        # Отличаем дополнительные элементы белым фоном
        self.cutting_table.setItem(row, 0, item_name)

        # Количество
        qty_spin = QSpinBox()
        qty_spin.setRange(1, 100)
        qty_spin.setValue(cutting_data.get('default_qty', 2))
        self.cutting_table.setCellWidget(row, 1, qty_spin)

        # Расход (дм²) - берем из справочника или по умолчанию
        consumption_spin = QDoubleSpinBox()
        consumption_spin.setRange(0.1, 999.9)
        consumption_spin.setValue(cutting_data.get('material_consumption', 1.0))
        consumption_spin.setDecimals(1)
        consumption_spin.setSuffix(" дм²")
        self.cutting_table.setCellWidget(row, 2, consumption_spin)

        # Материал - комбобокс с кожа/ткань материалами
        material_combo = QComboBox()
        material_combo.addItem("Выберите материал...", None)
        self.load_leather_fabric_materials(material_combo)
        self.cutting_table.setCellWidget(row, 3, material_combo)

        # Примечание
        self.cutting_table.setItem(row, 4, QTableWidgetItem(cutting_data.get('notes', '')))

    def add_cutting_part_from_base(self, part_data):
        """Добавляет деталь кроя из базовой модели в таблицу варианта"""
        row = self.cutting_table.rowCount()
        self.cutting_table.insertRow(row)

        # Название детали (нередактируемое)
        part_item = QTableWidgetItem(part_data.get('name', ''))
        part_item.setFlags(part_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.cutting_table.setItem(row, 0, part_item)

        # Количество (берем из базовой модели, можно изменить)
        qty_spin = QSpinBox()
        qty_spin.setRange(1, 100)
        qty_spin.setValue(part_data.get('quantity', 2))
        self.cutting_table.setCellWidget(row, 1, qty_spin)

        # Расход (дм²)
        consumption_spin = QDoubleSpinBox()
        consumption_spin.setRange(0.1, 999.9)
        consumption_spin.setValue(part_data.get('consumption', 1.0))
        consumption_spin.setDecimals(1)
        consumption_spin.setSuffix(" дм²")
        self.cutting_table.setCellWidget(row, 2, consumption_spin)

        # Материал - комбобокс с кожа/ткань материалами
        material_combo = QComboBox()
        material_combo.addItem("Выберите материал...", None)
        self.load_leather_fabric_materials(material_combo)
        self.cutting_table.setCellWidget(row, 3, material_combo)

        # Примечание
        self.cutting_table.setItem(row, 4, QTableWidgetItem(part_data.get('note', '')))

    def load_leather_fabric_materials(self, combo_box):
        """Загружает материалы кожа/ткань в комбобокс"""
        db = DatabaseConnection()
        conn = db.get_connection()
        if not conn:
            return

        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, code FROM materials
                WHERE group_type IN ('LEATHER', 'LINING')
                ORDER BY group_type, name
            """)
            materials = cursor.fetchall()

            for material_id, name, code in materials:
                display_text = f"{name} ({code})" if code else name
                combo_box.addItem(display_text, material_id)

            cursor.close()
        except Exception as e:
            print(f"Ошибка загрузки материалов кожа/ткань: {e}")
        finally:
            if conn:
                db.put_connection(conn)

    def remove_cutting_part(self):
        """Удалить выбранную деталь кроя"""
        current_row = self.cutting_table.currentRow()
        if current_row >= 0:
            self.cutting_table.removeRow(current_row)

    def add_hardware(self):
        """Добавить фурнитуру"""
        row = self.hardware_table.rowCount()
        self.hardware_table.insertRow(row)

        # Комбобокс для выбора фурнитуры из материалов группы HARDWARE
        hw_combo = QComboBox()
        hw_combo.addItem("Выберите фурнитуру...", None)

        # Загружаем материалы группы HARDWARE из базы данных
        self.load_hardware_materials(hw_combo)
        self.hardware_table.setCellWidget(row, 0, hw_combo)

        # Количество
        qty_spin = QSpinBox()
        qty_spin.setRange(1, 100)
        qty_spin.setValue(1)
        self.hardware_table.setCellWidget(row, 1, qty_spin)

        # Единица
        unit_combo = QComboBox()
        unit_combo.addItems(["шт", "пара", "комплект"])
        self.hardware_table.setCellWidget(row, 2, unit_combo)

        # Примечание
        self.hardware_table.setItem(row, 3, QTableWidgetItem(""))

    def remove_hardware(self):
        """Удалить выбранную фурнитуру"""
        current_row = self.hardware_table.currentRow()
        if current_row >= 0:
            self.hardware_table.removeRow(current_row)

    def load_hardware_materials(self, combo_box):
        """Загружает материалы группы HARDWARE в комбобокс"""
        db = DatabaseConnection()
        conn = db.get_connection()
        if not conn:
            return

        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, code FROM materials
                WHERE group_type = 'HARDWARE'
                ORDER BY name
            """)
            materials = cursor.fetchall()

            for material_id, name, code in materials:
                display_text = f"{name} ({code})" if code else name
                combo_box.addItem(display_text, material_id)

            cursor.close()
        except Exception as e:
            print(f"Ошибка загрузки материалов фурнитуры: {e}")
        finally:
            if conn:
                db.put_connection(conn)

    def add_variant(self):
        """Создать новый вариант модели"""
        if not self.model_id:
            QMessageBox.warning(self, "Внимание", "Сначала сохраните базовую модель")
            return

        # Находим ID базовой спецификации для этой модели
        base_specification_id = None
        conn = self.db.get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id FROM specifications
                    WHERE model_id = %s AND (is_default = true OR variant_name IS NULL OR variant_name = '')
                    LIMIT 1
                """, (self.model_id,))
                result = cursor.fetchone()
                if result:
                    base_specification_id = result[0]
                else:
                    pass
                cursor.close()
            except Exception as e:
                pass
            finally:
                self.db.put_connection(conn)

        if not base_specification_id:
            QMessageBox.warning(self, "Ошибка", "Не найдена базовая спецификация для этой модели")
            return

        # Используем ту же форму, но в режиме создания варианта
        dialog = ModelSpecificationFormV5(
            model_id=self.model_id,  # Передаем ID базовой модели!
            is_variant=True,  # Режим варианта
            parent=self
        )
        dialog.base_model_id = base_specification_id  # Ссылка на базовую спецификацию
        # Не нужно вызывать load_base_model_data здесь - это происходит автоматически в конструкторе
        dialog.setWindowTitle("Создание специфического варианта модели")
        dialog.saved.connect(self.load_variants)
        dialog.exec()

    def edit_variant(self):
        """Редактировать выбранный вариант"""
        current_row = self.variants_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Внимание", "Выберите вариант для редактирования")
            return

        variant_id = int(self.variants_table.item(current_row, 0).text())
        is_default = self.variants_table.item(current_row, 1).text() == "Базовый вариант"

        if is_default:
            # Базовый вариант редактируется в текущей форме
            QMessageBox.information(self, "Информация",
                "Базовый вариант редактируется в основных вкладках этой формы")
        else:
            # Специфический вариант - используем ту же форму с флагом is_variant=True
            print(f"🔧 V5: Открываем форму редактирования специфического варианта ID={variant_id}")
            dialog = ModelSpecificationFormV5(
                model_id=self.model_id,
                is_variant=True,
                parent=self
            )
            dialog.saved.connect(self.load_variants)
            dialog.exec()

    def view_variant(self):
        """Просмотр варианта"""
        current_row = self.variants_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Внимание", "Выберите вариант для просмотра")
            return

        variant_id = int(self.variants_table.item(current_row, 0).text())

        # Используем ту же форму для просмотра варианта
        print(f"🔧 V5: Открываем форму просмотра варианта ID={variant_id}")
        dialog = ModelSpecificationFormV5(
            model_id=self.model_id,
            is_variant=True,
            parent=self
        )
        dialog.exec()

    def remove_variant(self):
        """Удалить выбранный вариант"""
        current_row = self.variants_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Внимание", "Выберите вариант для удаления")
            return

        # Проверяем, не базовый ли это вариант
        is_default = self.variants_table.item(current_row, 1).text() == "Базовый вариант"
        if is_default:
            QMessageBox.warning(self, "Внимание", "Нельзя удалить базовый вариант модели")
            return

        variant_name = self.variants_table.item(current_row, 1).text()
        reply = QMessageBox.question(
            self,
            "Подтверждение",
            f"Удалить вариант '{variant_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            variant_id = int(self.variants_table.item(current_row, 0).text())

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
                finally:
                    # Обязательно возвращаем соединение в пул
                    if conn:
                        self.db.put_connection(conn)

    def load_variants(self):
        """Загрузка списка вариантов модели"""
        if not self.model_id:
            return

        conn = self.db.get_connection()
        if not conn:
            return

        try:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

            # Загружаем варианты модели
            cursor.execute("""
                SELECT s.id, s.variant_name, s.variant_code, s.is_default,
                       s.total_material_cost, s.is_active,
                       p.name as perforation_name,
                       l.name as lining_name
                FROM specifications s
                LEFT JOIN perforation_types p ON s.perforation_id = p.id
                LEFT JOIN lining_types l ON s.lining_id = l.id
                WHERE s.model_id = %s
                ORDER BY s.is_default DESC, s.created_at DESC
            """, (self.model_id,))

            variants = cursor.fetchall()

            self.variants_table.setRowCount(0)
            for variant in variants:
                row = self.variants_table.rowCount()
                self.variants_table.insertRow(row)

                # ID
                self.variants_table.setItem(row, 0, QTableWidgetItem(str(variant['id'])))

                # Название
                name = variant['variant_name'] or "Базовый вариант"
                self.variants_table.setItem(row, 1, QTableWidgetItem(name))

                # Код
                code = variant['variant_code'] or "-"
                self.variants_table.setItem(row, 2, QTableWidgetItem(code))

                # Перфорация
                perf = variant['perforation_name'] or "-"
                self.variants_table.setItem(row, 3, QTableWidgetItem(perf))

                # Подкладка
                lining = variant['lining_name'] or "-"
                self.variants_table.setItem(row, 4, QTableWidgetItem(lining))

                # Стоимость
                cost = f"{variant['total_material_cost']:.2f}" if variant['total_material_cost'] else "-"
                self.variants_table.setItem(row, 5, QTableWidgetItem(cost))

                # Активен
                active = "✓" if variant['is_active'] else "✗"
                self.variants_table.setItem(row, 6, QTableWidgetItem(active))

            cursor.close()

        except Exception as e:
            print(f"Ошибка загрузки вариантов: {e}")
        finally:
            # Обязательно возвращаем соединение в пул
            if conn:
                self.db.put_connection(conn)

    def load_model_data(self):
        """Загрузка данных модели для редактирования"""
        if not self.model_id:
            return

        conn = self.db.get_connection()
        if not conn:
            return

        try:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

            # Если редактируем вариант, основные данные модели уже загружены
            # Загружаем основные данные модели только для новых или базовых моделей
            if not self.specification_id:
                cursor.execute("""
                    SELECT * FROM models WHERE id = %s
                """, (self.model_id,))
                model = cursor.fetchone()

                if model:
                    # Заполняем основные поля
                    self.name_input.setText(model['name'] or '')
                    self.article_input.setText(model['article'] or '')
                    self.last_code_input.setText(model['last_code'] or '')

                    # Тип колодки
                    if model['last_type']:
                        index = self.last_type_combo.findText(model['last_type'])
                        if index >= 0:
                            self.last_type_combo.setCurrentIndex(index)

                    # Размерный ряд
                    if model['size_min']:
                        self.size_min_spin.setValue(model['size_min'])
                    if model['size_max']:
                        self.size_max_spin.setValue(model['size_max'])

                    # Тип затяжки
                    if model.get('lasting_type_id'):
                        index = self.lasting_combo.findData(model['lasting_type_id'])
                        if index >= 0:
                            self.lasting_combo.setCurrentIndex(index)

            # Загружаем данные из specifications (детали кроя, фурнитура и т.д.)
            if self.specification_id:
                # Для редактирования конкретной спецификации
                cursor.execute("""
                    SELECT * FROM specifications WHERE id = %s
                """, (self.specification_id,))
            else:
                # Для базовой модели ищем по умолчанию
                cursor.execute("""
                    SELECT * FROM specifications
                    WHERE model_id = %s AND is_default = true
                    ORDER BY created_at DESC
                    LIMIT 1
                """, (self.model_id,))
            spec = cursor.fetchone()

            if spec:
                # Загружаем детали кроя
                if spec.get('cutting_parts'):
                    self.cutting_table.setRowCount(0)
                    cutting_parts_data = spec['cutting_parts']

                    # Если это строка JSON, декодируем
                    if isinstance(cutting_parts_data, str):
                        try:
                            import json
                            cutting_parts_data = json.loads(cutting_parts_data)
                        except json.JSONDecodeError:
                            cutting_parts_data = []

                    for part in cutting_parts_data:
                        row = self.cutting_table.rowCount()
                        self.cutting_table.insertRow(row)

                        # Название детали как QTableWidgetItem (как в add_cutting_part_base)
                        item_name = QTableWidgetItem(part.get('name', ''))
                        # Если есть ID детали в справочнике, сохраняем его
                        if part.get('id'):
                            item_name.setData(Qt.ItemDataRole.UserRole, part['id'])
                        self.cutting_table.setItem(row, 0, item_name)

                        # Количество как SpinBox
                        qty_spin = QSpinBox()
                        qty_spin.setRange(1, 100)
                        qty_spin.setValue(part.get('quantity', 1))
                        self.cutting_table.setCellWidget(row, 1, qty_spin)

                        # Расход (дм²) как DoubleSpinBox
                        consumption_spin = QDoubleSpinBox()
                        consumption_spin.setRange(0.1, 999.9)
                        consumption_spin.setValue(part.get('consumption', 1.0))
                        consumption_spin.setDecimals(1)
                        consumption_spin.setSuffix(" дм²")
                        self.cutting_table.setCellWidget(row, 2, consumption_spin)

                        # Материал и примечание
                        self.cutting_table.setItem(row, 3, QTableWidgetItem(part.get('material', 'Кожа/Замша')))
                        self.cutting_table.setItem(row, 4, QTableWidgetItem(part.get('notes', '')))

                # Загружаем фурнитуру
                if spec.get('hardware'):
                    self.hardware_table.setRowCount(0)
                    for hw in spec['hardware']:
                        row = self.hardware_table.rowCount()
                        self.hardware_table.insertRow(row)

                        # Название фурнитуры
                        hw_combo = QComboBox()
                        hw_combo.addItems(["Люверсы", "Крючки", "Молния", "Пряжка", "Кнопки"])
                        hw_combo.setEditable(True)
                        hw_combo.setEditText(hw.get('name', ''))
                        self.hardware_table.setCellWidget(row, 0, hw_combo)

                        # Количество
                        qty_spin = QSpinBox()
                        qty_spin.setRange(1, 100)
                        qty_spin.setValue(hw.get('quantity', 1))
                        self.hardware_table.setCellWidget(row, 1, qty_spin)

                        # Единица
                        unit_combo = QComboBox()
                        unit_combo.addItems(["шт", "пара", "комплект", "м²", "дм2"])
                        if hw.get('unit'):
                            index = unit_combo.findText(hw['unit'])
                            if index >= 0:
                                unit_combo.setCurrentIndex(index)
                        self.hardware_table.setCellWidget(row, 2, unit_combo)

                        # Примечание
                        self.hardware_table.setItem(row, 3, QTableWidgetItem(hw.get('notes', '')))

                # Загружаем параметры перфорации и подкладки
                if self.is_variant:
                    # Для вариантов - используем одиночные поля
                    if spec.get('perforation_id'):
                        index = self.perforation_combo.findData(spec['perforation_id'])
                        if index >= 0:
                            self.perforation_combo.setCurrentIndex(index)

                    if spec.get('lining_id'):
                        index = self.lining_combo.findData(spec['lining_id'])
                        if index >= 0:
                            self.lining_combo.setCurrentIndex(index)
                else:
                    # Для базовых моделей - проверяем массивы параметров
                    # Загружаем перфорации из массива
                    perforation_ids = []
                    if spec.get('perforation_ids'):
                        try:
                            perforation_ids = json.loads(spec['perforation_ids']) if isinstance(spec['perforation_ids'], str) else spec['perforation_ids']
                        except (json.JSONDecodeError, TypeError):
                            perforation_ids = []

                    # Если массива нет, попробуем загрузить из одиночного поля (обратная совместимость)
                    if not perforation_ids and spec.get('perforation_id'):
                        perforation_ids = [spec['perforation_id']]

                    # Добавляем типы перфораций в таблицу
                    for perf_id in perforation_ids:
                        cursor.execute("""
                            SELECT id, name FROM perforation_types WHERE id = %s
                        """, (perf_id,))
                        perf_result = cursor.fetchone()
                        if perf_result:
                            row = self.perforation_table.rowCount()
                            self.perforation_table.insertRow(row)
                            item = QTableWidgetItem(perf_result['name'])
                            item.setData(Qt.ItemDataRole.UserRole, perf_result['id'])
                            self.perforation_table.setItem(row, 0, item)
                            self.perforation_table.setItem(row, 1, QTableWidgetItem(perf_result.get('description', '')))

                    # Загружаем подкладки из массива
                    lining_ids = []
                    if spec.get('lining_ids'):
                        try:
                            lining_ids = json.loads(spec['lining_ids']) if isinstance(spec['lining_ids'], str) else spec['lining_ids']
                        except (json.JSONDecodeError, TypeError):
                            lining_ids = []

                    # Если массива нет, попробуем загрузить из одиночного поля (обратная совместимость)
                    if not lining_ids and spec.get('lining_id'):
                        lining_ids = [spec['lining_id']]

                    # Добавляем типы подкладок в таблицу
                    for lining_id in lining_ids:
                        cursor.execute("""
                            SELECT id, name FROM lining_types WHERE id = %s
                        """, (lining_id,))
                        lining_result = cursor.fetchone()
                        if lining_result:
                            row = self.lining_table.rowCount()
                            self.lining_table.insertRow(row)
                            item = QTableWidgetItem(lining_result['name'])
                            item.setData(Qt.ItemDataRole.UserRole, lining_result['id'])
                            self.lining_table.setItem(row, 0, item)
                            self.lining_table.setItem(row, 1, QTableWidgetItem(lining_result.get('description', '')))

                # Загружаем тип затяжки (одинаково для вариантов и базовых моделей)
                if spec.get('lasting_type_id'):
                    index = self.lasting_combo.findData(spec['lasting_type_id'])
                    if index >= 0:
                        self.lasting_combo.setCurrentIndex(index)

                # Загружаем подошвы
                if spec.get('soles'):
                    self.soles_table.setRowCount(0)
                    try:
                        soles_data = json.loads(spec['soles']) if isinstance(spec['soles'], str) else spec['soles']
                        for sole in soles_data:
                            row = self.soles_table.rowCount()
                            self.soles_table.insertRow(row)

                            # Заполняем данные подошвы
                            material_item = QTableWidgetItem(sole.get('material', ''))
                            # Сохраняем ID материала если есть
                            if sole.get('material_id'):
                                material_item.setData(Qt.ItemDataRole.UserRole, sole['material_id'])

                            self.soles_table.setItem(row, 0, material_item)
                            self.soles_table.setItem(row, 1, QTableWidgetItem(str(sole.get('thickness', 0))))
                            self.soles_table.setItem(row, 2, QTableWidgetItem(sole.get('color', '')))
                            self.soles_table.setItem(row, 3, QTableWidgetItem(str(sole.get('heel_height', 0))))
                            self.soles_table.setItem(row, 4, QTableWidgetItem(str(sole.get('platform_height', 0))))

                    except (json.JSONDecodeError, TypeError) as e:
                        print(f"⚠️ Ошибка загрузки данных подошв: {e}")

            cursor.close()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки данных модели: {e}")
        finally:
            # Обязательно возвращаем соединение в пул
            if conn:
                self.db.put_connection(conn)

    def load_variant_for_editing(self, variant_id):
        """Загрузка данных конкретного варианта для редактирования"""
        conn = self.db.get_connection()
        if not conn:
            return

        try:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

            # Загружаем спецификацию варианта
            cursor.execute("""
                SELECT s.*, m.name as model_name, m.article as model_article,
                       m.id as actual_model_id, m.last_code, m.last_type,
                       m.size_min, m.size_max
                FROM specifications s
                JOIN models m ON s.model_id = m.id
                WHERE s.id = %s
            """, (variant_id,))

            variant = cursor.fetchone()
            if variant:
                from debug_logger import log_debug
                log_debug(f"🔍 НАЙДЕН ВАРИАНТ: ID={variant_id}, model_id={variant['actual_model_id']}, name={variant['variant_name']}")

                # Устанавливаем правильный model_id (ID базовой модели)
                self.model_id = variant['actual_model_id']
                log_debug(f"🔍 Обновлен model_id: {self.model_id}")

                # Заполняем основную информацию из модели
                self.name_input.setText(variant['model_name'] or '')
                self.article_input.setText(variant['model_article'] or '')
                self.last_code_input.setText(variant['last_code'] or '')

                # Тип колодки
                if variant['last_type']:
                    index = self.last_type_combo.findText(variant['last_type'])
                    if index >= 0:
                        self.last_type_combo.setCurrentIndex(index)

                # Размерный ряд
                if variant['size_min']:
                    self.size_min_spin.setValue(variant['size_min'])
                if variant['size_max']:
                    self.size_max_spin.setValue(variant['size_max'])

                # Заполняем поля варианта
                if hasattr(self, 'variant_name_input'):
                    self.variant_name_input.setText(variant['variant_name'] or '')
                if hasattr(self, 'variant_article_input'):
                    self.variant_article_input.setText(variant['variant_code'] or '')

                log_debug(f"🔄 Загружаем вариант ID={variant_id} для модели ID={self.model_id}")

                # ВАЖНО: Загружаем данные спецификации варианта (фурнитура, детали кроя, подошвы)
                log_debug(f"🔧 РЕДАКТИРОВАНИЕ ВАРИАНТА: загружаем спецификацию ID={variant_id}")

                # Сначала загружаем справочные данные для комбобоксов
                if not hasattr(self, 'hardware_list') or not self.hardware_list:
                    log_debug("🔄 Загружаем reference data для редактирования варианта")
                    self.load_reference_data()

                # ВАЖНО: Заполняем комбобоксы перфорации и подкладки для вариантов
                log_debug("🎨 Заполняем комбобоксы перфорации и подкладки для существующего варианта")

                # Очищаем комбобоксы
                self.perforation_combo.clear()
                self.lining_combo.clear()

                self.perforation_combo.addItem("Не выбрано", None)
                self.lining_combo.addItem("Не выбрано", None)

                # Заполняем ВСЕ доступные варианты
                if hasattr(self, 'perforation_types'):
                    log_debug(f"🎨 Заполняем перфорацию: {len(self.perforation_types)} типов")
                    for perf_type in self.perforation_types:
                        self.perforation_combo.addItem(perf_type['name'], perf_type['id'])
                        log_debug(f"  + {perf_type['name']} (ID={perf_type['id']})")

                if hasattr(self, 'lining_types'):
                    log_debug(f"🎨 Заполняем подкладку: {len(self.lining_types)} типов")
                    for lining_type in self.lining_types:
                        self.lining_combo.addItem(lining_type['name'], lining_type['id'])
                        log_debug(f"  + {lining_type['name']} (ID={lining_type['id']})")

                log_debug(f"✅ Combo boxes заполнены для варианта: перфорация={self.perforation_combo.count()}, подкладка={self.lining_combo.count()}")
                log_debug(f"✅ Комбобоксы включены: перфорация={self.perforation_combo.isEnabled()}, подкладка={self.lining_combo.isEnabled()}")

                # Теперь загружаем данные спецификации
                self.load_specification_data(variant)
                log_debug(f"✅ Спецификация варианта ID={variant_id} загружена")

                # Настраиваем видимость полей для режима варианта
                self.setup_field_visibility()

            cursor.close()
        except Exception as e:
            print(f"❌ Ошибка загрузки варианта: {e}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки варианта: {e}")
        finally:
            if conn:
                self.db.put_connection(conn)

    def load_base_model_data(self, base_model_id):
        """Загрузка данных базовой модели для создания нового варианта"""
        from debug_logger import log_debug

        log_debug(f"🔧 load_base_model_data вызван с base_model_id={base_model_id}")

        conn = self.db.get_connection()
        if not conn:
            return

        try:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

            # Загружаем данные базовой модели
            cursor.execute("""
                SELECT * FROM models WHERE id = %s
            """, (base_model_id,))
            model = cursor.fetchone()

            if model:
                # ВАЖНО: сохраняем model_id для использования при сохранении
                self.model_id = base_model_id

                # Заполняем основную информацию из модели
                self.name_input.setText(model['name'] or '')
                self.article_input.setText(model['article'] or '')
                self.last_code_input.setText(model['last_code'] or '')

                # Тип колодки
                if model['last_type']:
                    index = self.last_type_combo.findText(model['last_type'])
                    if index >= 0:
                        self.last_type_combo.setCurrentIndex(index)

                # Размерный ряд
                if model['size_min']:
                    self.size_min_spin.setValue(model['size_min'])
                if model['size_max']:
                    self.size_max_spin.setValue(model['size_max'])

                log_debug(f"🔄 Загружаем данные базовой модели ID={base_model_id} для нового варианта")
                log_debug(f"✅ model_id установлен: {self.model_id}")

                # Загружаем базовую спецификацию модели
                cursor.execute("""
                    SELECT * FROM specifications
                    WHERE model_id = %s AND is_default = true
                    ORDER BY created_at DESC
                    LIMIT 1
                """, (base_model_id,))

                base_spec = cursor.fetchone()
                if base_spec:
                    log_debug(f"✅ Найдена базовая спецификация ID={base_spec['id']}")

                    # Для вариантов СНАЧАЛА заполняем combo boxes всеми доступными опциями
                    if self.is_variant:
                        log_debug("🔧 Заполняем combo boxes для варианта перед загрузкой спецификации")

                        # Убедимся что у нас есть reference data
                        if not hasattr(self, 'perforation_types') or not self.perforation_types:
                            log_debug("🔄 Загружаем reference data для combo boxes")
                            self.load_reference_data()

                        # Очищаем комбобоксы
                        self.perforation_combo.clear()
                        self.lining_combo.clear()

                        self.perforation_combo.addItem("Не выбрано", None)
                        self.lining_combo.addItem("Не выбрано", None)

                        # Заполняем ВСЕ доступные варианты
                        if hasattr(self, 'perforation_types'):
                            log_debug(f"🎨 Заполняем перфорацию: {len(self.perforation_types)} типов")
                            for perf_type in self.perforation_types:
                                self.perforation_combo.addItem(perf_type['name'], perf_type['id'])
                                log_debug(f"  + {perf_type['name']} (ID={perf_type['id']})")

                        if hasattr(self, 'lining_types'):
                            log_debug(f"🎨 Заполняем подкладку: {len(self.lining_types)} типов")
                            for lining_type in self.lining_types:
                                self.lining_combo.addItem(lining_type['name'], lining_type['id'])
                                log_debug(f"  + {lining_type['name']} (ID={lining_type['id']})")

                        log_debug(f"✅ Combo boxes заполнены: перфорация={self.perforation_combo.count()}, подкладка={self.lining_combo.count()}")
                        log_debug(f"✅ Комбобоксы включены: перфорация={self.perforation_combo.isEnabled()}, подкладка={self.lining_combo.isEnabled()}")

                    # Теперь загружаем данные из базовой спецификации
                    self.load_specification_data(base_spec)
                else:
                    log_debug(f"⚠️ Базовая спецификация для модели ID={base_model_id} не найдена")

            cursor.close()

            # Финальная проверка
            log_debug(f"🏁 После загрузки базовой модели: self.model_id={self.model_id}")

            # Настраиваем поля варианта после загрузки данных базовой модели
            self.setup_field_visibility()

        except Exception as e:
            print(f"❌ Ошибка загрузки базовой модели: {e}")
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки базовой модели: {e}")
        finally:
            if conn:
                self.db.put_connection(conn)

    def load_specification_data(self, spec):
        """Загрузка данных спецификации (общий метод)"""
        from debug_logger import log_debug

        if not spec:
            log_debug("⚠️ Спецификация пуста")
            return

        log_debug(f"📋 Загружаем спецификацию ID={spec.get('id', 'Unknown')}, variant_name={spec.get('variant_name', 'Unknown')}")

        # Загружаем детали кроя
        if spec.get('cutting_parts'):
            cutting_parts_data = spec['cutting_parts']
            print(f"🔧 Найдены детали кроя: {type(cutting_parts_data)}")

            self.cutting_table.setRowCount(0)

            # Если это строка JSON, декодируем
            if isinstance(cutting_parts_data, str):
                try:
                    import json
                    cutting_parts_data = json.loads(cutting_parts_data)
                except json.JSONDecodeError:
                    cutting_parts_data = []

            for part in cutting_parts_data:
                row = self.cutting_table.rowCount()
                self.cutting_table.insertRow(row)

                # Название детали как QTableWidgetItem
                item_name = QTableWidgetItem(part.get('name', ''))
                if part.get('id'):
                    item_name.setData(Qt.ItemDataRole.UserRole, part['id'])
                self.cutting_table.setItem(row, 0, item_name)

                # Количество как SpinBox
                qty_spin = QSpinBox()
                qty_spin.setRange(1, 100)
                qty_spin.setValue(part.get('quantity', 1))
                self.cutting_table.setCellWidget(row, 1, qty_spin)

                # Расход (дм²) как DoubleSpinBox
                consumption_spin = QDoubleSpinBox()
                consumption_spin.setRange(0.1, 999.9)
                consumption_spin.setValue(part.get('consumption', 1.0))
                consumption_spin.setDecimals(1)
                consumption_spin.setSuffix(" дм²")
                self.cutting_table.setCellWidget(row, 2, consumption_spin)

                # Материал и примечание
                self.cutting_table.setItem(row, 3, QTableWidgetItem(part.get('material', 'Кожа/Замша')))
                self.cutting_table.setItem(row, 4, QTableWidgetItem(part.get('notes', '')))
        else:
            print("⚠️ Детали кроя отсутствуют в спецификации")

        # Загружаем фурнитуру
        if spec.get('hardware'):
            from debug_logger import log_debug
            log_debug("🔧 Загружаем фурнитуру для варианта")

            # Для вариантов убедимся, что hardware_list заполнен
            if self.is_variant and (not hasattr(self, 'hardware_list') or not self.hardware_list):
                log_debug("🔄 Загружаем hardware_list для варианта")
                self.load_reference_data()

            self.hardware_table.setRowCount(0)
            hardware_data = spec['hardware']
            if isinstance(hardware_data, str):
                try:
                    import json
                    hardware_data = json.loads(hardware_data)
                except json.JSONDecodeError:
                    hardware_data = []

            log_debug(f"🔧 Найдено фурнитуры в спецификации: {len(hardware_data)} шт.")
            log_debug(f"🔧 В hardware_list доступно: {len(getattr(self, 'hardware_list', []))} вариантов")
            log_debug(f"🔧 Фурнитура варианта: {[hw.get('name', hw.get('material_name', 'Unknown')) for hw in hardware_data]}")

            for hw in hardware_data:
                row = self.hardware_table.rowCount()
                self.hardware_table.insertRow(row)

                # Фурнитура как ComboBox
                hw_combo = QComboBox()
                hw_combo.addItem("Выберите фурнитуру")
                for hardware_item in getattr(self, 'hardware_list', []):
                    hw_combo.addItem(f"{hardware_item['name']} ({hardware_item['code']})", hardware_item['id'])

                # Устанавливаем текущий элемент если найден
                current_text = hw.get('name', '')
                log_debug(f"🔧 Ищем фурнитуру '{current_text}' в комбобоксе с {hw_combo.count()} элементами")
                index = hw_combo.findText(current_text, Qt.MatchFlag.MatchContains)
                if index >= 0:
                    hw_combo.setCurrentIndex(index)
                    log_debug(f"✅ Установлена фурнитура '{current_text}' на index={index}")
                else:
                    log_debug(f"❌ Фурнитура '{current_text}' НЕ НАЙДЕНА в комбобоксе")
                    for i in range(hw_combo.count()):
                        log_debug(f"  [{i}] {hw_combo.itemText(i)}")

                self.hardware_table.setCellWidget(row, 0, hw_combo)

                # Количество
                qty_spin = QSpinBox()
                qty_spin.setRange(1, 100)
                qty_spin.setValue(hw.get('quantity', 1))
                self.hardware_table.setCellWidget(row, 1, qty_spin)

                # Единица измерения
                unit_combo = QComboBox()
                unit_combo.addItems(["шт", "пара", "м", "см"])
                unit_text = hw.get('unit', 'шт')
                unit_index = unit_combo.findText(unit_text)
                if unit_index >= 0:
                    unit_combo.setCurrentIndex(unit_index)
                self.hardware_table.setCellWidget(row, 2, unit_combo)

                # Примечание
                self.hardware_table.setItem(row, 3, QTableWidgetItem(hw.get('notes', '')))

        # Загружаем подошвы
        if spec.get('soles'):
            soles_data = spec['soles']
            if isinstance(soles_data, str):
                try:
                    import json
                    soles_data = json.loads(soles_data)
                except (json.JSONDecodeError, TypeError):
                    soles_data = []

            if soles_data:
                self.soles_table.setRowCount(0)
                for sole in soles_data:
                    row = self.soles_table.rowCount()
                    self.soles_table.insertRow(row)

                    material_item = QTableWidgetItem(sole.get('material', ''))
                    if sole.get('material_id'):
                        material_item.setData(Qt.ItemDataRole.UserRole, sole['material_id'])

                    self.soles_table.setItem(row, 0, material_item)
                    self.soles_table.setItem(row, 1, QTableWidgetItem(str(sole.get('thickness', 0))))
                    self.soles_table.setItem(row, 2, QTableWidgetItem(sole.get('color', '')))
                    self.soles_table.setItem(row, 3, QTableWidgetItem(str(sole.get('heel_height', 0))))
                    self.soles_table.setItem(row, 4, QTableWidgetItem(str(sole.get('platform_height', 0))))

        # Загружаем данные перфорации и подкладки
        from debug_logger import log_debug

        # Для варианта устанавливаем одиночные значения в комбобоксы
        if self.is_variant:
            log_debug("🎨 Загружаем перфорацию и подкладку для варианта")

            # Сначала проверяем одиночные значения (для редактирования существующего варианта)
            if spec.get('perforation_id'):
                perforation_id = spec['perforation_id']
                log_debug(f"🎨 Найдена перфорация ID={perforation_id}")
                index = self.perforation_combo.findData(perforation_id)
                if index >= 0:
                    self.perforation_combo.setCurrentIndex(index)
                    log_debug(f"✅ Установлена перфорация index={index}")
            # Если нет одиночного значения, берем первый элемент из массива (для нового варианта)
            elif spec.get('perforation_ids'):
                try:
                    perforation_ids = spec['perforation_ids']
                    if isinstance(perforation_ids, str):
                        import json
                        perforation_ids = json.loads(perforation_ids)
                    if perforation_ids and len(perforation_ids) > 0:
                        first_perforation = perforation_ids[0]
                        log_debug(f"🎨 Устанавливаем первую перфорацию из массива ID={first_perforation}")
                        log_debug(f"🔍 В комбобоксе перфорации {self.perforation_combo.count()} элементов")
                        index = self.perforation_combo.findData(first_perforation)
                        if index >= 0:
                            self.perforation_combo.setCurrentIndex(index)
                            log_debug(f"✅ Установлена перфорация из массива index={index}")
                        else:
                            log_debug(f"❌ Перфорация ID={first_perforation} НЕ НАЙДЕНА в комбобоксе")
                            # Выведем все элементы комбобокса
                            for i in range(self.perforation_combo.count()):
                                item_data = self.perforation_combo.itemData(i)
                                item_text = self.perforation_combo.itemText(i)
                                log_debug(f"  [{i}] {item_text} = {item_data}")
                except Exception as e:
                    log_debug(f"❌ Ошибка обработки массива перфораций: {e}")

            # Подкладка - аналогично
            if spec.get('lining_id'):
                lining_id = spec['lining_id']
                log_debug(f"🎨 Найдена подкладка ID={lining_id}")
                index = self.lining_combo.findData(lining_id)
                if index >= 0:
                    self.lining_combo.setCurrentIndex(index)
                    log_debug(f"✅ Установлена подкладка index={index}")
            elif spec.get('lining_ids'):
                try:
                    lining_ids = spec['lining_ids']
                    if isinstance(lining_ids, str):
                        import json
                        lining_ids = json.loads(lining_ids)
                    if lining_ids and len(lining_ids) > 0:
                        first_lining = lining_ids[0]
                        log_debug(f"🎨 Устанавливаем первую подкладку из массива ID={first_lining}")
                        log_debug(f"🔍 В комбобоксе подкладки {self.lining_combo.count()} элементов")
                        index = self.lining_combo.findData(first_lining)
                        if index >= 0:
                            self.lining_combo.setCurrentIndex(index)
                            log_debug(f"✅ Установлена подкладка из массива index={index}")
                        else:
                            log_debug(f"❌ Подкладка ID={first_lining} НЕ НАЙДЕНА в комбобоксе")
                            # Выведем все элементы комбобокса
                            for i in range(self.lining_combo.count()):
                                item_data = self.lining_combo.itemData(i)
                                item_text = self.lining_combo.itemText(i)
                                log_debug(f"  [{i}] {item_text} = {item_data}")
                except Exception as e:
                    log_debug(f"❌ Ошибка обработки массива подкладок: {e}")

            # Тип затяжки
            if spec.get('lasting_type_id'):
                lasting_id = spec['lasting_type_id']
                log_debug(f"🎨 Найден тип затяжки ID={lasting_id}")
                index = self.lasting_combo.findData(lasting_id)
                if index >= 0:
                    self.lasting_combo.setCurrentIndex(index)
                    log_debug(f"✅ Установлен тип затяжки index={index}")
                else:
                    log_debug(f"⚠️ Тип затяжки ID={lasting_id} не найден в комбобоксе")

        else:
            # Для базовой модели загружаем массивы в таблицы (старая логика)
            log_debug("🎨 Загружаем перфорации и подкладки для базовой модели в таблицы")
            # Здесь можно добавить загрузку в таблицы если нужно

    def save_model(self):
        """Сохранение модели"""
        from debug_logger import log_debug

        log_debug(f"💾 Начинаем сохранение: is_variant={self.is_variant}, model_id={self.model_id}, specification_id={self.specification_id}")

        conn = self.db.get_connection()
        if not conn:
            return

        try:
            cursor = conn.cursor()

            if self.is_variant:
                # Для варианта создаем только спецификацию, модель уже существует
                log_debug(f"💾 Обрабатываем сохранение варианта: model_id={self.model_id}, specification_id={self.specification_id}")

                if not self.model_id:
                    log_debug(f"❌ Ошибка: model_id отсутствует")
                    QMessageBox.warning(self, "Ошибка", f"Не указана базовая модель. model_id={self.model_id}, specification_id={self.specification_id}")
                    return

                log_debug(f"💾 Сохраняем вариант для модели ID={self.model_id} (specification_id={self.specification_id})")

            else:
                # Для базовой модели проверяем обязательные поля
                if not self.name_input.text():
                    QMessageBox.warning(self, "Внимание", "Укажите название модели")
                    return

                # Сохраняем основные данные модели
                if self.model_id:
                    # Обновляем существующую модель
                    cursor.execute("""
                        UPDATE models
                        SET name = %s, article = %s, last_code = %s,
                            last_type = %s, size_min = %s, size_max = %s,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE id = %s
                    """, (
                        self.name_input.text(),
                        self.article_input.text(),
                        self.last_code_input.text(),
                        self.last_type_combo.currentText(),
                        self.size_min_spin.value(),
                        self.size_max_spin.value(),
                        self.model_id
                    ))
                else:
                    # Создаем новую модель с UUID
                    import uuid
                    cursor.execute("""
                        INSERT INTO models (uuid, name, article, last_code, last_type,
                                          size_min, size_max, model_type, gender,
                                          created_at, updated_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s,
                                CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                        RETURNING id
                    """, (
                        str(uuid.uuid4()),  # Генерируем UUID
                        self.name_input.text(),
                        self.article_input.text(),
                        self.last_code_input.text(),
                        self.last_type_combo.currentText(),
                        self.size_min_spin.value(),
                        self.size_max_spin.value(),
                        "Кроссовки",  # Тип по умолчанию
                        "Мужская"    # Пол по умолчанию
                    ))

                    result = cursor.fetchone()
                    if result:
                        self.model_id = result[0]

            # Сохраняем параметры в спецификацию
            if self.model_id:
                if self.is_variant:
                    if self.specification_id:
                        # Редактируем существующую спецификацию варианта
                        spec_id = self.specification_id
                        print(f"✅ Обновляем существующую спецификацию варианта ID={spec_id}")
                    else:
                        # Создаем новую спецификацию варианта
                        log_debug(f"💾 Создаем новую спецификацию для варианта")

                        import uuid
                        variant_name = getattr(self, 'variant_name_input', None)
                        variant_code = getattr(self, 'variant_article_input', None)

                        log_debug(f"💾 variant_name_input: {variant_name}, variant_code_input: {variant_code}")

                        cursor.execute("""
                            INSERT INTO specifications (uuid, model_id, is_default, is_active,
                                                       variant_name, variant_code, materials,
                                                       created_at, updated_at)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                            RETURNING id
                        """, (
                            str(uuid.uuid4()),
                            self.model_id,
                            False,  # Не базовая
                            True,   # Активная
                            variant_name.text() if variant_name else f"{self.name_input.text()} - Вариант",
                            variant_code.text() if variant_code else "VAR-001",
                            '{}'    # Пустой JSON для материалов
                        ))

                        spec_result = cursor.fetchone()
                        spec_id = spec_result[0] if spec_result else None
                        log_debug(f"✅ Создана новая спецификация для варианта ID={spec_id}")

                else:
                    # Для базовой модели получаем существующую или создаем спецификацию
                    cursor.execute("""
                        SELECT id FROM specifications
                        WHERE model_id = %s AND is_default = true
                        ORDER BY created_at ASC
                        LIMIT 1
                    """, (self.model_id,))

                    spec_result = cursor.fetchone()

                    if spec_result:
                        spec_id = spec_result[0]
                    else:
                        # Создаем базовую спецификацию если ее нет
                        import uuid
                        cursor.execute("""
                            INSERT INTO specifications (uuid, model_id, is_default, is_active, materials,
                                                       created_at, updated_at)
                            VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                            RETURNING id
                        """, (
                            str(uuid.uuid4()),
                            self.model_id,
                            True,   # Базовая
                            True,   # Активная
                            '{}'    # Пустой JSON для материалов
                        ))

                        spec_result = cursor.fetchone()
                        spec_id = spec_result[0] if spec_result else None

                if spec_id:
                    # Определяем параметры для сохранения
                    if self.is_variant:
                        # Для специфического варианта - одиночные значения в старых полях
                        perforation_id = self.perforation_combo.currentData()
                        lining_id = self.lining_combo.currentData()
                        log_debug(f"💾 Сохраняем параметры варианта: perforation_id={perforation_id}, lining_id={lining_id}")
                        perforation_ids = None
                        lining_ids = None
                    else:
                        # Для базовой модели - собираем все выбранные элементы в массивы
                        perforation_id = None
                        lining_id = None

                        # Собираем все ID перфораций из таблицы
                        perforation_ids = []
                        for row in range(self.perforation_table.rowCount()):
                            item = self.perforation_table.item(row, 0)
                            if item:
                                perf_id = item.data(Qt.ItemDataRole.UserRole)
                                if perf_id:
                                    perforation_ids.append(perf_id)

                        # Собираем все ID подкладок из таблицы
                        lining_ids = []
                        for row in range(self.lining_table.rowCount()):
                            item = self.lining_table.item(row, 0)
                            if item:
                                lining_id_item = item.data(Qt.ItemDataRole.UserRole)
                                if lining_id_item:
                                    lining_ids.append(lining_id_item)

                    # Получаем тип затяжки (одинаково для вариантов и базовых моделей)
                    lasting_type_id = self.lasting_combo.currentData()

                    # Собираем данные элементов раскроя из таблицы
                    cutting_parts_data = []
                    for row in range(self.cutting_table.rowCount()):
                        part_item = self.cutting_table.item(row, 0)
                        if part_item:
                            # Получаем количество
                            qty_widget = self.cutting_table.cellWidget(row, 1)
                            quantity = qty_widget.value() if qty_widget else 1

                            # Получаем расход (дм²)
                            consumption_widget = self.cutting_table.cellWidget(row, 2)
                            consumption = consumption_widget.value() if consumption_widget else 1.0

                            # Получаем материал
                            material_widget = self.cutting_table.cellWidget(row, 3)
                            material_text = self.cutting_table.item(row, 3)
                            if material_widget and hasattr(material_widget, 'currentText'):
                                material = material_widget.currentText()
                            elif material_text:
                                material = material_text.text()
                            else:
                                material = "Кожа/Замша"

                            # Получаем примечание
                            notes_item = self.cutting_table.item(row, 4)
                            notes = notes_item.text() if notes_item else ""

                            cutting_part = {
                                'name': part_item.text(),
                                'quantity': quantity,
                                'consumption': consumption,
                                'material': material,
                                'notes': notes
                            }
                            cutting_parts_data.append(cutting_part)

                    # Собираем данные фурнитуры из таблицы
                    hardware_data = []
                    log_debug(f"💾 Собираем фурнитуру из таблицы: {self.hardware_table.rowCount()} строк")

                    for row in range(self.hardware_table.rowCount()):
                        hw_widget = self.hardware_table.cellWidget(row, 0)
                        qty_widget = self.hardware_table.cellWidget(row, 1)
                        unit_widget = self.hardware_table.cellWidget(row, 2)
                        notes_item = self.hardware_table.item(row, 3)

                        log_debug(f"💾 Строка {row}: hw_widget={hw_widget is not None}, qty_widget={qty_widget is not None}, unit_widget={unit_widget is not None}")

                        if hw_widget:
                            hw_name = hw_widget.currentText() if hasattr(hw_widget, 'currentText') else str(hw_widget)
                            hw_quantity = qty_widget.value() if qty_widget else 1
                            hw_unit = unit_widget.currentText() if unit_widget else 'шт'
                            hw_notes = notes_item.text() if notes_item else ''

                            log_debug(f"💾 Фурнитура [{row}]: {hw_name}, кол-во: {hw_quantity}, единица: {hw_unit}, примечание: '{hw_notes}'")

                            hardware_item = {
                                'name': hw_name,
                                'quantity': hw_quantity,
                                'unit': hw_unit,
                                'notes': hw_notes
                            }
                            hardware_data.append(hardware_item)
                        else:
                            log_debug(f"💾 Строка {row}: hw_widget отсутствует, пропускаем")

                    # Собираем данные подошв из таблицы
                    soles_data = []
                    for row in range(self.soles_table.rowCount()):
                        material_item = self.soles_table.item(row, 0)
                        sole_item = {
                            'material': material_item.text() if material_item else '',
                            'material_id': material_item.data(Qt.ItemDataRole.UserRole) if material_item else None,
                            'thickness': float(self.soles_table.item(row, 1).text()) if self.soles_table.item(row, 1) and self.soles_table.item(row, 1).text() else 0,
                            'color': self.soles_table.item(row, 2).text() if self.soles_table.item(row, 2) else '',
                            'heel_height': float(self.soles_table.item(row, 3).text()) if self.soles_table.item(row, 3) and self.soles_table.item(row, 3).text() else 0,
                            'platform_height': float(self.soles_table.item(row, 4).text()) if self.soles_table.item(row, 4) and self.soles_table.item(row, 4).text() else 0
                        }
                        soles_data.append(sole_item)

                    # Обновляем спецификацию с параметрами
                    log_debug(f"💾 Выполняем UPDATE спецификации ID={spec_id}")
                    log_debug(f"💾 Фурнитура для сохранения: {len(hardware_data)} элементов")

                    cursor.execute("""
                        UPDATE specifications
                        SET perforation_id = %s, lining_id = %s,
                            perforation_ids = %s, lining_ids = %s,
                            lasting_type_id = %s, soles = %s,
                            cutting_parts = %s, hardware = %s,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE id = %s
                    """, (perforation_id, lining_id,
                          json.dumps(perforation_ids) if perforation_ids else None,
                          json.dumps(lining_ids) if lining_ids else None,
                          lasting_type_id,
                          json.dumps(soles_data) if soles_data else None,
                          json.dumps(cutting_parts_data) if cutting_parts_data else None,
                          json.dumps(hardware_data) if hardware_data else None,
                          spec_id))

                    log_debug(f"✓ Сохранены параметры:")
                    log_debug(f"  Вариант: perforation_id={perforation_id}, lining_id={lining_id}")
                    log_debug(f"  Базовая модель: perforation_ids={perforation_ids}, lining_ids={lining_ids}")
                    log_debug(f"  Тип затяжки: lasting_type_id={lasting_type_id}")
                    log_debug(f"  Подошвы: {len(soles_data)} шт.")
                    log_debug(f"  Элементы раскроя: {len(cutting_parts_data)} шт.")
                    log_debug(f"  Фурнитура: {len(hardware_data)} шт.")

                else:
                    print("⚠️ Спецификация не найдена для модели")

            cursor.close()
            conn.commit()

            QMessageBox.information(self, "Успех", "Модель успешно сохранена")
            self.saved.emit()
            self.accept()

        except Exception as e:
            log_debug(f"❌ Ошибка при сохранении: {e}")
            log_debug(f"❌ Тип ошибки: {type(e).__name__}")
            import traceback
            log_debug(f"❌ Трейсбек: {traceback.format_exc()}")
            conn.rollback()
            QMessageBox.critical(self, "Ошибка", f"Ошибка сохранения: {e}")
        finally:
            # Обязательно возвращаем соединение в пул
            if conn:
                self.db.put_connection(conn)