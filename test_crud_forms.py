#!/usr/bin/env python3
"""
Тестовый скрипт для проверки CRUD форм справочников
"""
import sys
from PyQt6.QtWidgets import QApplication, QVBoxLayout, QWidget, QPushButton

def test_perforation_types():
    """Тестирование формы типов перфорации"""
    try:
        from ui.references.perforation_types_view import PerforationTypesTableWidget
        widget = PerforationTypesTableWidget()
        widget.show()
        print("✅ Форма типов перфорации успешно открыта")
        return widget
    except Exception as e:
        print(f"❌ Ошибка открытия формы типов перфорации: {e}")
        return None

def test_lining_types():
    """Тестирование формы типов подкладки"""
    try:
        from ui.references.lining_types_view import LiningTypesTableWidget
        widget = LiningTypesTableWidget()
        widget.show()
        print("✅ Форма типов подкладки успешно открыта")
        return widget
    except Exception as e:
        print(f"❌ Ошибка открытия формы типов подкладки: {e}")
        return None

def test_cutting_parts():
    """Тестирование формы деталей раскроя"""
    try:
        from ui.references.cutting_parts_view import CuttingPartsTableWidget
        widget = CuttingPartsTableWidget()
        widget.show()
        print("✅ Форма деталей раскроя успешно открыта")
        return widget
    except Exception as e:
        print(f"❌ Ошибка открытия формы деталей раскроя: {e}")
        return None

class TestWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Тестирование CRUD форм")
        self.setGeometry(100, 100, 300, 200)

        layout = QVBoxLayout()

        # Кнопки для тестирования каждой формы
        btn_perf = QPushButton("Тест: Типы перфорации")
        btn_perf.clicked.connect(test_perforation_types)
        layout.addWidget(btn_perf)

        btn_lining = QPushButton("Тест: Типы подкладки")
        btn_lining.clicked.connect(test_lining_types)
        layout.addWidget(btn_lining)

        btn_cutting = QPushButton("Тест: Детали раскроя")
        btn_cutting.clicked.connect(test_cutting_parts)
        layout.addWidget(btn_cutting)

        self.setLayout(layout)

def main():
    app = QApplication(sys.argv)

    print("🧪 Запуск тестирования CRUD форм...")

    # Создаем тестовое окно
    test_window = TestWindow()
    test_window.show()

    print("📋 Нажмите кнопки для тестирования каждой формы")
    print("🔍 Проверьте:")
    print("  - Открывается ли форма")
    print("  - Загружаются ли данные из БД")
    print("  - Работают ли кнопки Добавить/Редактировать/Удалить")

    sys.exit(app.exec())

if __name__ == "__main__":
    main()