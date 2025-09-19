"""Main window for KRAI Desktop Application"""
print("🔥 ЗАГРУЖАЕТСЯ main_window.py - НАЧАЛО ФАЙЛА")
from PyQt6.QtWidgets import (
    QMainWindow, QTabWidget, QMessageBox, QStatusBar, QLabel,
    QHBoxLayout, QWidget, QVBoxLayout, QSplashScreen
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QAction, QPixmap, QPainter, QFont
from ui.styles.app_styles import AppStyles, AppColors, AppIcons
print("🔥 ИМПОРТЫ main_window.py ЗАВЕРШЕНЫ")

class MainWindow(QMainWindow):
    """Главное окно приложения"""

    def __init__(self):
        super().__init__()
        print("🔥 MainWindow __init__ ВЫЗВАН")

        # Настройка окна
        self.setWindowTitle(f"{AppIcons.MODEL} KRAI Production System v0.4")
        self.setGeometry(100, 100, 1400, 900)
        self.setMinimumSize(1200, 700)

        # Применение стилей
        self.setStyleSheet(AppStyles.get_combined_style())

        print("🔥 ВЫЗЫВАЮ setup_ui()")
        self.setup_ui()
        print("🔥 ВЫЗЫВАЮ setup_menu()")
        self.setup_menu()
        print("🔥 ВЫЗЫВАЮ setup_status_bar()")
        self.setup_status_bar()
        print("🔥 MainWindow __init__ ЗАВЕРШЕН")

    def setup_ui(self):
        # Центральный виджет с табами
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Добавляем вкладки
        from PyQt6.QtWidgets import QLabel

        try:
            from ui.references.models_view_full import ModelsTableFullWidget as ModelsTableWidget
            from ui.references.materials_view_full import MaterialsTableFullWidget as MaterialsTableWidget
            from ui.warehouse.warehouse_view import WarehouseWidget

            self.models_widget = ModelsTableWidget()
            self.materials_widget = MaterialsTableWidget()
            self.stock_widget = WarehouseWidget()
        except Exception as e:
            print(f"Error loading views: {e}")
            # Заглушки при ошибке
            self.models_widget = QLabel("Модели обуви - Ошибка загрузки")
            self.models_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.materials_widget = QLabel("Материалы - Ошибка загрузки")
            self.materials_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.stock_widget = QLabel("Склад - Ошибка загрузки")
            self.stock_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.orders_widget = QLabel("Заказы - В разработке")
        self.orders_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Добавляем основные табы с иконками
        self.tabs.addTab(self.models_widget, f"{AppIcons.MODEL} Модели")
        self.tabs.addTab(self.materials_widget, f"{AppIcons.MATERIAL} Материалы")
        self.tabs.addTab(self.stock_widget, f"📦 Склад")
        self.tabs.addTab(self.orders_widget, f"📋 Заказы")

        # Добавляем единую вкладку справочников
        try:
            from ui.references.references_main_view import ReferencesMainView
            self.references_widget = ReferencesMainView()
            self.tabs.addTab(self.references_widget, "📚 Справочники")
            print("✅ Единая вкладка справочников добавлена успешно")
        except Exception as e:
            print(f"❌ Ошибка загрузки вкладки справочников: {e}")
            import traceback
            traceback.print_exc()
            # Заглушка при ошибке
            error_widget = QLabel("Справочники - Ошибка загрузки")
            error_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tabs.addTab(error_widget, "📚 Справочники")

        print("✅ Все виджеты справочников загружены")

    def setup_menu(self):
        menubar = self.menuBar()

        # Меню Файл
        file_menu = menubar.addMenu("Файл")

        exit_action = QAction("Выход", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Меню Справочники (теперь просто для навигации по табам)
        ref_menu = menubar.addMenu("Справочники")

        models_action = QAction("Модели обуви", self)
        models_action.triggered.connect(lambda: self.tabs.setCurrentIndex(0))
        ref_menu.addAction(models_action)

        materials_action = QAction("Материалы", self)
        materials_action.triggered.connect(lambda: self.tabs.setCurrentIndex(1))
        ref_menu.addAction(materials_action)

        ref_menu.addSeparator()

        # Навигация к справочникам (теперь все в одной вкладке)
        all_refs_action = QAction("Все справочники", self)
        all_refs_action.triggered.connect(lambda: self.tabs.setCurrentIndex(4))  # Вкладка "Справочники"
        ref_menu.addAction(all_refs_action)

        print("✅ Меню навигации к единой вкладке справочников настроено")

        # Меню Склад
        warehouse_menu = menubar.addMenu("Склад")

        stock_action = QAction("Остатки", self)
        stock_action.triggered.connect(lambda: self.tabs.setCurrentIndex(2))
        warehouse_menu.addAction(stock_action)

        # Меню Производство
        prod_menu = menubar.addMenu("Производство")

        orders_action = QAction("Заказы", self)
        orders_action.triggered.connect(lambda: self.tabs.setCurrentIndex(3))
        prod_menu.addAction(orders_action)

        # Меню Помощь
        help_menu = menubar.addMenu("Помощь")

        about_action = QAction("О программе", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def setup_status_bar(self):
        """Настройка красивого статус-бара"""
        self.status_bar = self.statusBar()

        # Основное сообщение
        self.status_message = QLabel(f"{AppIcons.SUCCESS} Готов к работе")
        self.status_bar.addWidget(self.status_message)

        # Добавляем отступ
        self.status_bar.addPermanentWidget(QLabel(""), 1)

        # Версия приложения
        version_label = QLabel("v0.4")
        version_label.setStyleSheet(f"color: {AppColors.TEXT_SECONDARY}; font-size: 12px;")
        self.status_bar.addPermanentWidget(version_label)

        # Настраиваем стиль статус-бара
        self.status_bar.setStyleSheet(f"""
            QStatusBar {{
                background-color: {AppColors.SURFACE};
                color: {AppColors.TEXT_PRIMARY};
                border-top: 1px solid {AppColors.LIGHT_GRAY};
            }}
            QStatusBar::item {{
                border: none;
            }}
        """)

    def update_status(self, message, icon=AppIcons.INFO, timeout=3000):
        """Обновление статуса с временным сообщением"""
        if hasattr(self, 'status_message'):
            self.status_message.setText(f"{icon} {message}")
            if timeout > 0:
                QTimer.singleShot(timeout, lambda: self.status_message.setText(f"{AppIcons.SUCCESS} Готов к работе"))

    def show_about(self):
        QMessageBox.about(self, f"{AppIcons.ABOUT} О программе",
                         f"{AppIcons.MODEL} KRAI Production System v0.4\n\n"
                         "Система управления производством обуви\n"
                         f"{AppIcons.SUCCESS} Версия 0.4 - Красивый интерфейс\n"
                         "© 2024 KRAI")

