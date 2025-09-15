"""
Диалог выбора типа создания модели: свободный или специфический вариант
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QRadioButton, QGroupBox, QDialogButtonBox
)
from PyQt6.QtCore import Qt

class ModelVariantTypeDialog(QDialog):
    """Диалог выбора типа варианта модели"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Выбор типа модели")
        self.setModal(True)
        self.setFixedSize(500, 350)

        self.variant_type = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Заголовок
        title = QLabel("Выберите тип создаваемой модели:")
        title.setStyleSheet("font-size: 14px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)

        # Группа свободного варианта
        free_group = QGroupBox("🔓 Свободный вариант (базовая модель)")
        free_layout = QVBoxLayout()

        self.free_radio = QRadioButton("Создать базовую модель")
        self.free_radio.setChecked(True)
        free_layout.addWidget(self.free_radio)

        free_desc = QLabel(
            "• Базовая версия модели с вариативностью\n"
            "• Возможность выбора из нескольких материалов\n"
            "• Несколько вариантов перфорации\n"
            "• Выбор из нескольких подошв\n"
            "• Используется как основа для специфических вариантов"
        )
        free_desc.setStyleSheet("color: #666; padding-left: 20px; font-size: 11px;")
        free_desc.setWordWrap(True)
        free_layout.addWidget(free_desc)

        free_group.setLayout(free_layout)
        layout.addWidget(free_group)

        # Группа специфического варианта
        specific_group = QGroupBox("🔒 Специфический вариант")
        specific_layout = QVBoxLayout()

        self.specific_radio = QRadioButton("Создать конкретную версию модели")
        specific_layout.addWidget(self.specific_radio)

        specific_desc = QLabel(
            "• Конкретная версия модели для производства\n"
            "• Фиксированные материалы для каждой детали\n"
            "• Точный расчет себестоимости\n"
            "• Готовая спецификация для запуска в производство\n"
            "• Создается на основе базовой модели"
        )
        specific_desc.setStyleSheet("color: #666; padding-left: 20px; font-size: 11px;")
        specific_desc.setWordWrap(True)
        specific_layout.addWidget(specific_desc)

        specific_group.setLayout(specific_layout)
        layout.addWidget(specific_group)

        layout.addStretch()

        # Кнопки
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def accept(self):
        """Сохранить выбранный тип варианта"""
        if self.free_radio.isChecked():
            self.variant_type = "free"
        else:
            self.variant_type = "specific"
        super().accept()

    def get_variant_type(self):
        """Получить выбранный тип варианта"""
        return self.variant_type