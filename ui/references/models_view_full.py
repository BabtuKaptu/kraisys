"""Full models reference view with all DB fields"""
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QDoubleValidator, QIntValidator
from ui.base.base_table_v2 import BaseTableWidgetV2
from ui.base.base_form import BaseFormDialog
from ui.references.model_components_dialog_v2 import ModelComponentsDialogV2 as ModelComponentsDialog
from database.connection import DatabaseConnection
import psycopg2
import psycopg2.extras
import json

class ModelsTableFullWidget(BaseTableWidgetV2):
    """Полная таблица моделей обуви со всеми полями БД"""

    def __init__(self, parent=None):
        super().__init__('models', parent)
        self.setWindowTitle("Модели обуви - Полная версия")
        self.db = DatabaseConnection()

    def setup_ui(self):
        """Переопределяем метод настройки UI для добавления кнопки вариантов"""
        # Вызываем родительский метод
        super().setup_ui()

        # Теперь добавляем кнопку вариантов
        # Находим layout панели инструментов
        main_layout = self.layout()
        if main_layout and main_layout.count() > 0:
            # Первый элемент - это панель инструментов
            toolbar_layout = main_layout.itemAt(0).layout()
            if toolbar_layout:
                # Добавляем кнопку для просмотра вариантов
                self.variants_btn = QPushButton("📋 Варианты")
                self.variants_btn.clicked.connect(self.show_variants)
                # Вставляем кнопку после кнопки "Удалить"
                toolbar_layout.insertWidget(4, self.variants_btn)

    def get_search_columns(self):
        """Колонки для поиска"""
        return ['article', 'name', 'category', 'collection', 'season']

    def add_record(self):
        from ui.references.model_variant_dialog import ModelVariantTypeDialog
        from ui.references.model_specification_form_v5 import ModelSpecificationFormV5
        from ui.references.model_specific_variant_form import ModelSpecificVariantForm

        # Сначала спрашиваем тип модели
        type_dialog = ModelVariantTypeDialog(self)
        if type_dialog.exec():
            variant_type = type_dialog.get_variant_type()

            if variant_type == "free":
                # Создаем базовую модель (свободный вариант)
                dialog = ModelSpecificationFormV5(is_variant=False, parent=self)
                dialog.saved.connect(self.refresh_data)
                dialog.exec()
            else:
                # Для специфического варианта используем специализированную форму
                model_id = self.select_base_model()
                if model_id:
                    dialog = ModelSpecificVariantForm(parent=self, db=self.db, model_id=model_id)
                    dialog.saved.connect(self.refresh_data)
                    dialog.exec()

    def select_base_model(self):
        """Диалог выбора базовой модели для создания специфического варианта"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

            # Получаем список всех моделей
            cursor.execute("""
                SELECT id, article, name, last_code
                FROM models
                ORDER BY article
            """)

            models = cursor.fetchall()
            cursor.close()
            self.db.put_connection(conn)

            if not models:
                QMessageBox.warning(self, "Внимание", "Нет доступных базовых моделей")
                return None

            # Создаем список для выбора
            items = []
            model_ids = []
            for model in models:
                items.append(f"{model['article']} - {model['name']} (Колодка: {model['last_code']})")
                model_ids.append(model['id'])

            # Показываем диалог выбора
            item, ok = QInputDialog.getItem(
                self,
                "Выбор базовой модели",
                "Выберите базовую модель для создания специфического варианта:",
                items,
                0,
                False
            )

            if ok and item:
                index = items.index(item)
                return model_ids[index]

            return None

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить модели: {e}")
            return None

    def edit_record(self):
        record_id = self.get_current_record_id()
        if record_id:
            from ui.references.model_specification_form_v5 import ModelSpecificationFormV5
            # При редактировании определяем тип модели по наличию данных варианта
            # TODO: определить is_variant на основе данных из БД
            dialog = ModelSpecificationFormV5(model_id=record_id, is_variant=False, parent=self)
            dialog.saved.connect(self.refresh_data)
            dialog.exec()

    def show_variants(self):
        """Показать варианты выбранной модели"""
        record_id = self.get_current_record_id()
        if not record_id:
            QMessageBox.warning(self, "Внимание", "Выберите модель для просмотра вариантов")
            return

        from ui.references.variants_list_dialog import VariantsListDialog
        dialog = VariantsListDialog(model_id=record_id, db=self.db, parent=self)
        dialog.exec()


class ModelFullFormDialog(BaseFormDialog):
    """Полная форма редактирования модели со всеми полями"""

    def __init__(self, title: str, parent=None):
        self.record_id = None
        self.db = DatabaseConnection()
        super().__init__(title, parent)
        self.resize(1200, 800)

    def create_form_content(self):
        # Главный layout с прокруткой
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        scroll.setWidget(content)
        self.layout.addWidget(scroll)

        # Табы для группировки полей
        self.tabs = QTabWidget()
        layout = QVBoxLayout(content)
        layout.addWidget(self.tabs)

        # Создаем все вкладки
        self.create_main_tab()
        self.create_characteristics_tab()
        self.create_materials_tab()
        self.create_pricing_tab()
        self.create_production_tab()
        self.create_components_tab()
        self.create_additional_tab()

    def create_main_tab(self):
        """Основные данные"""
        tab = QWidget()
        layout = QFormLayout(tab)

        # Артикул и название
        self.article_input = QLineEdit()
        self.article_input.setMaxLength(50)
        self.name_input = QLineEdit()
        self.name_input.setMaxLength(200)

        layout.addRow("Артикул*:", self.article_input)
        layout.addRow("Название*:", self.name_input)

        # Пол и категория
        self.gender_combo = QComboBox()
        self.gender_combo.addItems(["", "Мужская", "Женская", "Унисекс", "Детская"])

        self.model_type_input = QLineEdit()
        self.model_type_input.setPlaceholderText("Ботинки, Туфли, Кроссовки...")

        self.category_input = QLineEdit()
        self.category_input.setPlaceholderText("Повседневная, Спортивная, Классическая...")

        layout.addRow("Пол:", self.gender_combo)
        layout.addRow("Тип модели:", self.model_type_input)
        layout.addRow("Категория:", self.category_input)

        # Коллекция и сезон
        self.collection_input = QLineEdit()
        self.collection_input.setPlaceholderText("Весна-Лето 2024...")

        self.season_combo = QComboBox()
        self.season_combo.addItems(["", "Весна-Лето", "Осень-Зима", "Демисезон", "Всесезон"])

        layout.addRow("Коллекция:", self.collection_input)
        layout.addRow("Сезон:", self.season_combo)

        # Размерный ряд
        size_group = QGroupBox("Размерный ряд")
        size_layout = QHBoxLayout(size_group)

        self.size_min = QSpinBox()
        self.size_min.setRange(15, 50)
        self.size_min.setValue(36)

        self.size_max = QSpinBox()
        self.size_max.setRange(15, 50)
        self.size_max.setValue(46)

        size_layout.addWidget(QLabel("От:"))
        size_layout.addWidget(self.size_min)
        size_layout.addWidget(QLabel("До:"))
        size_layout.addWidget(self.size_max)
        size_layout.addStretch()

        layout.addRow(size_group)

        # Активность
        self.is_active_check = QCheckBox("Модель активна")
        self.is_active_check.setChecked(True)
        layout.addRow("Статус:", self.is_active_check)

        self.tabs.addTab(tab, "📋 Основные данные")

    def create_characteristics_tab(self):
        """Характеристики"""
        tab = QWidget()
        layout = QFormLayout(tab)

        # Колодка
        self.last_code_input = QLineEdit()
        self.last_code_input.setPlaceholderText("Код колодки")

        self.last_type_combo = QComboBox()
        self.last_type_combo.addItems(["", "Ботиночная", "Туфельная", "Сапожная",
                                      "Спортивная", "Мокасинная"])

        layout.addRow("Код колодки:", self.last_code_input)
        layout.addRow("Тип колодки:", self.last_type_combo)

        # Метод крепления и тип подошвы
        self.assembly_type_combo = QComboBox()
        self.assembly_type_combo.addItems(["", "Клеевой", "Прошивной", "Литьевой",
                                          "Заготовочно-нашивной", "Сандальный"])

        self.sole_type_input = QLineEdit()
        self.sole_type_input.setPlaceholderText("ТЭП, ПУ, Резина, Кожа...")

        layout.addRow("Метод крепления:", self.assembly_type_combo)
        layout.addRow("Тип подошвы:", self.sole_type_input)

        # Тип застежки
        self.closure_type_combo = QComboBox()
        self.closure_type_combo.addItems(["", "Шнурки", "Молния", "Липучка",
                                         "Пряжка", "Резинка", "Без застежки"])

        layout.addRow("Тип застежки:", self.closure_type_combo)

        # Размерный ряд лекал
        self.pattern_size_range_input = QLineEdit()
        self.pattern_size_range_input.setPlaceholderText("36-46")

        layout.addRow("Размерный ряд лекал:", self.pattern_size_range_input)

        self.tabs.addTab(tab, "⚙️ Характеристики")

    def create_materials_tab(self):
        """Материалы и нормы"""
        tab = QWidget()
        layout = QFormLayout(tab)

        # Основной материал верха
        self.default_upper_material = QLineEdit()
        self.default_upper_material.setPlaceholderText("Кожа натуральная, замша...")

        layout.addRow("Материал верха по умолчанию:", self.default_upper_material)

        # Нормы расхода
        norm_group = QGroupBox("Нормы расхода")
        norm_layout = QFormLayout(norm_group)

        self.base_leather_norm = QDoubleSpinBox()
        self.base_leather_norm.setRange(0, 999)
        self.base_leather_norm.setSuffix(" дм²")
        self.base_leather_norm.setDecimals(2)

        self.base_lining_norm = QDoubleSpinBox()
        self.base_lining_norm.setRange(0, 999)
        self.base_lining_norm.setSuffix(" дм²")
        self.base_lining_norm.setDecimals(2)

        self.base_labor_hours = QDoubleSpinBox()
        self.base_labor_hours.setRange(0, 99)
        self.base_labor_hours.setSuffix(" ч")
        self.base_labor_hours.setDecimals(2)

        norm_layout.addRow("Норма кожи:", self.base_leather_norm)
        norm_layout.addRow("Норма подкладки:", self.base_lining_norm)
        norm_layout.addRow("Трудозатраты:", self.base_labor_hours)

        layout.addRow(norm_group)

        self.tabs.addTab(tab, "🧵 Материалы")

    def create_pricing_tab(self):
        """Цены и себестоимость"""
        tab = QWidget()
        layout = QFormLayout(tab)

        # Себестоимость
        cost_group = QGroupBox("Себестоимость")
        cost_layout = QFormLayout(cost_group)

        self.material_cost = QDoubleSpinBox()
        self.material_cost.setRange(0, 999999)
        self.material_cost.setSuffix(" ₽")
        self.material_cost.setDecimals(2)

        self.labor_cost = QDoubleSpinBox()
        self.labor_cost.setRange(0, 999999)
        self.labor_cost.setSuffix(" ₽")
        self.labor_cost.setDecimals(2)

        self.overhead_cost = QDoubleSpinBox()
        self.overhead_cost.setRange(0, 999999)
        self.overhead_cost.setSuffix(" ₽")
        self.overhead_cost.setDecimals(2)

        cost_layout.addRow("Материалы:", self.material_cost)
        cost_layout.addRow("Работа:", self.labor_cost)
        cost_layout.addRow("Накладные:", self.overhead_cost)

        # Итого себестоимость
        self.total_cost_label = QLabel("0.00 ₽")
        self.total_cost_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        cost_layout.addRow("ИТОГО:", self.total_cost_label)

        layout.addRow(cost_group)

        # Цены продажи
        price_group = QGroupBox("Цены продажи")
        price_layout = QFormLayout(price_group)

        self.retail_price = QDoubleSpinBox()
        self.retail_price.setRange(0, 999999)
        self.retail_price.setSuffix(" ₽")
        self.retail_price.setDecimals(2)

        self.wholesale_price = QDoubleSpinBox()
        self.wholesale_price.setRange(0, 999999)
        self.wholesale_price.setSuffix(" ₽")
        self.wholesale_price.setDecimals(2)

        self.online_price = QDoubleSpinBox()
        self.online_price.setRange(0, 999999)
        self.online_price.setSuffix(" ₽")
        self.online_price.setDecimals(2)

        price_layout.addRow("Розничная:", self.retail_price)
        price_layout.addRow("Оптовая:", self.wholesale_price)
        price_layout.addRow("Онлайн:", self.online_price)

        # Маржа
        self.margin_label = QLabel("Маржа: 0%")
        price_layout.addRow(self.margin_label)

        layout.addRow(price_group)

        # Связываем расчеты
        self.material_cost.valueChanged.connect(self.calculate_totals)
        self.labor_cost.valueChanged.connect(self.calculate_totals)
        self.overhead_cost.valueChanged.connect(self.calculate_totals)
        self.retail_price.valueChanged.connect(self.calculate_margin)
        self.wholesale_price.valueChanged.connect(self.calculate_margin)

        self.tabs.addTab(tab, "💰 Цены")

    def create_production_tab(self):
        """Производственные данные"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Заметки о производстве
        layout.addWidget(QLabel("Особенности производства:"))
        self.production_notes = QTextEdit()
        self.production_notes.setMaximumHeight(150)
        self.production_notes.setPlaceholderText(
            "Укажите особые требования к производству, сложные операции, "
            "специальное оборудование..."
        )
        layout.addWidget(self.production_notes)

        # Теги
        layout.addWidget(QLabel("Теги (через запятую):"))
        self.tags_input = QLineEdit()
        self.tags_input.setPlaceholderText("премиум, экспорт, новинка...")
        layout.addWidget(self.tags_input)

        layout.addStretch()

        self.tabs.addTab(tab, "⚙️ Производство")

    def create_components_tab(self):
        """Компоненты модели"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Информация
        info_label = QLabel(
            "Детали кроя и компоненты модели настраиваются через отдельное окно "
            "после сохранения основных данных модели."
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        # Кнопка открытия редактора компонентов
        self.btn_edit_components = QPushButton("📝 Редактировать компоненты модели")
        self.btn_edit_components.setEnabled(False)  # Активируется после сохранения
        self.btn_edit_components.clicked.connect(self.open_components_dialog)
        layout.addWidget(self.btn_edit_components)

        # Таблица текущих компонентов (только просмотр)
        layout.addWidget(QLabel("Текущие компоненты:"))
        self.components_table = QTableWidget()
        self.components_table.setColumnCount(3)
        self.components_table.setHorizontalHeaderLabels(["Тип", "Название", "Количество"])
        layout.addWidget(self.components_table)

        self.tabs.addTab(tab, "🧩 Компоненты")

    def create_additional_tab(self):
        """Дополнительная информация"""
        tab = QWidget()
        layout = QFormLayout(tab)

        # Фото
        self.main_photo_url = QLineEdit()
        self.main_photo_url.setPlaceholderText("URL основного фото")
        layout.addRow("Основное фото:", self.main_photo_url)

        # Дополнительные свойства
        layout.addRow(QLabel("Дополнительные свойства (JSON):"))
        self.properties_text = QTextEdit()
        self.properties_text.setMaximumHeight(150)
        self.properties_text.setPlaceholderText('{"ключ": "значение"}')
        layout.addRow(self.properties_text)

        self.tabs.addTab(tab, "📎 Дополнительно")

    def calculate_totals(self):
        """Расчет итоговой себестоимости"""
        total = (self.material_cost.value() +
                self.labor_cost.value() +
                self.overhead_cost.value())
        self.total_cost_label.setText(f"{total:.2f} ₽")
        self.calculate_margin()

    def calculate_margin(self):
        """Расчет маржи"""
        total_cost = (self.material_cost.value() +
                     self.labor_cost.value() +
                     self.overhead_cost.value())

        if total_cost > 0:
            retail_margin = ((self.retail_price.value() - total_cost) / total_cost * 100)
            wholesale_margin = ((self.wholesale_price.value() - total_cost) / total_cost * 100)
            self.margin_label.setText(
                f"Маржа: Розница {retail_margin:.1f}% | Опт {wholesale_margin:.1f}%"
            )
        else:
            self.margin_label.setText("Маржа: 0%")

    def save_data(self):
        """Сохранение данных в БД"""
        if not self.validate():
            return

        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            # Собираем все данные
            data = {
                'article': self.article_input.text(),
                'name': self.name_input.text(),
                'gender': self.gender_combo.currentText() or None,
                'model_type': self.model_type_input.text() or None,
                'category': self.category_input.text() or None,
                'collection': self.collection_input.text() or None,
                'season': self.season_combo.currentText() or None,
                'last_code': self.last_code_input.text() or None,
                'last_type': self.last_type_combo.currentText() or None,
                'closure_type': self.closure_type_combo.currentText() or None,
                'sole_type': self.sole_type_input.text() or None,
                'size_min': self.size_min.value(),
                'size_max': self.size_max.value(),
                'pattern_size_range': self.pattern_size_range_input.text() or None,
                'assembly_type': self.assembly_type_combo.currentText() or None,
                'default_upper_material': self.default_upper_material.text() or None,
                'base_leather_norm': self.base_leather_norm.value() if self.base_leather_norm.value() > 0 else None,
                'base_lining_norm': self.base_lining_norm.value() if self.base_lining_norm.value() > 0 else None,
                'base_labor_hours': self.base_labor_hours.value() if self.base_labor_hours.value() > 0 else None,
                'material_cost': self.material_cost.value() if self.material_cost.value() > 0 else None,
                'labor_cost': self.labor_cost.value() if self.labor_cost.value() > 0 else None,
                'overhead_cost': self.overhead_cost.value() if self.overhead_cost.value() > 0 else None,
                'retail_price': self.retail_price.value() if self.retail_price.value() > 0 else None,
                'wholesale_price': self.wholesale_price.value() if self.wholesale_price.value() > 0 else None,
                'online_price': self.online_price.value() if self.online_price.value() > 0 else None,
                'main_photo_url': self.main_photo_url.text() or None,
                'is_active': self.is_active_check.isChecked()
            }

            # Обработка JSON полей
            if self.tags_input.text():
                tags = [tag.strip() for tag in self.tags_input.text().split(',')]
                data['tags'] = json.dumps(tags, ensure_ascii=False)

            if self.properties_text.toPlainText():
                try:
                    properties = json.loads(self.properties_text.toPlainText())
                    data['properties'] = json.dumps(properties, ensure_ascii=False)
                except:
                    pass

            if self.record_id:
                # Обновление
                columns = []
                values = []
                for key, value in data.items():
                    columns.append(f"{key} = %s")
                    values.append(value)
                values.append(self.record_id)

                query = f"UPDATE models SET {', '.join(columns)}, updated_at = NOW() WHERE id = %s"
                cursor.execute(query, values)
            else:
                # Создание
                import uuid
                data['uuid'] = str(uuid.uuid4())

                columns = list(data.keys())
                placeholders = ['%s'] * len(columns)

                query = f"""
                    INSERT INTO models ({', '.join(columns)}, created_at, updated_at)
                    VALUES ({', '.join(placeholders)}, NOW(), NOW())
                    RETURNING id
                """
                cursor.execute(query, list(data.values()))
                self.record_id = cursor.fetchone()[0]

            conn.commit()
            cursor.close()
            self.db.put_connection(conn)

            # После сохранения активируем кнопку компонентов
            self.btn_edit_components.setEnabled(True)

            QMessageBox.information(self, "Успешно", "Модель сохранена")
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить: {e}")

    def load_data(self, record_id: int):
        """Загрузка данных модели"""
        self.record_id = record_id

        try:
            conn = self.db.get_connection()
            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cursor.execute("SELECT * FROM models WHERE id = %s", (record_id,))
            row = cursor.fetchone()
            cursor.close()
            self.db.put_connection(conn)

            if row:
                # Основные данные
                self.article_input.setText(row['article'] or '')
                self.name_input.setText(row['name'] or '')
                self.gender_combo.setCurrentText(row['gender'] or '')
                self.model_type_input.setText(row['model_type'] or '')
                self.category_input.setText(row['category'] or '')
                self.collection_input.setText(row['collection'] or '')
                self.season_combo.setCurrentText(row['season'] or '')

                # Размеры
                if row['size_min']:
                    self.size_min.setValue(row['size_min'])
                if row['size_max']:
                    self.size_max.setValue(row['size_max'])

                # Характеристики
                self.last_code_input.setText(row['last_code'] or '')
                self.last_type_combo.setCurrentText(row['last_type'] or '')
                self.assembly_type_combo.setCurrentText(row['assembly_type'] or '')
                self.sole_type_input.setText(row['sole_type'] or '')
                self.closure_type_combo.setCurrentText(row['closure_type'] or '')
                self.pattern_size_range_input.setText(row['pattern_size_range'] or '')

                # Материалы
                self.default_upper_material.setText(row['default_upper_material'] or '')
                if row['base_leather_norm']:
                    self.base_leather_norm.setValue(float(row['base_leather_norm']))
                if row['base_lining_norm']:
                    self.base_lining_norm.setValue(float(row['base_lining_norm']))
                if row['base_labor_hours']:
                    self.base_labor_hours.setValue(float(row['base_labor_hours']))

                # Цены
                if row['material_cost']:
                    self.material_cost.setValue(float(row['material_cost']))
                if row['labor_cost']:
                    self.labor_cost.setValue(float(row['labor_cost']))
                if row['overhead_cost']:
                    self.overhead_cost.setValue(float(row['overhead_cost']))
                if row['retail_price']:
                    self.retail_price.setValue(float(row['retail_price']))
                if row['wholesale_price']:
                    self.wholesale_price.setValue(float(row['wholesale_price']))
                if row['online_price']:
                    self.online_price.setValue(float(row['online_price']))

                # Дополнительно
                self.main_photo_url.setText(row['main_photo_url'] or '')
                if row['tags']:
                    tags = json.loads(row['tags']) if isinstance(row['tags'], str) else row['tags']
                    self.tags_input.setText(', '.join(tags))
                if row['properties']:
                    props = row['properties'] if isinstance(row['properties'], dict) else json.loads(row['properties'])
                    self.properties_text.setPlainText(json.dumps(props, indent=2, ensure_ascii=False))

                self.is_active_check.setChecked(row['is_active'] if row['is_active'] is not None else True)

                # Активируем кнопку компонентов
                self.btn_edit_components.setEnabled(True)
                # Загружаем превью компонентов
                self.load_components_preview()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить данные: {e}")

    def validate(self) -> bool:
        """Валидация формы"""
        if not self.article_input.text():
            QMessageBox.warning(self, "Ошибка", "Укажите артикул модели")
            self.tabs.setCurrentIndex(0)
            self.article_input.setFocus()
            return False

        if not self.name_input.text():
            QMessageBox.warning(self, "Ошибка", "Укажите название модели")
            self.tabs.setCurrentIndex(0)
            self.name_input.setFocus()
            return False

        return True

    def open_components_dialog(self):
        """Открыть диалог управления компонентами"""
        if not self.record_id:
            QMessageBox.warning(self, "Внимание",
                              "Сначала сохраните модель для добавления компонентов")
            return

        article = self.article_input.text()
        dialog = ModelComponentsDialog(self.record_id, article, self)
        dialog.exec()
        self.load_components_preview()

    def load_components_preview(self):
        """Загрузить превью компонентов в таблицу"""
        if not self.record_id:
            return

        try:
            conn = self.db.get_connection()
            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cursor.execute("""
                SELECT component_group, component_name,
                       COALESCE(absolute_consumption, consumption_percent) as qty,
                       unit
                FROM model_components
                WHERE model_id = %s
                ORDER BY sort_order
            """, (self.record_id,))

            components = cursor.fetchall()
            cursor.close()
            self.db.put_connection(conn)

            # Обновляем таблицу компонентов
            self.components_table.setRowCount(len(components))
            for row, comp in enumerate(components):
                group_display = {
                    'cutting': 'Крой',
                    'material': 'Материал',
                    'other': 'Прочее'
                }.get(comp['component_group'], comp['component_group'])

                self.components_table.setItem(row, 0, QTableWidgetItem(group_display))
                self.components_table.setItem(row, 1, QTableWidgetItem(comp['component_name']))
                qty_str = f"{comp['qty']:.2f} {comp['unit']}" if comp['qty'] else ""
                self.components_table.setItem(row, 2, QTableWidgetItem(qty_str))

        except Exception as e:
            print(f"Error loading components preview: {e}")