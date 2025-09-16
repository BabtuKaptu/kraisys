"""
Улучшенные виджеты с красивыми стилями для KRAI Desktop
"""

from PyQt6.QtWidgets import (
    QPushButton, QLineEdit, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox,
    QLabel, QHBoxLayout, QVBoxLayout, QWidget, QFrame, QProgressBar, QGroupBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtGui import QFont, QPalette, QColor
from ui.styles.app_styles import AppColors, AppIcons, AppFonts


class StyledButton(QPushButton):
    """Улучшенная кнопка с различными стилями"""

    STYLE_PRIMARY = "primary"
    STYLE_SECONDARY = "secondary"
    STYLE_SUCCESS = "success"
    STYLE_WARNING = "warning"
    STYLE_ERROR = "error"

    def __init__(self, text="", icon="", style=STYLE_PRIMARY, parent=None):
        if icon and text:
            super().__init__(f"{icon} {text}", parent)
        elif icon:
            super().__init__(icon, parent)
        else:
            super().__init__(text, parent)

        self.button_style = style
        self._setup_style()

    def _setup_style(self):
        """Настройка стиля кнопки"""
        self.setProperty("class", self.button_style)

        # Базовые стили для всех кнопок
        base_style = f"""
            QPushButton {{
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: 500;
                font-size: 14px;
                min-height: 32px;
                min-width: 80px;
            }}
        """

        # Специфичные стили для каждого типа
        if self.button_style == self.STYLE_PRIMARY:
            style = base_style + f"""
                QPushButton {{
                    background-color: {AppColors.PRIMARY};
                    color: {AppColors.TEXT_ON_PRIMARY};
                }}
                QPushButton:hover {{
                    background-color: {AppColors.PRIMARY_DARK};
                }}
                QPushButton:pressed {{
                    background-color: {AppColors.PRIMARY_DARK};
                }}
            """
        elif self.button_style == self.STYLE_SECONDARY:
            style = base_style + f"""
                QPushButton {{
                    background-color: {AppColors.SURFACE};
                    color: {AppColors.PRIMARY};
                    border: 2px solid {AppColors.PRIMARY};
                }}
                QPushButton:hover {{
                    background-color: {AppColors.PRIMARY_LIGHT};
                }}
            """
        elif self.button_style == self.STYLE_SUCCESS:
            style = base_style + f"""
                QPushButton {{
                    background-color: {AppColors.SUCCESS};
                    color: {AppColors.TEXT_ON_PRIMARY};
                }}
                QPushButton:hover {{
                    background-color: #45a049;
                }}
            """
        elif self.button_style == self.STYLE_WARNING:
            style = base_style + f"""
                QPushButton {{
                    background-color: {AppColors.WARNING};
                    color: {AppColors.TEXT_ON_PRIMARY};
                }}
                QPushButton:hover {{
                    background-color: {AppColors.SECONDARY_DARK};
                }}
            """
        elif self.button_style == self.STYLE_ERROR:
            style = base_style + f"""
                QPushButton {{
                    background-color: {AppColors.ERROR};
                    color: {AppColors.TEXT_ON_PRIMARY};
                }}
                QPushButton:hover {{
                    background-color: #d32f2f;
                }}
            """

        self.setStyleSheet(style)


class ValidatedLineEdit(QLineEdit):
    """Поле ввода с валидацией и визуальной обратной связью"""

    validationChanged = pyqtSignal(bool)  # Сигнал изменения валидации

    def __init__(self, placeholder="", required=False, validator_func=None, parent=None):
        super().__init__(parent)
        self.is_required = required
        self.validator_func = validator_func
        self._is_valid = True

        if placeholder:
            self.setPlaceholderText(placeholder)

        # Подключение сигналов
        self.textChanged.connect(self._on_text_changed)

        self._setup_style()

    def _setup_style(self):
        """Настройка базового стиля"""
        style = f"""
            QLineEdit {{
                background-color: {AppColors.SURFACE};
                color: {AppColors.TEXT_PRIMARY};
                border: 2px solid {AppColors.LIGHT_GRAY};
                border-radius: 6px;
                padding: 8px;
                font-size: 14px;
                min-height: 32px;
            }}
            QLineEdit:focus {{
                border-color: {AppColors.PRIMARY};
                outline: none;
            }}
        """
        self.setStyleSheet(style)

    def _on_text_changed(self):
        """Обработка изменения текста"""
        self._validate()

    def _validate(self):
        """Валидация значения"""
        text = self.text().strip()
        is_valid = True

        # Проверка обязательности
        if self.is_required and not text:
            is_valid = False

        # Кастомная валидация
        if is_valid and self.validator_func and text:
            is_valid = self.validator_func(text)

        # Обновление стиля
        if is_valid != self._is_valid:
            self._is_valid = is_valid
            self._update_validation_style()
            self.validationChanged.emit(is_valid)

    def _update_validation_style(self):
        """Обновление стиля в зависимости от валидации"""
        if self._is_valid:
            border_color = AppColors.PRIMARY if self.hasFocus() else AppColors.LIGHT_GRAY
        else:
            border_color = AppColors.ERROR

        style = f"""
            QLineEdit {{
                background-color: {AppColors.SURFACE};
                color: {AppColors.TEXT_PRIMARY};
                border: 2px solid {border_color};
                border-radius: 6px;
                padding: 8px;
                font-size: 14px;
                min-height: 32px;
            }}
            QLineEdit:focus {{
                border-color: {AppColors.PRIMARY if self._is_valid else AppColors.ERROR};
                outline: none;
            }}
        """
        self.setStyleSheet(style)

    def is_valid(self):
        """Проверка валидности"""
        return self._is_valid

    def set_error(self, show_error=True):
        """Принудительная установка состояния ошибки"""
        self._is_valid = not show_error
        self._update_validation_style()


class FormGroupBox(QGroupBox):
    """Красивая группирующая рамка для форм"""

    def __init__(self, title="", parent=None):
        super().__init__(title, parent)
        self._setup_style()

    def _setup_style(self):
        """Настройка стиля группы"""
        style = f"""
            QGroupBox {{
                font-weight: 500;
                font-size: 16px;
                color: {AppColors.TEXT_PRIMARY};
                border: 2px solid {AppColors.LIGHT_GRAY};
                border-radius: 8px;
                margin-top: 16px;
                padding-top: 8px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 16px;
                padding: 0 8px 0 8px;
                background-color: {AppColors.SURFACE};
                color: {AppColors.PRIMARY};
            }}
        """
        self.setStyleSheet(style)


class LoadingWidget(QWidget):
    """Виджет загрузки с прогресс-баром"""

    def __init__(self, message="Загрузка...", parent=None):
        super().__init__(parent)
        self.message = message
        self._setup_ui()

    def _setup_ui(self):
        """Настройка интерфейса"""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Иконка загрузки
        icon_label = QLabel("⏳")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet(f"font-size: 32px; color: {AppColors.PRIMARY};")
        layout.addWidget(icon_label)

        # Сообщение
        message_label = QLabel(self.message)
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message_label.setStyleSheet(f"font-size: 14px; color: {AppColors.TEXT_SECONDARY}; margin: 8px;")
        layout.addWidget(message_label)

        # Прогресс-бар
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)  # Неопределённый прогресс
        self.progress.setStyleSheet(f"""
            QProgressBar {{
                border: 2px solid {AppColors.LIGHT_GRAY};
                border-radius: 5px;
                text-align: center;
                font-size: 12px;
                color: {AppColors.TEXT_PRIMARY};
                background-color: {AppColors.SURFACE_VARIANT};
            }}
            QProgressBar::chunk {{
                background-color: {AppColors.PRIMARY};
                border-radius: 3px;
            }}
        """)
        layout.addWidget(self.progress)

    def set_message(self, message):
        """Изменение сообщения"""
        self.message = message
        # Найти и обновить label с сообщением
        for child in self.findChildren(QLabel):
            if child.text() != "⏳":
                child.setText(message)
                break


class NotificationBar(QFrame):
    """Полоса уведомлений"""

    TYPE_INFO = "info"
    TYPE_SUCCESS = "success"
    TYPE_WARNING = "warning"
    TYPE_ERROR = "error"

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self.hide()  # Скрыт по умолчанию

    def _setup_ui(self):
        """Настройка интерфейса"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 8)

        self.icon_label = QLabel()
        self.message_label = QLabel()
        self.close_button = StyledButton("❌", style=StyledButton.STYLE_SECONDARY)
        self.close_button.setMaximumSize(24, 24)
        self.close_button.clicked.connect(self.hide)

        layout.addWidget(self.icon_label)
        layout.addWidget(self.message_label, 1)
        layout.addWidget(self.close_button)

    def show_notification(self, message, notification_type=TYPE_INFO, timeout=5000):
        """Показать уведомление"""
        # Установка иконки и цвета
        colors = {
            self.TYPE_INFO: (AppColors.INFO, AppColors.INFO_LIGHT, AppIcons.INFO),
            self.TYPE_SUCCESS: (AppColors.SUCCESS, AppColors.SUCCESS_LIGHT, AppIcons.SUCCESS),
            self.TYPE_WARNING: (AppColors.WARNING, AppColors.WARNING_LIGHT, AppIcons.WARNING),
            self.TYPE_ERROR: (AppColors.ERROR, AppColors.ERROR_LIGHT, AppIcons.ERROR),
        }

        color, bg_color, icon = colors.get(notification_type, colors[self.TYPE_INFO])

        self.icon_label.setText(icon)
        self.message_label.setText(message)

        # Стиль
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border: 1px solid {color};
                border-radius: 6px;
                color: {AppColors.TEXT_PRIMARY};
            }}
        """)

        self.show()

        # Автоматическое скрытие
        if timeout > 0:
            QTimer.singleShot(timeout, self.hide)


class ButtonGroup(QWidget):
    """Группа кнопок для форм"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addStretch()  # Выравнивание по правому краю

    def add_button(self, text, icon="", style=StyledButton.STYLE_PRIMARY, callback=None):
        """Добавить кнопку в группу"""
        button = StyledButton(text, icon, style)
        if callback:
            button.clicked.connect(callback)
        self.layout.addWidget(button)
        return button

    def add_save_cancel_buttons(self, save_callback=None, cancel_callback=None):
        """Добавить стандартные кнопки Сохранить/Отмена"""
        cancel_btn = self.add_button("Отмена", AppIcons.CANCEL, StyledButton.STYLE_SECONDARY, cancel_callback)
        save_btn = self.add_button("Сохранить", AppIcons.SAVE, StyledButton.STYLE_SUCCESS, save_callback)
        return save_btn, cancel_btn


# Удобные функции для создания компонентов
def create_form_row(label_text, widget, required=False):
    """Создать строку формы с подписью и виджетом"""
    row = QWidget()
    layout = QHBoxLayout(row)
    layout.setContentsMargins(0, 0, 0, 0)

    # Подпись
    label = QLabel(label_text + ("*" if required else ""))
    label.setStyleSheet(f"""
        QLabel {{
            color: {AppColors.TEXT_PRIMARY};
            font-weight: 500;
            min-width: 120px;
        }}
    """)
    if required:
        label.setStyleSheet(label.styleSheet() + f"QLabel {{ color: {AppColors.ERROR}; }}")

    layout.addWidget(label)
    layout.addWidget(widget, 1)

    return row


def create_field_with_validation(label_text, placeholder="", required=False, validator_func=None):
    """Создать поле с валидацией"""
    field = ValidatedLineEdit(placeholder, required, validator_func)
    row = create_form_row(label_text, field, required)
    return row, field