#!/usr/bin/env python3
"""
Тестовый файл для демонстрации новых UI компонентов Version 0.4
Запустите этот файл для просмотра всех новых возможностей
"""

import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QTabWidget, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt

# Добавляем путь к проекту
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

from ui.styles.app_styles import AppColors, AppIcons, AppFonts, AppStyles
from ui.components.enhanced_widgets import (
    StyledButton, ValidatedLineEdit, FormGroupBox, LoadingWidget,
    NotificationBar, ButtonGroup, create_form_row, create_field_with_validation
)
from ui.base.enhanced_table import EnhancedTableWidget
from ui.references.model_specification_form_v6 import ModelSpecificationFormV6


class ComponentsTestWindow(QMainWindow):
    """Окно для тестирования новых компонентов"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{AppIcons.SETTINGS} KRAI UI Components v0.4 - Тест новых компонентов")
        self.setGeometry(100, 100, 1200, 800)

        # Применяем единый стиль
        self.setStyleSheet(AppStyles.get_combined_style())

        self._setup_ui()

    def _setup_ui(self):
        """Настройка интерфейса"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        # Заголовок
        header_label = QLabel(f"{AppIcons.MODEL} KRAI Desktop v0.4 - Демонстрация новых UI компонентов")
        header_label.setStyleSheet(f"""
            QLabel {{
                font-size: 24px;
                font-weight: 600;
                color: {AppColors.PRIMARY};
                padding: 16px;
                background-color: {AppColors.SURFACE};
                border-radius: 8px;
                border: 1px solid {AppColors.LIGHT_GRAY};
            }}
        """)
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header_label)

        # Вкладки с демонстрациями
        tabs = QTabWidget()

        # Вкладка кнопок
        buttons_tab = self._create_buttons_demo()
        tabs.addTab(buttons_tab, f"{AppIcons.SUCCESS} Кнопки")

        # Вкладка полей ввода
        inputs_tab = self._create_inputs_demo()
        tabs.addTab(inputs_tab, f"{AppIcons.EDIT} Поля ввода")

        # Вкладка таблиц
        tables_tab = self._create_tables_demo()
        tabs.addTab(tables_tab, f"{AppIcons.SORT} Таблицы")

        # Вкладка форм
        forms_tab = self._create_forms_demo()
        tabs.addTab(forms_tab, f"{AppIcons.MODEL} Формы")

        layout.addWidget(tabs)

    def _create_buttons_demo(self):
        """Демонстрация кнопок"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Группа кнопок
        buttons_group = FormGroupBox("Различные стили кнопок")
        buttons_layout = QVBoxLayout(buttons_group)

        # Ряд основных кнопок
        row1 = QHBoxLayout()
        row1.addWidget(StyledButton("Основная", AppIcons.SUCCESS, StyledButton.STYLE_PRIMARY))
        row1.addWidget(StyledButton("Вторичная", AppIcons.EDIT, StyledButton.STYLE_SECONDARY))
        row1.addWidget(StyledButton("Успех", AppIcons.OK, StyledButton.STYLE_SUCCESS))
        row1.addWidget(StyledButton("Предупреждение", AppIcons.WARNING, StyledButton.STYLE_WARNING))
        row1.addWidget(StyledButton("Ошибка", AppIcons.ERROR, StyledButton.STYLE_ERROR))
        row1.addStretch()
        buttons_layout.addLayout(row1)

        # Группа кнопок
        button_group = ButtonGroup()
        button_group.add_button("Добавить", AppIcons.ADD, StyledButton.STYLE_PRIMARY)
        button_group.add_button("Редактировать", AppIcons.EDIT, StyledButton.STYLE_SECONDARY)
        button_group.add_button("Удалить", AppIcons.DELETE, StyledButton.STYLE_ERROR)
        buttons_layout.addWidget(button_group)

        layout.addWidget(buttons_group)

        # Уведомления
        notifications_group = FormGroupBox("Уведомления")
        notifications_layout = QVBoxLayout(notifications_group)

        self.notification_bar = NotificationBar()
        notifications_layout.addWidget(self.notification_bar)

        # Кнопки для тестирования уведомлений
        notif_buttons = QHBoxLayout()

        info_btn = StyledButton("Информация", AppIcons.INFO, StyledButton.STYLE_SECONDARY)
        info_btn.clicked.connect(lambda: self.notification_bar.show_notification("Это информационное сообщение", NotificationBar.TYPE_INFO))
        notif_buttons.addWidget(info_btn)

        success_btn = StyledButton("Успех", AppIcons.SUCCESS, StyledButton.STYLE_SUCCESS)
        success_btn.clicked.connect(lambda: self.notification_bar.show_notification("Операция выполнена успешно!", NotificationBar.TYPE_SUCCESS))
        notif_buttons.addWidget(success_btn)

        warning_btn = StyledButton("Предупреждение", AppIcons.WARNING, StyledButton.STYLE_WARNING)
        warning_btn.clicked.connect(lambda: self.notification_bar.show_notification("Внимание! Проверьте данные", NotificationBar.TYPE_WARNING))
        notif_buttons.addWidget(warning_btn)

        error_btn = StyledButton("Ошибка", AppIcons.ERROR, StyledButton.STYLE_ERROR)
        error_btn.clicked.connect(lambda: self.notification_bar.show_notification("Произошла ошибка при выполнении операции", NotificationBar.TYPE_ERROR))
        notif_buttons.addWidget(error_btn)

        notif_buttons.addStretch()
        notifications_layout.addLayout(notif_buttons)

        layout.addWidget(notifications_group)
        layout.addStretch()

        return widget

    def _create_inputs_demo(self):
        """Демонстрация полей ввода"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Группа полей с валидацией
        validation_group = FormGroupBox("Поля с валидацией")
        validation_layout = QVBoxLayout(validation_group)

        # Обязательное поле
        required_row, self.required_field = create_field_with_validation(
            "Обязательное поле", "Введите не менее 3 символов", True,
            lambda x: len(x.strip()) >= 3
        )
        validation_layout.addWidget(required_row)

        # Поле с проверкой email
        email_row, self.email_field = create_field_with_validation(
            "Email", "example@domain.com", False,
            lambda x: "@" in x and "." in x.split("@")[-1] if x else True
        )
        validation_layout.addWidget(email_row)

        # Поле с проверкой числа
        number_row, self.number_field = create_field_with_validation(
            "Число", "Введите число от 1 до 100", False,
            lambda x: x.isdigit() and 1 <= int(x) <= 100 if x else True
        )
        validation_layout.addWidget(number_row)

        layout.addWidget(validation_group)

        # Индикатор загрузки
        loading_group = FormGroupBox("Индикатор загрузки")
        loading_layout = QVBoxLayout(loading_group)

        self.loading_widget = LoadingWidget("Демонстрация загрузки...")
        self.loading_widget.hide()
        loading_layout.addWidget(self.loading_widget)

        loading_btn = StyledButton("Показать загрузку", AppIcons.REFRESH, StyledButton.STYLE_PRIMARY)
        loading_btn.clicked.connect(self._toggle_loading)
        loading_layout.addWidget(loading_btn)

        layout.addWidget(loading_group)
        layout.addStretch()

        return widget

    def _create_tables_demo(self):
        """Демонстрация таблиц"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Улучшенная таблица
        self.demo_table = EnhancedTableWidget("Демонстрационные данные")
        self.demo_table.set_columns(["ID", "Название", "Категория", "Статус", "Дата"])

        # Тестовые данные
        demo_data = [
            [1, "Кроссовки спортивные", "Спортивная обувь", "Активен", "2024-01-15"],
            [2, "Туфли классические", "Классическая обувь", "Активен", "2024-01-16"],
            [3, "Ботинки зимние", "Зимняя обувь", "В разработке", "2024-01-17"],
            [4, "Сандалии летние", "Летняя обувь", "Архив", "2024-01-18"],
            [5, "Балетки женские", "Женская обувь", "Активен", "2024-01-19"],
        ]

        self.demo_table.set_data(demo_data)
        layout.addWidget(self.demo_table)

        return widget

    def _create_forms_demo(self):
        """Демонстрация форм"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Кнопка открытия формы модели
        form_group = FormGroupBox("Демонстрация формы модели")
        form_layout = QVBoxLayout(form_group)

        info_label = QLabel(
            "Новая форма создания модели включает:\n"
            "• Современный дизайн с вкладками\n"
            "• Валидацию полей в реальном времени\n"
            "• Уведомления об ошибках\n"
            "• Индикаторы загрузки\n"
            "• Красивые стили"
        )
        info_label.setStyleSheet(f"color: {AppColors.TEXT_SECONDARY}; padding: 8px;")
        form_layout.addWidget(info_label)

        open_form_btn = StyledButton("Открыть форму создания модели", AppIcons.MODEL, StyledButton.STYLE_PRIMARY)
        open_form_btn.clicked.connect(self._open_model_form)
        form_layout.addWidget(open_form_btn)

        layout.addWidget(form_group)
        layout.addStretch()

        return widget

    def _toggle_loading(self):
        """Переключение индикатора загрузки"""
        if self.loading_widget.isVisible():
            self.loading_widget.hide()
        else:
            self.loading_widget.show()

    def _open_model_form(self):
        """Открытие формы модели"""
        try:
            form = ModelSpecificationFormV6(parent=self)
            form.exec()
        except Exception as e:
            print(f"Ошибка открытия формы: {e}")


def main():
    """Главная функция тестирования"""
    app = QApplication(sys.argv)

    # Установка информации о приложении
    app.setApplicationName("KRAI UI Components Test")
    app.setApplicationVersion("0.4")
    app.setOrganizationName("KRAI")

    # Создание и показ окна
    window = ComponentsTestWindow()
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())