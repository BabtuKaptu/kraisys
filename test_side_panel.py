"""
Тест боковой панели - демонстрация каркаса
"""
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel
from PyQt6.QtCore import Qt

from ui.components.side_panel_form import SidePanelForm


class TestSidePanel(SidePanelForm):
    """Тестовая боковая панель для демонстрации"""

    def __init__(self, parent=None):
        super().__init__("Тест боковой панели", parent)

        # Добавляем тестовые табы
        self.setup_test_tabs()

    def setup_test_tabs(self):
        """Создание тестовых табов"""

        # Таб 1: Основное
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.addWidget(QLabel("Это таб 'Основное'"))
        main_layout.addWidget(QLabel("Здесь будет основная информация модели"))
        main_layout.addStretch()
        self.tabs.addTab(main_widget, "Основное")

        # Таб 2: Параметры
        params_widget = QWidget()
        params_layout = QVBoxLayout(params_widget)
        params_layout.addWidget(QLabel("Это таб 'Параметры'"))
        params_layout.addWidget(QLabel("Здесь будут параметры модели"))
        params_layout.addStretch()
        self.tabs.addTab(params_widget, "Параметры")

        # Таб 3: Детали
        details_widget = QWidget()
        details_layout = QVBoxLayout(details_widget)
        details_layout.addWidget(QLabel("Это таб 'Детали'"))
        details_layout.addWidget(QLabel("Здесь будут детали кроя"))
        details_layout.addStretch()
        self.tabs.addTab(details_widget, "Детали")


class TestMainWindow(QMainWindow):
    """Главное окно для тестирования"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Тест боковой панели")
        self.setGeometry(100, 100, 1000, 700)

        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        # Заголовок
        title = QLabel("Демонстрация боковой панели Version 0.6")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 20px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Описание
        description = QLabel(
            "Нажмите кнопки ниже, чтобы открыть боковые панели разных типов.\n"
            "Панели появляются справа с плавной анимацией."
        )
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description.setStyleSheet("color: gray; margin: 10px;")
        layout.addWidget(description)

        layout.addStretch()

        # Кнопки для тестирования
        buttons_layout = QVBoxLayout()
        buttons_layout.setSpacing(10)

        # Кнопка 1: Новая модель
        btn_new_model = QPushButton("🆕 Новая базовая модель")
        btn_new_model.setStyleSheet("""
            QPushButton {
                padding: 12px 20px;
                font-size: 14px;
                background-color: #2563eb;
                color: white;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #3b82f6;
            }
        """)
        btn_new_model.clicked.connect(self.show_new_model_panel)
        buttons_layout.addWidget(btn_new_model)

        # Кнопка 2: Новый вариант
        btn_new_variant = QPushButton("🎨 Новый вариант")
        btn_new_variant.setStyleSheet("""
            QPushButton {
                padding: 12px 20px;
                font-size: 14px;
                background-color: #059669;
                color: white;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #10b981;
            }
        """)
        btn_new_variant.clicked.connect(self.show_new_variant_panel)
        buttons_layout.addWidget(btn_new_variant)

        # Кнопка 3: Редактирование
        btn_edit = QPushButton("✏️ Редактировать модель")
        btn_edit.setStyleSheet("""
            QPushButton {
                padding: 12px 20px;
                font-size: 14px;
                background-color: #dc2626;
                color: white;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #ef4444;
            }
        """)
        btn_edit.clicked.connect(self.show_edit_panel)
        buttons_layout.addWidget(btn_edit)

        layout.addLayout(buttons_layout)
        layout.addStretch()

        # Инструкции
        instructions = QLabel(
            "💡 Боковая панель:\n"
            "• Открывается справа с анимацией\n"
            "• Содержит табы для разных разделов\n"
            "• Кнопка ✕ или 'Отмена' закрывает панель\n"
            "• Кнопка 'Сохранить' эмулирует сохранение"
        )
        instructions.setStyleSheet("""
            background-color: #f0f8ff;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #2563eb;
        """)
        layout.addWidget(instructions)

        # Переменная для текущей панели
        self.current_panel = None

    def show_new_model_panel(self):
        """Показать панель новой модели"""
        if self.current_panel:
            self.current_panel.hide_panel()

        self.current_panel = TestSidePanel(self)
        self.current_panel.title_label.setText("Новая базовая модель")
        self.current_panel.show_panel()

    def show_new_variant_panel(self):
        """Показать панель нового варианта"""
        if self.current_panel:
            self.current_panel.hide_panel()

        self.current_panel = TestSidePanel(self)
        self.current_panel.title_label.setText("Новый вариант: Хайкеры М")
        self.current_panel.show_panel()

    def show_edit_panel(self):
        """Показать панель редактирования"""
        if self.current_panel:
            self.current_panel.hide_panel()

        self.current_panel = TestSidePanel(self)
        self.current_panel.title_label.setText("Редактирование: Кроссовки летние")
        self.current_panel.show_panel()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Устанавливаем стиль приложения
    app.setStyleSheet("""
        QMainWindow {
            background-color: #f8fafc;
        }
        QWidget {
            font-family: 'Segoe UI', Arial, sans-serif;
        }
    """)

    window = TestMainWindow()
    window.show()

    sys.exit(app.exec())