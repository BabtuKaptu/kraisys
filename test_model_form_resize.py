#!/usr/bin/env python3
"""
Тестирование изменяемых размеров окна формы модели
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel
from PyQt6.QtCore import Qt
from ui.references.model_specification_form_v4 import ModelSpecificationFormV4

class ModelFormResizeTestWindow(QMainWindow):
    """Окно для тестирования изменяемых размеров формы модели"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("🔧 Тест изменяемости окна формы модели")
        self.setGeometry(200, 200, 600, 400)

        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Информация
        info_label = QLabel("""
🔧 ТЕСТИРОВАНИЕ ПРОКРУТКИ И ИЗМЕНЯЕМЫХ РАЗМЕРОВ

✅ Форма модели: полностью изменяемая + прокрутка
✅ Добавлен минимальный размер: 1200x700
✅ Окно можно изменять по горизонтали И вертикали
✅ Добавлена прокрутка - поля не сжимаются, появляется скроллбар

🖱️ Проверьте: изменение размеров окна + прокрутка содержимого!
        """)
        info_label.setWordWrap(True)
        info_label.setStyleSheet("padding: 20px; background: #e8f5e8; border-radius: 5px; font-size: 13px;")
        layout.addWidget(info_label)

        # Кнопка тестирования
        btn_model = QPushButton("📋 Открыть форму модели (С ПРОКРУТКОЙ)")
        btn_model.clicked.connect(self.test_model_form)
        btn_model.setStyleSheet("QPushButton { padding: 15px; font-size: 14px; margin: 10px; font-weight: bold; }")
        layout.addWidget(btn_model)

        # Инструкции
        instructions_label = QLabel("""
🔧 ИНСТРУКЦИИ ПО ТЕСТИРОВАНИЮ:

1. Нажмите кнопку выше
2. Попробуйте изменить размеры окна курсором за углы ↔ ↕ ↗ ↙
3. Уменьшите окно - должен появиться скроллбар справа/снизу
4. Поля не должны сжиматься - вместо этого появляется прокрутка
5. Кнопки "Сохранить/Отмена" остаются внизу (не прокручиваются)

✅ ИСПРАВЛЕНО: добавлены QScrollArea + setMinimumSize(1200, 700)
✅ РЕЗУЛЬТАТ: поля сохраняют размер, появляется прокрутка при необходимости
        """)
        instructions_label.setWordWrap(True)
        instructions_label.setStyleSheet("padding: 15px; background: #fff8dc; border-radius: 5px; font-size: 12px;")
        layout.addWidget(instructions_label)

        layout.addStretch()

    def test_model_form(self):
        """Тестирование формы модели"""
        dialog = ModelSpecificationFormV4(parent=self)
        dialog.setWindowTitle("📋 Форма модели - С ПРОКРУТКОЙ И ИЗМЕНЯЕМЫМИ РАЗМЕРАМИ!")
        dialog.exec()

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Тест изменяемости формы модели")

    window = ModelFormResizeTestWindow()
    window.show()

    return app.exec()

if __name__ == "__main__":
    sys.exit(main())