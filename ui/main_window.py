"""Main window for KRAI Desktop Application"""
print("🔥 ЗАГРУЖАЕТСЯ main_window.py - НАЧАЛО ФАЙЛА")
from PyQt6.QtWidgets import QMainWindow, QTabWidget, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
print("🔥 ИМПОРТЫ main_window.py ЗАВЕРШЕНЫ")

class MainWindow(QMainWindow):
    """Главное окно приложения"""

    def __init__(self):
        super().__init__()
        print("🔥 MainWindow __init__ ВЫЗВАН")
        self.setWindowTitle("KRAI Production System")
        self.setGeometry(100, 100, 1400, 900)
        print("🔥 ВЫЗЫВАЮ setup_ui()")
        self.setup_ui()
        print("🔥 ВЫЗЫВАЮ setup_menu()")
        self.setup_menu()
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

        # Добавляем основные табы
        self.tabs.addTab(self.models_widget, "Модели")
        self.tabs.addTab(self.materials_widget, "Материалы")
        self.tabs.addTab(self.stock_widget, "Склад")
        self.tabs.addTab(self.orders_widget, "Заказы")

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

        # Статус бар
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Готов к работе")

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

    def show_about(self):
        QMessageBox.about(self, "О программе",
                         "KRAI Production System v1.0\n\n"
                         "Система управления производством обуви\n"
                         "© 2024 KRAI")

