#!/usr/bin/env python3
"""
Тестирование изменяемых размеров окон
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel
from PyQt6.QtCore import Qt
from ui.references.sole_dialog import SoleDialog
from ui.references.model_variant_dialog import ModelVariantTypeDialog
from ui.references.model_specification_form_v4 import ModelSpecificationFormV4

class ResizableTestWindow(QMainWindow):
    """Окно для тестирования изменяемых размеров"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("🔄 Тест изменяемых размеров окон")
        self.setGeometry(200, 200, 700, 500)

        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Информация
        info_label = QLabel("""
🔄 ТЕСТИРОВАНИЕ ИЗМЕНЯЕМЫХ РАЗМЕРОВ ОКОН

✅ Главное окно: уже изменяемое
✅ Диалог подошвы: исправлен (resize + минимальный размер)
✅ Диалог типа модели: исправлен (resize + минимальный размер)
✅ Форма создания модели: уже изменяемая

🖱️ Попробуйте изменить размеры окон курсором за углы!
        """)
        info_label.setWordWrap(True)
        info_label.setStyleSheet("padding: 20px; background: #e8f5e8; border-radius: 5px; font-size: 13px;")
        layout.addWidget(info_label)

        # Кнопки тестирования
        btn_sole = QPushButton("🦶 Тест диалога подошвы (теперь изменяемый)")
        btn_sole.clicked.connect(self.test_sole_dialog)
        btn_sole.setStyleSheet("QPushButton { padding: 12px; font-size: 14px; margin: 5px; }")
        layout.addWidget(btn_sole)

        btn_variant = QPushButton("🎯 Тест диалога типа модели (теперь изменяемый)")
        btn_variant.clicked.connect(self.test_variant_dialog)
        btn_variant.setStyleSheet("QPushButton { padding: 12px; font-size: 14px; margin: 5px; }")
        layout.addWidget(btn_variant)

        btn_model = QPushButton("📋 Тест формы создания модели (уже была изменяемой)")
        btn_model.clicked.connect(self.test_model_form)
        btn_model.setStyleSheet("QPushButton { padding: 12px; font-size: 14px; margin: 5px; }")
        layout.addWidget(btn_model)

        # Инструкции
        instructions_label = QLabel("""
🔧 ИНСТРУКЦИИ ПО ТЕСТИРОВАНИЮ:

1. Нажмите любую кнопку выше
2. В открывшемся окне подведите курсор к углу или краю окна
3. Курсор должен измениться на стрелку изменения размера ↔ ↕ ↗
4. Потяните за край окна, чтобы изменить его размер
5. Окно должно плавно изменяться по размеру!

✅ ДО: окна имели фиксированный размер (setFixedSize)
✅ ПОСЛЕ: окна изменяемые с минимальными размерами (resize + setMinimumSize)
        """)
        instructions_label.setWordWrap(True)
        instructions_label.setStyleSheet("padding: 15px; background: #fff8dc; border-radius: 5px; font-size: 12px;")
        layout.addWidget(instructions_label)

        layout.addStretch()

    def test_sole_dialog(self):
        """Тестирование диалога подошвы"""
        dialog = SoleDialog(parent=self)
        dialog.setWindowTitle("🦶 Диалог подошвы - ТЕПЕРЬ ИЗМЕНЯЕМЫЙ!")
        dialog.exec()

    def test_variant_dialog(self):
        """Тестирование диалога типа модели"""
        dialog = ModelVariantTypeDialog(parent=self)
        dialog.setWindowTitle("🎯 Диалог типа модели - ТЕПЕРЬ ИЗМЕНЯЕМЫЙ!")
        dialog.exec()

    def test_model_form(self):
        """Тестирование формы создания модели"""
        dialog = ModelSpecificationFormV4(parent=self)
        dialog.setWindowTitle("📋 Форма модели - УЖЕ БЫЛА ИЗМЕНЯЕМОЙ!")
        dialog.exec()

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Тест изменяемых размеров окон")

    window = ResizableTestWindow()
    window.show()

    return app.exec()

if __name__ == "__main__":
    sys.exit(main())