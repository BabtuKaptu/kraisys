"""
Современная форма создания/редактирования модели обуви Version 0.4
Использует новые enhanced компоненты для красивого UI
"""

import json
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QScrollArea, QWidget, QLabel,
    QLineEdit, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox, QCheckBox,
    QTabWidget, QFrame, QApplication
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont

from ui.styles.app_styles import AppColors, AppIcons, AppFonts
from ui.components.enhanced_widgets import (
    StyledButton, ValidatedLineEdit, FormGroupBox, LoadingWidget,
    NotificationBar, ButtonGroup, create_form_row, create_field_with_validation
)
from database.connection import DatabaseConnection


class ModelSpecificationFormV6(QDialog):
    """Современная форма для создания/редактирования модели обуви"""

    modelSaved = pyqtSignal(dict)  # Сигнал о сохранении модели

    def __init__(self, model_data=None, parent=None):
        super().__init__(parent)
        self.model_data = model_data
        self.is_edit_mode = model_data is not None

        # Подключение к БД
        self.db = DatabaseConnection()

        # Справочные данные
        self.lasting_types = []
        self.lining_types = []
        self.perforation_types = []
        self.materials = []
        self.sole_constructions = []

        self._setup_window()
        self._setup_ui()
        self._load_reference_data()

        if self.is_edit_mode:
            self._populate_fields()

    def _setup_window(self):
        """Настройка окна"""
        title = "Редактирование модели" if self.is_edit_mode else "Новая модель"
        self.setWindowTitle(f"{AppIcons.MODEL} {title}")
        self.setModal(True)
        self.resize(1000, 700)
        self.setMinimumSize(800, 600)

        # Применяем единый стиль
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {AppColors.BACKGROUND};
                color: {AppColors.TEXT_PRIMARY};
                font-family: {AppFonts.FAMILY_PRIMARY};
            }}
        """)

    def _setup_ui(self):
        """Настройка интерфейса"""
        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        # Панель уведомлений
        self.notification_bar = NotificationBar()
        layout.addWidget(self.notification_bar)

        # Заголовок формы
        self._setup_header(layout)

        # Основной контент в скролл-области
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameStyle(QFrame.Shape.NoFrame)

        # Контейнер для скролла
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(20)

        # Табы с разделами формы
        self.tabs = QTabWidget()
        self._setup_tabs()
        scroll_layout.addWidget(self.tabs)

        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area)

        # Кнопки действий
        self._setup_action_buttons(layout)

        # Виджет загрузки (скрыт по умолчанию)
        self.loading_widget = LoadingWidget("Сохранение модели...")
        self.loading_widget.hide()
        layout.addWidget(self.loading_widget)

    def _setup_header(self, layout):
        """Настройка заголовка"""
        header_frame = QFrame()
        header_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {AppColors.SURFACE};
                border: 1px solid {AppColors.LIGHT_GRAY};
                border-radius: 8px;
                padding: 16px;
            }}
        """)

        header_layout = QHBoxLayout(header_frame)

        # Иконка и заголовок
        icon_label = QLabel(AppIcons.MODEL)
        icon_label.setStyleSheet(f"font-size: 32px; color: {AppColors.PRIMARY};")
        header_layout.addWidget(icon_label)

        title_layout = QVBoxLayout()

        title_text = "Редактирование модели" if self.is_edit_mode else "Создание новой модели"
        title_label = QLabel(title_text)
        title_label.setStyleSheet(f"""
            font-size: 20px;
            font-weight: 600;
            color: {AppColors.TEXT_PRIMARY};
            margin: 0;
        """)
        title_layout.addWidget(title_label)

        subtitle = "Заполните все обязательные поля для создания модели" if not self.is_edit_mode else "Внесите необходимые изменения"
        subtitle_label = QLabel(subtitle)
        subtitle_label.setStyleSheet(f"color: {AppColors.TEXT_SECONDARY}; font-size: 14px;")
        title_layout.addWidget(subtitle_label)

        header_layout.addLayout(title_layout)
        header_layout.addStretch()

        # Статус модели (для режима редактирования)
        if self.is_edit_mode:
            status_label = QLabel(f"{AppIcons.SUCCESS} Активна")
            status_label.setStyleSheet(f"""
                background-color: {AppColors.SUCCESS_LIGHT};
                color: {AppColors.SUCCESS};
                padding: 6px 12px;
                border-radius: 16px;
                font-weight: 500;
            """)
            header_layout.addWidget(status_label)

        layout.addWidget(header_frame)

    def _setup_tabs(self):
        """Настройка вкладок формы"""
        # Основная информация
        self.main_tab = self._create_main_info_tab()
        self.tabs.addTab(self.main_tab, f"{AppIcons.INFO} Основное")

        # Материалы и конструкция
        self.materials_tab = self._create_materials_tab()
        self.tabs.addTab(self.materials_tab, f"{AppIcons.MATERIAL} Материалы")

        # Крой и фурнитура
        self.cutting_tab = self._create_cutting_tab()
        self.tabs.addTab(self.cutting_tab, f"{AppIcons.CUTTING} Крой")

        # Подошва
        self.sole_tab = self._create_sole_tab()
        self.tabs.addTab(self.sole_tab, f"{AppIcons.SOLE} Подошва")

    def _create_main_info_tab(self):
        """Создание вкладки основной информации"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(20)

        # Основная информация
        main_group = FormGroupBox("Основная информация")
        main_layout = QVBoxLayout(main_group)
        main_layout.setSpacing(12)

        # Название модели
        name_row, self.name_field = create_field_with_validation(
            "Название модели", "Введите название модели", True,
            lambda x: len(x.strip()) >= 3
        )
        main_layout.addWidget(name_row)

        # Артикул
        article_row, self.article_field = create_field_with_validation(
            "Артикул", "Уникальный артикул модели", True,
            lambda x: len(x.strip()) >= 3 and x.replace('-', '').replace('_', '').isalnum()
        )
        main_layout.addWidget(article_row)

        # Описание
        desc_row = create_form_row("Описание", QTextEdit())
        self.description_field = desc_row.findChild(QTextEdit)
        self.description_field.setMaximumHeight(80)
        self.description_field.setPlaceholderText("Краткое описание модели...")
        self.description_field.setStyleSheet(f"""
            QTextEdit {{
                background-color: {AppColors.SURFACE};
                color: {AppColors.TEXT_PRIMARY};
                border: 2px solid {AppColors.LIGHT_GRAY};
                border-radius: 6px;
                padding: 8px;
                font-size: 14px;
            }}
            QTextEdit:focus {{
                border-color: {AppColors.PRIMARY};
            }}
        """)
        main_layout.addWidget(desc_row)

        layout.addWidget(main_group)

        # Конструктивные параметры
        construction_group = FormGroupBox("Конструктивные параметры")
        construction_layout = QVBoxLayout(construction_group)
        construction_layout.setSpacing(12)

        # Тип затяжки
        lasting_row = create_form_row("Тип затяжки", QComboBox(), True)
        self.lasting_type_combo = lasting_row.findChild(QComboBox)
        construction_layout.addWidget(lasting_row)

        # Тип подкладки
        lining_row = create_form_row("Тип подкладки", QComboBox(), True)
        self.lining_type_combo = lining_row.findChild(QComboBox)
        construction_layout.addWidget(lining_row)

        # Тип перфорации
        perforation_row = create_form_row("Перфорация", QComboBox())
        self.perforation_type_combo = perforation_row.findChild(QComboBox)
        construction_layout.addWidget(perforation_row)

        layout.addWidget(construction_group)

        layout.addStretch()
        return tab

    def _create_materials_tab(self):
        """Создание вкладки материалов"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        materials_group = FormGroupBox("Материалы верха")
        materials_layout = QVBoxLayout(materials_group)

        # Основной материал
        main_material_row = create_form_row("Основной материал", QComboBox(), True)
        self.main_material_combo = main_material_row.findChild(QComboBox)
        materials_layout.addWidget(main_material_row)

        # Дополнительный материал
        additional_material_row = create_form_row("Дополнительный материал", QComboBox())
        self.additional_material_combo = additional_material_row.findChild(QComboBox)
        materials_layout.addWidget(additional_material_row)

        # Цветовая схема
        color_row, self.color_field = create_field_with_validation(
            "Цветовая схема", "Основные цвета модели"
        )
        materials_layout.addWidget(color_row)

        layout.addWidget(materials_group)
        layout.addStretch()
        return tab

    def _create_cutting_tab(self):
        """Создание вкладки кроя и фурнитуры"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        cutting_group = FormGroupBox("Детали кроя и фурнитура")
        cutting_layout = QVBoxLayout(cutting_group)

        # Информационная панель
        info_frame = QFrame()
        info_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {AppColors.INFO_LIGHT};
                border: 1px solid {AppColors.INFO};
                border-radius: 6px;
                padding: 12px;
            }}
        """)
        info_layout = QHBoxLayout(info_frame)

        info_icon = QLabel(AppIcons.INFO)
        info_icon.setStyleSheet(f"color: {AppColors.INFO}; font-size: 16px;")
        info_layout.addWidget(info_icon)

        info_text = QLabel("Детали кроя и фурнитура будут настроены в отдельном разделе")
        info_text.setStyleSheet(f"color: {AppColors.TEXT_PRIMARY}; font-weight: 500;")
        info_layout.addWidget(info_text)
        info_layout.addStretch()

        cutting_layout.addWidget(info_frame)

        # Заглушка для будущего функционала
        placeholder_label = QLabel("🚧 Раздел в разработке")
        placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder_label.setStyleSheet(f"""
            color: {AppColors.TEXT_SECONDARY};
            font-size: 16px;
            padding: 40px;
        """)
        cutting_layout.addWidget(placeholder_label)

        layout.addWidget(cutting_group)
        layout.addStretch()
        return tab

    def _create_sole_tab(self):
        """Создание вкладки подошвы"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        sole_group = FormGroupBox("Конструкция подошвы")
        sole_layout = QVBoxLayout(sole_group)

        # Тип подошвы
        sole_type_row = create_form_row("Тип подошвы", QComboBox(), True)
        self.sole_type_combo = sole_type_row.findChild(QComboBox)
        sole_layout.addWidget(sole_type_row)

        # Материал подошвы
        sole_material_row, self.sole_material_field = create_field_with_validation(
            "Материал подошвы", "Материал изготовления подошвы", True
        )
        sole_layout.addWidget(sole_material_row)

        # Высота каблука
        heel_height_row = create_form_row("Высота каблука (мм)", QSpinBox())
        self.heel_height_spin = heel_height_row.findChild(QSpinBox)
        self.heel_height_spin.setRange(0, 200)
        self.heel_height_spin.setSuffix(" мм")
        sole_layout.addWidget(heel_height_row)

        layout.addWidget(sole_group)
        layout.addStretch()
        return tab

    def _setup_action_buttons(self, layout):
        """Настройка кнопок действий"""
        buttons_frame = QFrame()
        buttons_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {AppColors.SURFACE};
                border-top: 1px solid {AppColors.LIGHT_GRAY};
                padding: 16px;
            }}
        """)

        self.button_group = ButtonGroup()

        # Кнопка отмены
        self.cancel_btn = self.button_group.add_button(
            "Отмена", AppIcons.CANCEL, StyledButton.STYLE_SECONDARY
        )
        self.cancel_btn.clicked.connect(self.reject)

        # Кнопка сохранения
        save_text = "Сохранить изменения" if self.is_edit_mode else "Создать модель"
        self.save_btn = self.button_group.add_button(
            save_text, AppIcons.SAVE, StyledButton.STYLE_SUCCESS
        )
        self.save_btn.clicked.connect(self._save_model)

        buttons_layout = QHBoxLayout(buttons_frame)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.button_group)

        layout.addWidget(buttons_frame)

    def _load_reference_data(self):
        """Загрузка справочных данных"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            # Загрузка типов затяжки
            cursor.execute("SELECT id, name FROM lasting_types ORDER BY name")
            self.lasting_types = cursor.fetchall()
            self.lasting_type_combo.clear()
            self.lasting_type_combo.addItem("Выберите тип затяжки...", None)
            for lasting_type in self.lasting_types:
                self.lasting_type_combo.addItem(lasting_type[1], lasting_type[0])

            # Загрузка типов подкладки
            cursor.execute("SELECT id, name FROM lining_types ORDER BY name")
            self.lining_types = cursor.fetchall()
            self.lining_type_combo.clear()
            self.lining_type_combo.addItem("Выберите тип подкладки...", None)
            for lining_type in self.lining_types:
                self.lining_type_combo.addItem(lining_type[1], lining_type[0])

            # Загрузка типов перфорации
            cursor.execute("SELECT id, name FROM perforation_types ORDER BY name")
            self.perforation_types = cursor.fetchall()
            self.perforation_type_combo.clear()
            self.perforation_type_combo.addItem("Без перфорации", None)
            for perforation_type in self.perforation_types:
                self.perforation_type_combo.addItem(perforation_type[1], perforation_type[0])

            # Загрузка материалов
            cursor.execute("SELECT id, name, type FROM materials ORDER BY type, name")
            self.materials = cursor.fetchall()

            # Заполнение комбобоксов материалов
            for combo in [self.main_material_combo, self.additional_material_combo]:
                combo.clear()
                combo.addItem("Выберите материал...", None)
                for material in self.materials:
                    combo.addItem(f"{material[1]} ({material[2]})", material[0])

            # Загрузка конструкций подошв
            cursor.execute("SELECT id, type, material FROM sole_constructions ORDER BY type")
            self.sole_constructions = cursor.fetchall()
            self.sole_type_combo.clear()
            self.sole_type_combo.addItem("Выберите тип подошвы...", None)
            for sole in self.sole_constructions:
                self.sole_type_combo.addItem(f"{sole[1]} - {sole[2]}", sole[0])

            cursor.close()
            conn.close()

        except Exception as e:
            self.notification_bar.show_notification(
                f"Ошибка загрузки справочных данных: {e}",
                NotificationBar.TYPE_ERROR
            )

    def _populate_fields(self):
        """Заполнение полей данными модели (режим редактирования)"""
        if not self.model_data:
            return

        try:
            # Основные поля
            self.name_field.setText(self.model_data.get('name', ''))
            self.article_field.setText(self.model_data.get('article', ''))
            self.description_field.setPlainText(self.model_data.get('description', ''))
            self.color_field.setText(self.model_data.get('color_scheme', ''))
            self.sole_material_field.setText(self.model_data.get('sole_material', ''))

            # Численные поля
            self.heel_height_spin.setValue(self.model_data.get('heel_height', 0))

            # Комбобоксы
            self._set_combo_value(self.lasting_type_combo, self.model_data.get('lasting_type_id'))
            self._set_combo_value(self.lining_type_combo, self.model_data.get('lining_type_id'))
            self._set_combo_value(self.perforation_type_combo, self.model_data.get('perforation_type_id'))
            self._set_combo_value(self.main_material_combo, self.model_data.get('main_material_id'))
            self._set_combo_value(self.additional_material_combo, self.model_data.get('additional_material_id'))
            self._set_combo_value(self.sole_type_combo, self.model_data.get('sole_construction_id'))

        except Exception as e:
            self.notification_bar.show_notification(
                f"Ошибка при заполнении полей: {e}",
                NotificationBar.TYPE_WARNING
            )

    def _set_combo_value(self, combo, value_id):
        """Установка значения в комбобоксе по ID"""
        if value_id is not None:
            for i in range(combo.count()):
                if combo.itemData(i) == value_id:
                    combo.setCurrentIndex(i)
                    break

    def _validate_form(self):
        """Валидация формы"""
        errors = []

        # Проверка обязательных полей
        if not self.name_field.is_valid() or not self.name_field.text().strip():
            errors.append("Название модели обязательно для заполнения")

        if not self.article_field.is_valid() or not self.article_field.text().strip():
            errors.append("Артикул модели обязателен и должен быть уникальным")

        if self.lasting_type_combo.currentData() is None:
            errors.append("Выберите тип затяжки")

        if self.lining_type_combo.currentData() is None:
            errors.append("Выберите тип подкладки")

        if self.main_material_combo.currentData() is None:
            errors.append("Выберите основной материал")

        if self.sole_type_combo.currentData() is None:
            errors.append("Выберите тип подошвы")

        if not self.sole_material_field.is_valid() or not self.sole_material_field.text().strip():
            errors.append("Материал подошвы обязателен для заполнения")

        return errors

    def _save_model(self):
        """Сохранение модели"""
        # Валидация
        errors = self._validate_form()
        if errors:
            error_message = "Исправьте следующие ошибки:\n• " + "\n• ".join(errors)
            self.notification_bar.show_notification(error_message, NotificationBar.TYPE_ERROR, 0)
            return

        # Показываем индикатор загрузки
        self.loading_widget.show()
        self.save_btn.setEnabled(False)
        self.cancel_btn.setEnabled(False)

        # Имитация задержки сохранения для демонстрации UX
        QTimer.singleShot(1000, self._perform_save)

    def _perform_save(self):
        """Выполнение сохранения"""
        try:
            conn = self.db.get_connection()
            cursor = conn.cursor()

            # Подготовка данных
            model_data = {
                'name': self.name_field.text().strip(),
                'article': self.article_field.text().strip(),
                'description': self.description_field.toPlainText().strip(),
                'lasting_type_id': self.lasting_type_combo.currentData(),
                'lining_type_id': self.lining_type_combo.currentData(),
                'perforation_type_id': self.perforation_type_combo.currentData(),
                'main_material_id': self.main_material_combo.currentData(),
                'additional_material_id': self.additional_material_combo.currentData(),
                'color_scheme': self.color_field.text().strip(),
                'sole_construction_id': self.sole_type_combo.currentData(),
                'sole_material': self.sole_material_field.text().strip(),
                'heel_height': self.heel_height_spin.value(),
                'cutting_parts': json.dumps([]),  # Пустой массив пока
                'hardware': json.dumps([]),       # Пустой массив пока
                'soles': json.dumps([])           # Пустой массив пока
            }

            if self.is_edit_mode:
                # Обновление существующей модели
                update_query = """
                    UPDATE models SET
                        name = %s, article = %s, description = %s,
                        lasting_type_id = %s, lining_type_id = %s, perforation_type_id = %s,
                        main_material_id = %s, additional_material_id = %s, color_scheme = %s,
                        sole_construction_id = %s, sole_material = %s, heel_height = %s,
                        cutting_parts = %s, hardware = %s, soles = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                """
                cursor.execute(update_query, list(model_data.values()) + [self.model_data['id']])
                model_data['id'] = self.model_data['id']
            else:
                # Создание новой модели
                insert_query = """
                    INSERT INTO models (name, article, description, lasting_type_id, lining_type_id,
                                      perforation_type_id, main_material_id, additional_material_id,
                                      color_scheme, sole_construction_id, sole_material, heel_height,
                                      cutting_parts, hardware, soles, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                            CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    RETURNING id
                """
                cursor.execute(insert_query, list(model_data.values()))
                model_data['id'] = cursor.fetchone()[0]

            conn.commit()
            cursor.close()
            conn.close()

            # Скрытие индикатора загрузки
            self.loading_widget.hide()

            # Уведомление об успехе
            success_message = "Модель успешно обновлена!" if self.is_edit_mode else "Модель успешно создана!"
            self.notification_bar.show_notification(success_message, NotificationBar.TYPE_SUCCESS, 3000)

            # Эмиссия сигнала
            self.modelSaved.emit(model_data)

            # Закрытие формы через небольшую задержку
            QTimer.singleShot(1500, self.accept)

        except Exception as e:
            # Скрытие индикатора загрузки
            self.loading_widget.hide()
            self.save_btn.setEnabled(True)
            self.cancel_btn.setEnabled(True)

            # Показ ошибки
            self.notification_bar.show_notification(
                f"Ошибка при сохранении: {e}",
                NotificationBar.TYPE_ERROR,
                0
            )


def test_form():
    """Тестовая функция для демонстрации формы"""
    app = QApplication([])

    # Тестовые данные модели для режима редактирования
    test_model_data = {
        'id': 1,
        'name': 'Классические туфли',
        'article': 'TF001',
        'description': 'Элегантные мужские туфли из натуральной кожи',
        'lasting_type_id': 1,
        'lining_type_id': 1,
        'perforation_type_id': None,
        'main_material_id': 1,
        'additional_material_id': None,
        'color_scheme': 'Черный',
        'sole_construction_id': 1,
        'sole_material': 'Кожа + резина',
        'heel_height': 25
    }

    # Создание формы в режиме создания
    # form = ModelSpecificationFormV6()

    # Создание формы в режиме редактирования
    form = ModelSpecificationFormV6(test_model_data)

    form.show()
    app.exec()


if __name__ == "__main__":
    test_form()