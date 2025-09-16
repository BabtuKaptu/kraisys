"""Main entry point for KRAI Desktop Application"""
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from database.connection import DatabaseConnection
from ui.main_window import MainWindow

def main():
    # Создаем приложение
    app = QApplication(sys.argv)

    # Настройки приложения
    app.setApplicationName("KRAI Production System")
    app.setOrganizationName("KRAI")

    # Инициализация БД
    try:
        db = DatabaseConnection()
        if db.test_connection():
            print("Database connected successfully")
        else:
            print("Warning: Database connection test failed")
    except Exception as e:
        print(f"Database connection failed: {e}")
        print("Starting in demo mode...")

    # Создаем и показываем главное окно
    print("🔥 СОЗДАЮ MainWindow() В main.py")
    window = MainWindow()
    print("🔥 ПОКАЗЫВАЮ window.show() В main.py")
    window.show()

    # Запуск приложения
    sys.exit(app.exec())

if __name__ == "__main__":
    main()