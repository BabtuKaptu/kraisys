"""Unified References view with sidebar navigation"""
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class ReferencesMainView(QWidget):
    """Главный виджет справочников с боковым меню"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_reference = None
        self.setup_ui()

    def setup_ui(self):
        """Настройка UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Левая панель - навигация
        self.setup_sidebar(layout)

        # Разделитель
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)

        # Правая панель - содержимое
        self.content_widget = QStackedWidget()
        splitter.addWidget(self.sidebar_widget)
        splitter.addWidget(self.content_widget)

        # Устанавливаем пропорции: 250px для sidebar, остальное для контента
        splitter.setSizes([250, 800])
        splitter.setChildrenCollapsible(False)

        # Загружаем справочники
        self.load_references()

    def setup_sidebar(self, parent_layout):
        """Настройка боковой панели"""
        self.sidebar_widget = QWidget()
        self.sidebar_widget.setMaximumWidth(250)
        self.sidebar_widget.setMinimumWidth(200)

        # Стиль боковой панели
        self.sidebar_widget.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                border-right: 1px solid #ddd;
            }
            QListWidget {
                background-color: transparent;
                border: none;
                font-size: 14px;
                selection-background-color: #0078d4;
                selection-color: white;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #eee;
            }
            QListWidget::item:hover {
                background-color: #e1f5fe;
            }
            QLabel {
                font-weight: bold;
                font-size: 16px;
                padding: 15px 10px 10px 10px;
                color: #333;
            }
        """)

        sidebar_layout = QVBoxLayout(self.sidebar_widget)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)

        # Заголовок
        title_label = QLabel("Справочники")
        sidebar_layout.addWidget(title_label)

        # Список справочников
        self.references_list = QListWidget()
        self.references_list.itemClicked.connect(self.on_reference_selected)
        sidebar_layout.addWidget(self.references_list)

        sidebar_layout.addStretch()

    def load_references(self):
        """Загружает список справочников"""
        references = [
            ("perforation_types", "🔹 Типы перфорации"),
            ("lining_types", "🔹 Типы подкладки"),
            ("cutting_parts", "🔹 Детали раскроя"),
            ("lasting_types", "🔹 Типы затяжки")
        ]

        for ref_id, ref_title in references:
            item = QListWidgetItem(ref_title)
            item.setData(Qt.ItemDataRole.UserRole, ref_id)
            self.references_list.addItem(item)

        # Загружаем виджеты справочников
        self.load_reference_widgets()

        # Выбираем первый элемент по умолчанию
        if self.references_list.count() > 0:
            self.references_list.setCurrentRow(0)
            self.on_reference_selected(self.references_list.item(0))

    def load_reference_widgets(self):
        """Загружает виджеты для каждого справочника"""
        try:
            # Загружаем все виджеты справочников
            from ui.references.perforation_types_view import PerforationTypesTableWidget
            from ui.references.lining_types_view import LiningTypesTableWidget
            from ui.references.cutting_parts_view import CuttingPartsTableWidget
            from ui.references.lasting_types_view import LastingTypesTableWidget

            # Создаем виджеты
            self.perforation_widget = PerforationTypesTableWidget()
            self.lining_widget = LiningTypesTableWidget()
            self.cutting_widget = CuttingPartsTableWidget()
            self.lasting_widget = LastingTypesTableWidget()

            # Добавляем в стек
            self.content_widget.addWidget(self.perforation_widget)
            self.content_widget.addWidget(self.lining_widget)
            self.content_widget.addWidget(self.cutting_widget)
            self.content_widget.addWidget(self.lasting_widget)

            print("✅ Все виджеты справочников загружены")

        except Exception as e:
            print(f"❌ Ошибка загрузки виджетов справочников: {e}")
            import traceback
            traceback.print_exc()

            # Добавляем заглушку при ошибке
            error_label = QLabel(f"Ошибка загрузки справочников:\n{e}")
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            error_label.setStyleSheet("color: red; font-size: 14px; padding: 20px;")
            self.content_widget.addWidget(error_label)

    def on_reference_selected(self, item):
        """Обработчик выбора справочника"""
        if not item:
            return

        ref_id = item.data(Qt.ItemDataRole.UserRole)

        # Маппинг справочников к индексам в стеке
        ref_mapping = {
            "perforation_types": 0,
            "lining_types": 1,
            "cutting_parts": 2,
            "lasting_types": 3
        }

        if ref_id in ref_mapping:
            self.content_widget.setCurrentIndex(ref_mapping[ref_id])
            self.current_reference = ref_id
            print(f"✅ Переключились на справочник: {item.text()}")
        else:
            print(f"❌ Неизвестный справочник: {ref_id}")


def main():
    """Тестовая функция"""
    import sys
    app = QApplication(sys.argv)
    window = ReferencesMainView()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()