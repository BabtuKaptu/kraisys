"""
Диалог для добавления/редактирования подошвы
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QLineEdit, QDoubleSpinBox, QFormLayout, QDialogButtonBox, QComboBox
)
from PyQt6.QtCore import Qt
from database.connection import DatabaseConnection

class SoleDialog(QDialog):
    """Диалог для ввода данных подошвы"""

    def __init__(self, parent=None, sole_data=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить подошву" if sole_data is None else "Редактировать подошву")
        self.setModal(True)
        self.resize(400, 300)
        self.setMinimumSize(350, 250)

        self.sole_data = sole_data or {}
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Форма ввода данных
        form_layout = QFormLayout()

        # Материал
        self.material_combo = QComboBox()
        self.material_combo.addItem("Не выбрано", None)
        self.load_materials()
        form_layout.addRow("Материал:", self.material_combo)

        # Толщина
        self.thickness_spin = QDoubleSpinBox()
        self.thickness_spin.setRange(0, 100)
        self.thickness_spin.setSuffix(" мм")
        self.thickness_spin.setValue(self.sole_data.get('thickness', 0))
        form_layout.addRow("Толщина:", self.thickness_spin)

        # Цвет
        self.color_input = QLineEdit()
        self.color_input.setText(self.sole_data.get('color', ''))
        form_layout.addRow("Цвет:", self.color_input)

        # Высота каблука
        self.heel_height_spin = QDoubleSpinBox()
        self.heel_height_spin.setRange(0, 200)
        self.heel_height_spin.setSuffix(" мм")
        self.heel_height_spin.setValue(self.sole_data.get('heel_height', 0))
        form_layout.addRow("Высота каблука:", self.heel_height_spin)

        # Высота платформы
        self.platform_height_spin = QDoubleSpinBox()
        self.platform_height_spin.setRange(0, 100)
        self.platform_height_spin.setSuffix(" мм")
        self.platform_height_spin.setValue(self.sole_data.get('platform_height', 0))
        form_layout.addRow("Высота платформы:", self.platform_height_spin)

        layout.addLayout(form_layout)

        # Кнопки
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        # Устанавливаем выбранный материал если редактируем
        if self.sole_data.get('material_id'):
            index = self.material_combo.findData(self.sole_data['material_id'])
            if index >= 0:
                self.material_combo.setCurrentIndex(index)

        # Фокус на первое поле
        self.material_combo.setFocus()

    def load_materials(self):
        """Загружаем материалы из базы данных"""
        db = DatabaseConnection()
        conn = db.get_connection()
        if not conn:
            return

        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, code FROM materials
                WHERE group_type = 'SOLE'
                ORDER BY name
            """)
            materials = cursor.fetchall()

            for material_id, name, code in materials:
                display_text = f"{name} ({code})" if code else name
                self.material_combo.addItem(display_text, material_id)

            cursor.close()
        except Exception as e:
            print(f"Ошибка загрузки материалов: {e}")
        finally:
            if conn:
                db.put_connection(conn)

    def get_sole_data(self):
        """Возвращает введенные данные подошвы"""
        material_id = self.material_combo.currentData()
        material_name = self.material_combo.currentText() if material_id else ""

        return {
            'material_id': material_id,
            'material': material_name,
            'thickness': self.thickness_spin.value(),
            'color': self.color_input.text().strip(),
            'heel_height': self.heel_height_spin.value(),
            'platform_height': self.platform_height_spin.value()
        }

    def accept(self):
        """Валидация перед принятием диалога"""
        if not self.material_combo.currentData():
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите материал подошвы")
            self.material_combo.setFocus()
            return

        super().accept()