"""
Базовый класс для боковых панелей форм
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QLabel,
    QPushButton, QScrollArea, QFrame
)
from PyQt6.QtCore import Qt, QPropertyAnimation, QRect, pyqtSignal, QEasingCurve
from PyQt6.QtGui import QPalette


class SidePanelForm(QWidget):
    """Базовый класс для боковых панелей форм"""

    closed = pyqtSignal()
    saved = pyqtSignal()

    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.title = title
        self.panel_width = 480
        self.is_visible = False

        self.setup_ui()
        self.setup_animations()
        self.setup_styles()

    def setup_ui(self):
        """Настройка основной структуры панели"""
        self.setFixedWidth(self.panel_width)
        self.setWindowFlags(Qt.WindowType.Widget)

        # Основной layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header (sticky)
        self.setup_header(main_layout)

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.TabPosition.North)

        # Scroll area for tabs content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.tabs)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        main_layout.addWidget(scroll_area, 1)  # stretch

        # Footer (sticky)
        self.setup_footer(main_layout)

    def setup_header(self, main_layout):
        """Создание заголовка панели"""
        header_frame = QFrame()
        header_frame.setFixedHeight(60)
        header_frame.setObjectName("header_frame")

        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 15, 15, 15)

        # Заголовок
        self.title_label = QLabel(self.title)
        self.title_label.setObjectName("panel_title")
        header_layout.addWidget(self.title_label)

        header_layout.addStretch()

        # Кнопка закрытия
        self.close_btn = QPushButton("✕")
        self.close_btn.setFixedSize(30, 30)
        self.close_btn.setObjectName("close_btn")
        self.close_btn.clicked.connect(self.hide_panel)
        header_layout.addWidget(self.close_btn)

        main_layout.addWidget(header_frame)

    def setup_footer(self, main_layout):
        """Создание футера с кнопками"""
        footer_frame = QFrame()
        footer_frame.setFixedHeight(60)
        footer_frame.setObjectName("footer_frame")

        footer_layout = QHBoxLayout(footer_frame)
        footer_layout.setContentsMargins(20, 10, 20, 10)

        footer_layout.addStretch()

        # Кнопка отмены
        self.cancel_btn = QPushButton("Отмена")
        self.cancel_btn.setObjectName("secondary_btn")
        self.cancel_btn.clicked.connect(self.hide_panel)
        footer_layout.addWidget(self.cancel_btn)

        # Кнопка сохранения
        self.save_btn = QPushButton("Сохранить")
        self.save_btn.setObjectName("primary_btn")
        self.save_btn.clicked.connect(self.handle_save)
        footer_layout.addWidget(self.save_btn)

        main_layout.addWidget(footer_frame)

    def setup_animations(self):
        """Настройка анимаций"""
        self.slide_animation = QPropertyAnimation(self, b"geometry")
        self.slide_animation.setDuration(300)
        self.slide_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)

    def setup_styles(self):
        """Применение стилей"""
        self.setStyleSheet("""
            SidePanelForm {
                background-color: #ffffff;
                border-left: 1px solid #e2e8f0;
            }

            #header_frame {
                background-color: #f8fafc;
                border-bottom: 1px solid #e2e8f0;
            }

            #footer_frame {
                background-color: #f8fafc;
                border-top: 1px solid #e2e8f0;
            }

            #panel_title {
                font-size: 16px;
                font-weight: 600;
                color: #1e293b;
            }

            #close_btn {
                background-color: transparent;
                border: none;
                color: #64748b;
                font-size: 16px;
                border-radius: 15px;
            }

            #close_btn:hover {
                background-color: #f1f5f9;
                color: #1e293b;
            }

            #primary_btn {
                background-color: #2563eb;
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 8px;
                font-weight: 500;
                min-width: 100px;
            }

            #primary_btn:hover {
                background-color: #3b82f6;
            }

            #secondary_btn {
                background-color: white;
                color: #64748b;
                border: 1px solid #e2e8f0;
                padding: 12px 20px;
                border-radius: 8px;
                font-weight: 500;
                min-width: 100px;
                margin-right: 10px;
            }

            #secondary_btn:hover {
                background-color: #f8fafc;
                color: #1e293b;
            }

            QTabWidget::pane {
                border: none;
                background-color: white;
            }

            QTabBar::tab {
                background-color: transparent;
                border: none;
                padding: 12px 16px;
                margin-right: 4px;
                color: #64748b;
                font-weight: 500;
            }

            QTabBar::tab:selected {
                color: #2563eb;
                border-bottom: 2px solid #2563eb;
            }

            QTabBar::tab:hover {
                background-color: #f1f5f9;
                color: #1e293b;
            }
        """)

    def show_panel(self):
        """Показать панель с анимацией"""
        if self.is_visible:
            return

        parent = self.parent()
        if not parent:
            return

        # Позиционируем панель за правым краем
        parent_rect = parent.rect()
        start_rect = QRect(
            parent_rect.width(),
            0,
            self.panel_width,
            parent_rect.height()
        )
        end_rect = QRect(
            parent_rect.width() - self.panel_width,
            0,
            self.panel_width,
            parent_rect.height()
        )

        self.setGeometry(start_rect)
        self.show()

        # Анимация
        self.slide_animation.setStartValue(start_rect)
        self.slide_animation.setEndValue(end_rect)
        self.slide_animation.finished.connect(self.on_show_finished)
        self.slide_animation.start()

    def hide_panel(self):
        """Скрыть панель с анимацией"""
        if not self.is_visible:
            self.close()
            return

        parent = self.parent()
        if not parent:
            self.close()
            return

        # Анимация исчезновения
        current_rect = self.geometry()
        end_rect = QRect(
            parent.rect().width(),
            current_rect.y(),
            current_rect.width(),
            current_rect.height()
        )

        self.slide_animation.setStartValue(current_rect)
        self.slide_animation.setEndValue(end_rect)
        self.slide_animation.finished.connect(self.on_hide_finished)
        self.slide_animation.start()

    def on_show_finished(self):
        """Завершение анимации показа"""
        self.is_visible = True
        self.slide_animation.finished.disconnect()

    def on_hide_finished(self):
        """Завершение анимации скрытия"""
        self.is_visible = False
        self.slide_animation.finished.disconnect()
        self.close()
        self.closed.emit()

    def handle_save(self):
        """Обработка сохранения - переопределяется в наследниках"""
        self.saved.emit()
        self.hide_panel()

    def resizeEvent(self, event):
        """Обработка изменения размера родителя"""
        super().resizeEvent(event)
        if self.is_visible and self.parent():
            parent_rect = self.parent().rect()
            new_rect = QRect(
                parent_rect.width() - self.panel_width,
                0,
                self.panel_width,
                parent_rect.height()
            )
            self.setGeometry(new_rect)