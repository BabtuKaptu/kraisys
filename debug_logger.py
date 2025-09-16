"""
Debug logger for tracking variant creation issues
"""
import datetime
import os

class DebugLogger:
    def __init__(self, log_file="debug_variant.log"):
        self.log_file = log_file
        self.log_path = os.path.join(os.path.dirname(__file__), log_file)

        # Очищаем лог при запуске приложения
        with open(self.log_path, 'w', encoding='utf-8') as f:
            f.write(f"=== DEBUG LOG STARTED AT {datetime.datetime.now()} ===\n")

    def log(self, message):
        """Записать сообщение в лог"""
        timestamp = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
        log_message = f"[{timestamp}] {message}\n"

        # Выводим и в консоль и в файл
        print(message)

        try:
            with open(self.log_path, 'a', encoding='utf-8') as f:
                f.write(log_message)
        except Exception as e:
            print(f"ERROR writing to log: {e}")

# Создаем глобальный экземпляр логгера
debug_logger = DebugLogger()

def log_debug(message):
    """Функция для логирования отладочных сообщений"""
    debug_logger.log(message)