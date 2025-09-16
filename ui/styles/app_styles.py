"""
Единая система стилей для приложения KRAI Desktop
"""

class AppColors:
    """Цветовая палитра приложения"""

    # Основные цвета
    PRIMARY = "#2196F3"        # Синий
    PRIMARY_DARK = "#1976D2"   # Тёмно-синий
    PRIMARY_LIGHT = "#BBDEFB"  # Светло-синий

    SECONDARY = "#FF9800"      # Оранжевый
    SECONDARY_DARK = "#F57C00" # Тёмно-оранжевый
    SECONDARY_LIGHT = "#FFE0B2"# Светло-оранжевый

    # Семантические цвета
    SUCCESS = "#4CAF50"        # Зелёный
    SUCCESS_LIGHT = "#C8E6C9"
    WARNING = "#FF9800"        # Оранжевый
    WARNING_LIGHT = "#FFE0B2"
    ERROR = "#F44336"          # Красный
    ERROR_LIGHT = "#FFCDD2"
    INFO = "#2196F3"           # Синий
    INFO_LIGHT = "#E3F2FD"

    # Нейтральные цвета
    WHITE = "#FFFFFF"
    LIGHT_GRAY = "#F5F5F5"
    GRAY = "#9E9E9E"
    DARK_GRAY = "#424242"
    BLACK = "#212121"

    # Цвета фона
    BACKGROUND = "#FAFAFA"
    SURFACE = "#FFFFFF"
    SURFACE_VARIANT = "#F5F5F5"

    # Цвета текста
    TEXT_PRIMARY = "#212121"
    TEXT_SECONDARY = "#757575"
    TEXT_DISABLED = "#BDBDBD"
    TEXT_ON_PRIMARY = "#FFFFFF"


class AppFonts:
    """Типографика приложения"""

    # Размеры шрифтов
    SIZE_H1 = "24px"
    SIZE_H2 = "20px"
    SIZE_H3 = "18px"
    SIZE_H4 = "16px"
    SIZE_BODY = "14px"
    SIZE_SMALL = "12px"
    SIZE_CAPTION = "10px"

    # Веса шрифтов
    WEIGHT_LIGHT = "300"
    WEIGHT_NORMAL = "400"
    WEIGHT_MEDIUM = "500"
    WEIGHT_BOLD = "700"

    # Семейства шрифтов
    FAMILY_PRIMARY = "Segoe UI, Tahoma, Arial, sans-serif"
    FAMILY_MONOSPACE = "Consolas, Monaco, monospace"


class AppSpacing:
    """Система отступов"""

    XS = "4px"
    SM = "8px"
    MD = "16px"
    LG = "24px"
    XL = "32px"
    XXL = "48px"


class AppStyles:
    """Готовые стили для различных компонентов"""

    @staticmethod
    def get_main_window_style():
        """Стиль главного окна"""
        return f"""
        QMainWindow {{
            background-color: {AppColors.BACKGROUND};
            color: {AppColors.TEXT_PRIMARY};
            font-family: {AppFonts.FAMILY_PRIMARY};
            font-size: {AppFonts.SIZE_BODY};
        }}

        QMenuBar {{
            background-color: {AppColors.SURFACE};
            color: {AppColors.TEXT_PRIMARY};
            border-bottom: 1px solid {AppColors.LIGHT_GRAY};
            padding: {AppSpacing.SM};
        }}

        QMenuBar::item {{
            background-color: transparent;
            padding: {AppSpacing.SM} {AppSpacing.MD};
            border-radius: 4px;
        }}

        QMenuBar::item:selected {{
            background-color: {AppColors.PRIMARY_LIGHT};
        }}

        QStatusBar {{
            background-color: {AppColors.SURFACE};
            color: {AppColors.TEXT_SECONDARY};
            border-top: 1px solid {AppColors.LIGHT_GRAY};
            padding: {AppSpacing.SM};
        }}
        """

    @staticmethod
    def get_button_style():
        """Стили кнопок"""
        return f"""
        QPushButton {{
            background-color: {AppColors.PRIMARY};
            color: {AppColors.TEXT_ON_PRIMARY};
            border: none;
            padding: {AppSpacing.SM} {AppSpacing.MD};
            border-radius: 6px;
            font-weight: {AppFonts.WEIGHT_MEDIUM};
            font-size: {AppFonts.SIZE_BODY};
            min-height: 32px;
        }}

        QPushButton:hover {{
            background-color: {AppColors.PRIMARY_DARK};
        }}

        QPushButton:pressed {{
            background-color: {AppColors.PRIMARY_DARK};
        }}

        QPushButton:disabled {{
            background-color: {AppColors.GRAY};
            color: {AppColors.TEXT_DISABLED};
        }}

        /* Вторичная кнопка */
        QPushButton[class="secondary"] {{
            background-color: {AppColors.SURFACE};
            color: {AppColors.PRIMARY};
            border: 2px solid {AppColors.PRIMARY};
        }}

        QPushButton[class="secondary"]:hover {{
            background-color: {AppColors.PRIMARY_LIGHT};
        }}

        /* Кнопка успеха */
        QPushButton[class="success"] {{
            background-color: {AppColors.SUCCESS};
        }}

        QPushButton[class="success"]:hover {{
            background-color: #45a049;
        }}

        /* Кнопка предупреждения */
        QPushButton[class="warning"] {{
            background-color: {AppColors.WARNING};
        }}

        QPushButton[class="warning"]:hover {{
            background-color: {AppColors.SECONDARY_DARK};
        }}

        /* Кнопка ошибки */
        QPushButton[class="error"] {{
            background-color: {AppColors.ERROR};
        }}

        QPushButton[class="error"]:hover {{
            background-color: #d32f2f;
        }}
        """

    @staticmethod
    def get_table_style():
        """Стили таблиц"""
        return f"""
        QTableWidget {{
            background-color: {AppColors.SURFACE};
            alternate-background-color: {AppColors.SURFACE_VARIANT};
            gridline-color: {AppColors.LIGHT_GRAY};
            selection-background-color: {AppColors.PRIMARY_LIGHT};
            color: {AppColors.TEXT_PRIMARY};
            border: 1px solid {AppColors.LIGHT_GRAY};
            border-radius: 8px;
        }}

        QTableWidget::item {{
            padding: {AppSpacing.SM};
            border: none;
        }}

        QTableWidget::item:selected {{
            background-color: {AppColors.PRIMARY_LIGHT};
            color: {AppColors.TEXT_PRIMARY};
        }}

        QHeaderView::section {{
            background-color: {AppColors.SURFACE_VARIANT};
            color: {AppColors.TEXT_PRIMARY};
            padding: {AppSpacing.SM};
            border: none;
            border-bottom: 2px solid {AppColors.PRIMARY};
            font-weight: {AppFonts.WEIGHT_MEDIUM};
        }}

        QHeaderView::section:hover {{
            background-color: {AppColors.PRIMARY_LIGHT};
        }}
        """

    @staticmethod
    def get_input_style():
        """Стили полей ввода"""
        return f"""
        QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox, QComboBox {{
            background-color: {AppColors.SURFACE};
            color: {AppColors.TEXT_PRIMARY};
            border: 2px solid {AppColors.LIGHT_GRAY};
            border-radius: 6px;
            padding: {AppSpacing.SM};
            font-size: {AppFonts.SIZE_BODY};
            min-height: 32px;
        }}

        QLineEdit:focus, QTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {{
            border-color: {AppColors.PRIMARY};
            outline: none;
        }}

        QLineEdit:disabled, QTextEdit:disabled, QSpinBox:disabled, QDoubleSpinBox:disabled, QComboBox:disabled {{
            background-color: {AppColors.SURFACE_VARIANT};
            color: {AppColors.TEXT_DISABLED};
            border-color: {AppColors.GRAY};
        }}

        QComboBox::drop-down {{
            border: none;
            background-color: transparent;
            width: 20px;
        }}

        QComboBox::down-arrow {{
            image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iOCIgdmlld0JveD0iMCAwIDEyIDgiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik0xIDFMNiA2TDExIDEiIHN0cm9rZT0iIzc1NzU3NSIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiLz4KPHN2Zz4K);
            width: 12px;
            height: 8px;
        }}
        """

    @staticmethod
    def get_tab_style():
        """Стили вкладок"""
        return f"""
        QTabWidget::pane {{
            border: 1px solid {AppColors.LIGHT_GRAY};
            border-radius: 8px;
            background-color: {AppColors.SURFACE};
            top: -1px;
        }}

        QTabBar::tab {{
            background-color: {AppColors.SURFACE_VARIANT};
            color: {AppColors.TEXT_SECONDARY};
            padding: {AppSpacing.SM} {AppSpacing.MD};
            margin: 0px 2px;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
            min-width: 100px;
            font-weight: {AppFonts.WEIGHT_MEDIUM};
        }}

        QTabBar::tab:selected {{
            background-color: {AppColors.SURFACE};
            color: {AppColors.PRIMARY};
            border-bottom: 2px solid {AppColors.PRIMARY};
        }}

        QTabBar::tab:hover:!selected {{
            background-color: {AppColors.PRIMARY_LIGHT};
            color: {AppColors.TEXT_PRIMARY};
        }}
        """

    @staticmethod
    def get_group_box_style():
        """Стили группирующих элементов"""
        return f"""
        QGroupBox {{
            font-weight: {AppFonts.WEIGHT_MEDIUM};
            font-size: {AppFonts.SIZE_H4};
            color: {AppColors.TEXT_PRIMARY};
            border: 2px solid {AppColors.LIGHT_GRAY};
            border-radius: 8px;
            margin-top: {AppSpacing.MD};
            padding-top: {AppSpacing.SM};
        }}

        QGroupBox::title {{
            subcontrol-origin: margin;
            left: {AppSpacing.MD};
            padding: 0 {AppSpacing.SM} 0 {AppSpacing.SM};
            background-color: {AppColors.SURFACE};
            color: {AppColors.PRIMARY};
        }}
        """

    @staticmethod
    def get_combined_style():
        """Получить все стили вместе"""
        return (
            AppStyles.get_main_window_style() +
            AppStyles.get_button_style() +
            AppStyles.get_table_style() +
            AppStyles.get_input_style() +
            AppStyles.get_tab_style() +
            AppStyles.get_group_box_style()
        )


class AppIcons:
    """Иконки приложения (Unicode символы)"""

    # Действия
    ADD = "➕"
    EDIT = "✏️"
    DELETE = "🗑"
    SAVE = "💾"
    CANCEL = "❌"
    OK = "✅"
    REFRESH = "🔄"
    SEARCH = "🔍"
    FILTER = "🔽"
    SORT = "📊"

    # Навигация
    BACK = "⬅️"
    FORWARD = "➡️"
    UP = "⬆️"
    DOWN = "⬇️"
    HOME = "🏠"

    # Объекты
    MODEL = "👟"
    VARIANT = "🔀"
    MATERIAL = "🧵"
    CUTTING = "✂️"
    HARDWARE = "🔩"
    SOLE = "👟"
    PERFORATION = "🔹"
    LINING = "🧱"

    # Статусы
    SUCCESS = "✅"
    WARNING = "⚠️"
    ERROR = "❌"
    INFO = "ℹ️"

    # Файлы и данные
    IMPORT = "📥"
    EXPORT = "📤"
    PRINT = "🖨️"
    PDF = "📄"
    EXCEL = "📊"

    # Настройки
    SETTINGS = "⚙️"
    THEME = "🎨"
    HELP = "❓"
    ABOUT = "📋"