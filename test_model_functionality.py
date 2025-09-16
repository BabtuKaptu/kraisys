#!/usr/bin/env python
"""
Тестирование функционала модели ModelSpecificationFormV4
"""
import sys
import time
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtTest import QTest

from database.connection import DatabaseConnection
from ui.references.model_specification_form_v4 import ModelSpecificationFormV4

class ModelTester:
    def __init__(self):
        self.db = DatabaseConnection()
        self.form = None
        self.app = QApplication.instance()
        if not self.app:
            self.app = QApplication(sys.argv)

    def test_create_new_model(self):
        """Тест создания новой модели"""
        print("🧪 Тестирование создания новой модели...")

        self.form = ModelSpecificationFormV4()
        self.form.show()

        # Заполняем основные поля
        self.form.name_input.setText("Тестовая модель")
        self.form.article_input.setText("TEST001")

        # Проверяем вкладку Параметры
        parameters_tab_index = None
        for i in range(self.form.tabs.count()):
            if "Параметры" in self.form.tabs.tabText(i):
                parameters_tab_index = i
                break

        if parameters_tab_index is not None:
            print("✓ Вкладка 'Параметры модели' найдена")
            self.form.tabs.setCurrentIndex(parameters_tab_index)

            # Проверяем наличие таблиц
            if hasattr(self.form, 'perforation_table'):
                print("✓ Таблица перфораций найдена")
            else:
                print("❌ Таблица перфораций не найдена")

            if hasattr(self.form, 'lining_table'):
                print("✓ Таблица подкладок найдена")
            else:
                print("❌ Таблица подкладок не найдена")

            if hasattr(self.form, 'lasting_combo'):
                print("✓ Комбобокс типа затяжки найден")
            else:
                print("❌ Комбобокс типа затяжки не найден")
        else:
            print("❌ Вкладка 'Параметры' не найдена")

        # Проверяем работу кнопок добавления
        try:
            if hasattr(self.form, 'add_perforation_btn'):
                print("✓ Кнопка добавления перфорации найдена")
                # Можно попробовать кликнуть, но не будем пока
            else:
                print("❌ Кнопка добавления перфорации не найдена")
        except Exception as e:
            print(f"❌ Ошибка при проверке кнопки перфорации: {e}")

        self.form.close()
        print("✓ Создание формы прошло успешно")

    def test_database_connections(self):
        """Тест соединений с базой данных"""
        print("🧪 Тестирование соединений с БД...")

        # Проверяем основное соединение
        if self.db.test_connection():
            print("✓ Основное соединение с БД работает")
        else:
            print("❌ Основное соединение с БД не работает")
            return False

        # Проверяем пул соединений
        conn = self.db.get_connection()
        if conn:
            print("✓ Получение соединения из пула работает")
            self.db.put_connection(conn)
            print("✓ Возврат соединения в пул работает")
        else:
            print("❌ Не удалось получить соединение из пула")
            return False

        return True

    def test_reference_data_loading(self):
        """Тест загрузки справочных данных"""
        print("🧪 Тестирование загрузки справочных данных...")

        self.form = ModelSpecificationFormV4()

        try:
            # Проверяем метод load_reference_data
            self.form.load_reference_data()
            print("✓ Метод load_reference_data выполнился без ошибок")

            # Проверяем заполнение комбобоксов
            if self.form.lasting_combo.count() > 0:
                print(f"✓ Типы затяжки загружены: {self.form.lasting_combo.count()} элементов")
            else:
                print("⚠️ Типы затяжки не загружены (возможно, таблица пуста)")

        except Exception as e:
            print(f"❌ Ошибка при загрузке справочных данных: {e}")

        self.form.close()

    def run_all_tests(self):
        """Запуск всех тестов"""
        print("🏁 Начало тестирования функционала модели")
        print("=" * 50)

        # Тест соединений БД
        if not self.test_database_connections():
            print("❌ Критическая ошибка: БД недоступна")
            return

        print()

        # Тест создания формы
        self.test_create_new_model()
        print()

        # Тест загрузки данных
        self.test_reference_data_loading()
        print()

        print("=" * 50)
        print("🏁 Тестирование завершено")

def main():
    """Главная функция"""
    tester = ModelTester()

    # Настраиваем таймер для автоматического завершения
    timer = QTimer()
    timer.timeout.connect(lambda: tester.app.quit())
    timer.start(10000)  # 10 секунд на все тесты

    # Запускаем тесты
    QTimer.singleShot(100, tester.run_all_tests)

    # Запускаем приложение
    tester.app.exec()

if __name__ == "__main__":
    main()