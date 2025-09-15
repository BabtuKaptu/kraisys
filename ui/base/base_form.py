"""Base form dialog for PyQt6 application"""
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QDialogButtonBox
from PyQt6.QtCore import pyqtSignal

class BaseFormDialog(QDialog):
    """Базовый класс для форм редактирования"""

    saved = pyqtSignal(object)  # Сигнал при сохранении

    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setup_ui()

    def setup_ui(self):
        self.layout = QVBoxLayout(self)

        # Контент формы (заполняется в наследниках)
        self.create_form_content()

        # Кнопки
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save |
            QDialogButtonBox.StandardButton.Cancel
        )
        self.button_box.accepted.connect(self.save_data)
        self.button_box.rejected.connect(self.reject)

        self.layout.addWidget(self.button_box)

    def create_form_content(self):
        """Создание содержимого формы (переопределить в наследниках)"""
        pass

    def save_data(self):
        """Сохранение данных (переопределить в наследниках)"""
        pass

    def load_data(self, record_id: int):
        """Загрузка данных для редактирования"""
        pass

    def validate(self) -> bool:
        """Валидация формы"""
        return True