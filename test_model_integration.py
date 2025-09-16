#!/usr/bin/env python3
"""
Тестовый скрипт для проверки интеграции справочников в формы моделей
"""
import sys
from PyQt6.QtWidgets import QApplication, QVBoxLayout, QWidget, QPushButton, QLabel
from PyQt6.QtCore import Qt

def test_model_form_integration():
    """Тестирование интеграции справочников в форме модели"""
    try:
        from ui.references.model_specification_form_v4 import ModelSpecificationForm

        # Создаем форму базовой модели (не варианта)
        form = ModelSpecificationForm(is_variant=False)
        form.show()

        print("✅ Форма спецификации модели открыта")
        print("🔍 Проверьте следующее:")
        print("  1. Поле 'Тип затяжки' находится в основных данных модели")
        print("  2. Кнопка 'Добавить деталь раскроя' использует справочник")
        print("  3. Справочные данные загружаются корректно")

        return form

    except Exception as e:
        print(f"❌ Ошибка открытия формы модели: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_variant_form_integration():
    """Тестирование интеграции справочников в форме варианта"""
    try:
        from ui.references.model_specification_form_v4 import ModelSpecificationForm

        # Создаем форму варианта (с базовой моделью)
        # Нужен ID существующей базовой модели для тестирования
        form = ModelSpecificationForm(is_variant=True, base_model_id=1)
        form.show()

        print("✅ Форма варианта модели открыта")
        print("🔍 Проверьте следующее:")
        print("  1. Поле 'Тип затяжки' находится в основных данных варианта")
        print("  2. Таблицы перфорации и подкладки используют правильные заголовки")
        print("  3. Справочные данные наследуются от базовой модели")

        return form

    except Exception as e:
        print(f"❌ Ошибка открытия формы варианта: {e}")
        import traceback
        traceback.print_exc()
        return None

class TestIntegrationWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Тестирование интеграции справочников")
        self.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout()

        # Заголовок
        title = QLabel("Тестирование интеграции справочников в формы моделей")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-weight: bold; font-size: 14px; margin: 10px;")
        layout.addWidget(title)

        # Кнопки для тестирования
        btn_base_model = QPushButton("Тест: Форма базовой модели")
        btn_base_model.clicked.connect(test_model_form_integration)
        layout.addWidget(btn_base_model)

        btn_variant = QPushButton("Тест: Форма варианта модели")
        btn_variant.clicked.connect(test_variant_form_integration)
        layout.addWidget(btn_variant)

        # Инструкции
        instructions = QLabel("""
Инструкции по тестированию:

1. Нажмите кнопки выше для открытия форм
2. Проверьте расположение поля "Тип затяжки"
3. Проверьте работу кнопок добавления элементов
4. Убедитесь, что справочники загружаются
5. Проверьте корректность заголовков таблиц
        """)
        instructions.setWordWrap(True)
        instructions.setStyleSheet("margin: 10px; padding: 10px; background-color: #f0f0f0;")
        layout.addWidget(instructions)

        self.setLayout(layout)

def main():
    app = QApplication(sys.argv)

    print("🧪 Запуск тестирования интеграции справочников...")

    # Создаем тестовое окно
    test_window = TestIntegrationWindow()
    test_window.show()

    print("📋 Нажмите кнопки для тестирования интеграции")
    print("🔍 Проверьте корректность работы с справочниками")

    sys.exit(app.exec())

if __name__ == "__main__":
    main()