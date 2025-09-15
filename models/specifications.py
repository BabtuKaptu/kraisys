# krai_system/models/specifications.py
from sqlmodel import Field, Column, JSON
from typing import Optional, List, Dict, Any
from decimal import Decimal
from .base import Base

class Specification(Base, table=True):
    """Спецификации (SUPER-BOM)"""
    __tablename__ = "specifications"
    
    # Связи
    model_id: int = Field(foreign_key="models.id")
    
    # Версионирование
    version: int = Field(default=1)
    is_default: bool = Field(default=False)
    is_active: bool = Field(default=True)
    
    # Название варианта
    variant_name: Optional[str] = Field(default=None)
    variant_code: Optional[str] = Field(default=None)
    
    # SUPER-BOM структура как в примере "Хайкеры М 75"
    
    # Детали кроя
    cutting_parts: List[Dict[str, Any]] = Field(
        default=[],
        sa_column=Column(JSON),
        description="""
        Структура элемента:
        {
            "cutting_part_id": 123,
            "code": "SOYUZKA",
            "name": "Союзка",
            "quantity": 2,
            "note": "Примечание к детали"
        }
        """
    )
    
    # Фурнитура и покупные материалы  
    hardware: List[Dict[str, Any]] = Field(
        default=[],
        sa_column=Column(JSON),
        description="""
        Структура элемента:
        {
            "material_id": 456,
            "name": "Шнурки плоские вощеные",
            "quantity": 1,
            "file": "150 см",
            "unit": "пара"
        }
        """
    )
    
    # Варианты исполнения
    variants: Dict[str, Any] = Field(
        default={},
        sa_column=Column(JSON),
        description="""
        Структура:
        {
            "perforation": ["без перфорации", "на союзке", "на берце"],
            "lining": ["Полный подклад: кожподклад", "Байка", "Мех"],
            "sole": [
                {"name": "888", "size_range": "39-45"},
                {"name": "Мишлен", "size_range": "36-49"}
            ]
        }
        """
    )
    
    # Расчетные поля
    total_material_cost: Decimal = Field(default=Decimal(0))
    total_labor_hours: Decimal = Field(default=Decimal(0))
    
    # Методы для работы с новой структурой SUPER-BOM
    def add_cutting_part(self, cutting_part_id: int, code: str, 
                        name: str, quantity: int, note: str = ""):
        """Добавление детали кроя в спецификацию"""
        self.cutting_parts.append({
            "cutting_part_id": cutting_part_id,
            "code": code,
            "name": name,
            "quantity": quantity,
            "note": note
        })
    
    def add_hardware(self, material_id: int, name: str,
                    quantity: float, description: str = "", unit: str = "шт"):
        """Добавление фурнитуры в спецификацию"""
        self.hardware.append({
            "material_id": material_id,
            "name": name,
            "quantity": quantity,
            "file": description,
            "unit": unit
        })
    
    def set_variants(self, perforation: List[str] = None,
                    lining: List[str] = None, sole: List[Dict] = None):
        """Установка вариантов исполнения"""
        self.variants = {
            "perforation": perforation or [],
            "lining": lining or [],
            "sole": sole or []
        }
    
    def get_cutting_parts_by_category(self, category: str) -> List[Dict]:
        """Получение деталей кроя по категории"""
        # Требует дополнительной информации о категориях
        return [p for p in self.cutting_parts if p.get("category") == category]
    
    def calculate_total_cost(self, cutting_prices: Dict[int, float], 
                            hardware_prices: Dict[int, float]) -> Decimal:
        """Расчет общей стоимости спецификации"""
        total = Decimal(0)
        
        # Стоимость деталей кроя
        for part in self.cutting_parts:
            part_id = part.get("cutting_part_id")
            quantity = Decimal(str(part.get("quantity", 0)))
            price = Decimal(str(cutting_prices.get(part_id, 0)))
            total += quantity * price
        
        # Стоимость фурнитуры
        for hw in self.hardware:
            mat_id = hw.get("material_id")
            quantity = Decimal(str(hw.get("quantity", 0)))
            price = Decimal(str(hardware_prices.get(mat_id, 0)))
            total += quantity * price
            
        return total