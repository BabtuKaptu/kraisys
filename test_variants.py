#!/usr/bin/env python3
"""
Тестирование функциональности создания вариантов моделей
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel
from PyQt6.QtCore import Qt
from ui.references.model_specification_form_v4 import ModelSpecificationFormV4

class VariantTestWindow(QMainWindow):
    """Окно для тестирования функциональности вариантов"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Тестирование функциональности вариантов моделей")
        self.setGeometry(100, 100, 600, 400)

        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Информация
        info_label = QLabel("""
🧪 ТЕСТИРОВАНИЕ ФУНКЦИОНАЛЬНОСТИ ВАРИАНТОВ

1. Сначала создайте базовую модель с несколькими параметрами
2. Затем создайте специфический вариант этой модели
3. Проверьте ограничения для вариантов:
   ✓ Одиночный выбор параметров вместо множественного
   ✓ Только параметры из базовой модели
   ✓ Конкретные материалы для деталей кроя
        """)
        info_label.setWordWrap(True)
        info_label.setStyleSheet("padding: 20px; background: #f0f8ff; border-radius: 5px;")
        layout.addWidget(info_label)

        # Кнопки тестирования
        btn_create_base = QPushButton("📋 Создать базовую модель")
        btn_create_base.clicked.connect(self.create_base_model)
        btn_create_base.setStyleSheet("QPushButton { padding: 10px; font-size: 14px; }")
        layout.addWidget(btn_create_base)

        btn_create_variant = QPushButton("🎨 Создать специфический вариант")
        btn_create_variant.clicked.connect(self.create_variant)
        btn_create_variant.setStyleSheet("QPushButton { padding: 10px; font-size: 14px; }")
        layout.addWidget(btn_create_variant)

        # Статус
        self.status_label = QLabel("Готов к тестированию...")
        self.status_label.setStyleSheet("color: green; font-weight: bold; padding: 10px;")
        layout.addWidget(self.status_label)

        layout.addStretch()

    def create_base_model(self):
        """Создать базовую модель"""
        self.status_label.setText("🔧 Создание базовой модели...")
        dialog = ModelSpecificationFormV4(is_variant=False, parent=self)
        dialog.setWindowTitle("Создание базовой модели - Тестирование")
        if dialog.exec():
            self.status_label.setText("✅ Базовая модель создана! Теперь можно создать вариант.")
        else:
            self.status_label.setText("❌ Создание базовой модели отменено")

    def create_variant(self):
        """Создать специфический вариант"""
        self.status_label.setText("🎨 Создание специфического варианта...")

        # Для тестирования используем фиксированный ID базовой модели
        # В реальном приложении это будет выбираться из списка
        dialog = ModelSpecificationFormV4(is_variant=True, parent=self)
        dialog.base_model_id = 1  # Предполагаем, что есть базовая модель с ID 1
        dialog.setWindowTitle("Создание специфического варианта - Тестирование")

        if dialog.exec():
            self.status_label.setText("✅ Специфический вариант создан!")
        else:
            self.status_label.setText("❌ Создание варианта отменено")

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Тестирование вариантов моделей")

    window = VariantTestWindow()
    window.show()

    return app.exec()

if __name__ == "__main__":
    sys.exit(main())