# krai_system/services/warehouse.py
from typing import Dict, List, Any, Optional
from datetime import datetime, date
from decimal import Decimal
from sqlmodel import Session, select
from ..models.materials import Material, MaterialGroup
from ..models.warehouse import WarehouseStock
from .database import DatabaseService, engine

class WarehouseService:
    """Сервис для управления складом"""
    
    @staticmethod
    def get_all_stocks() -> List[WarehouseStock]:
        """
        Получить все складские остатки
        """
        with Session(engine) as session:
            stocks = session.exec(select(WarehouseStock)).all()
            return list(stocks)

    @staticmethod
    def get_material_stock(material_id: int) -> Optional[WarehouseStock]:
        """
        Получить остаток материала на складе
        """
        with Session(engine) as session:
            stock = session.exec(
                select(WarehouseStock).where(WarehouseStock.material_id == material_id)
            ).first()
            return stock

    @staticmethod
    def create_stock(stock_data: Dict[str, Any]) -> WarehouseStock:
        """
        Создать новую запись складского остатка
        """
        with Session(engine) as session:
            stock = WarehouseStock(
                material_id=stock_data.get('material_id'),
                warehouse_code=stock_data.get('warehouse_code', 'WH01'),
                quantity=Decimal(str(stock_data.get('quantity', 0))),
                unit=stock_data.get('unit', 'шт'),
                location=stock_data.get('location', 'Основной склад'),
                receipt_date=date.today(),
                updated_at=datetime.now()
            )
            session.add(stock)
            session.commit()
            session.refresh(stock)
            return stock

    @staticmethod
    def update_stock(stock_id: int, update_data: Dict[str, Any]) -> Optional[WarehouseStock]:
        """
        Обновить складской остаток
        """
        with Session(engine) as session:
            stock = session.get(WarehouseStock, stock_id)
            if not stock:
                return None

            for key, value in update_data.items():
                if hasattr(stock, key):
                    if key in ['quantity', 'reserved_qty', 'purchase_price'] and value is not None:
                        setattr(stock, key, Decimal(str(value)))
                    else:
                        setattr(stock, key, value)

            stock.updated_at = datetime.now()
            session.add(stock)
            session.commit()
            session.refresh(stock)
            return stock

    @staticmethod
    def delete_stock(stock_id: int) -> bool:
        """
        Удалить складской остаток
        """
        with Session(engine) as session:
            stock = session.get(WarehouseStock, stock_id)
            if not stock:
                return False

            session.delete(stock)
            session.commit()
            return True
    
    @staticmethod
    def check_low_stock() -> List[Dict[str, Any]]:
        """
        Проверить материалы с низким остатком
        """
        low_stock_items = []

        with Session(engine) as session:
            stocks = session.exec(
                select(WarehouseStock).where(
                    WarehouseStock.quantity < Decimal('100')  # Low stock threshold
                )
            ).all()

            for stock in stocks:
                low_stock_items.append({
                    'stock_id': stock.id,
                    'material_id': stock.material_id,
                    'warehouse_code': stock.warehouse_code,
                    'current_stock': float(stock.quantity) if stock.quantity else 0,
                    'unit': stock.unit,
                    'status': stock.status
                })

        return low_stock_items
    
    @staticmethod
    def receive_materials(receipt_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Оприходовать поступление материалов
        """
        receipt_id = f"RCP-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        with Session(engine) as session:
            transactions = []

            for item in receipt_data.get('items', []):
                material_id = item.get('material_id')

                # Получаем складской остаток по material_id
                stock = session.exec(
                    select(WarehouseStock).where(
                        WarehouseStock.material_id == material_id
                    )
                ).first()

                if not stock:
                    # Создаем новую запись если материала нет на складе
                    stock = WarehouseStock(
                        material_id=material_id,
                        warehouse_code=item.get('warehouse_code', 'WH01'),
                        quantity=Decimal('0'),
                        unit=item.get('unit', 'шт'),
                        location=receipt_data.get('location', 'Основной склад'),
                        receipt_date=date.today(),
                        last_receipt_date=date.today(),
                        updated_at=datetime.now()
                    )
                    session.add(stock)
                    session.flush()

                if stock:
                    # Увеличиваем количество
                    quantity = Decimal(str(item.get('quantity', 0)))
                    stock.quantity = (stock.quantity or Decimal('0')) + quantity
                    stock.last_receipt_date = date.today()
                    stock.updated_at = datetime.now()

            session.commit()

            return {
                'receipt_id': receipt_id,
                'supplier': receipt_data.get('supplier', 'Unknown'),
                'receipt_date': datetime.now().isoformat(),
                'items_count': len(receipt_data.get('items', [])),
                'status': 'success'
            }
    
    @staticmethod
    def issue_materials(issue_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Списать материалы в производство
        """
        issue_id = f"ISS-{datetime.now().strftime('%Y%m%d%H%M%S')}"

        with Session(engine) as session:
            transactions = []

            for item in issue_data.get('items', []):
                # Получаем складской остаток по material_id
                material_id = item.get('material_id')
                stock = session.exec(
                    select(WarehouseStock).where(
                        WarehouseStock.material_id == material_id
                    )
                ).first()

                if not stock:
                    return {
                        "error": f"Material {item.get('material_code')} not found in stock",
                        "status": "error"
                    }

                quantity = Decimal(str(item.get('quantity', 0)))

                if stock.quantity < quantity:
                    return {
                        "error": f"Insufficient stock for material {material_id}",
                        "available": float(stock.quantity),
                        "requested": float(quantity),
                        "status": "error"
                    }

                # Уменьшаем количество
                stock.quantity = (stock.quantity or Decimal('0')) - quantity
                stock.last_issue_date = date.today()
                stock.updated_at = datetime.now()

            session.commit()

            return {
                'issue_id': issue_id,
                'order_id': issue_data.get('order_id'),
                'issue_date': datetime.now().isoformat(),
                'items_count': len(issue_data.get('items', [])),
                'status': 'success'
            }
    
    @staticmethod
    def transfer_materials(transfer_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Переместить материалы между складами
        """
        transfer = {
            'transfer_id': f"TRF-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'from_location': transfer_data.get('from_location'),
            'to_location': transfer_data.get('to_location'),
            'transfer_date': datetime.now().isoformat(),
            'items': transfer_data.get('items', []),
            'status': 'completed'
        }
        
        return transfer
    
    @staticmethod
    def inventory_check() -> Dict[str, Any]:
        """
        Провести инвентаризацию
        """
        materials = DatabaseService.get_all(Material)
        
        inventory = {
            'inventory_id': f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            'date': datetime.now().isoformat(),
            'items': []
        }
        
        for material in materials:
            # Заглушка для фактического остатка
            system_quantity = 1000
            actual_quantity = 995  # Имитируем небольшое расхождение
            
            inventory['items'].append({
                'material_id': material.id,
                'material_name': material.name,
                'system_quantity': system_quantity,
                'actual_quantity': actual_quantity,
                'difference': actual_quantity - system_quantity,
                'unit': material.unit
            })
        
        # Статистика инвентаризации
        total_items = len(inventory['items'])
        items_with_diff = sum(1 for item in inventory['items'] if item['difference'] != 0)
        
        inventory['summary'] = {
            'total_items': total_items,
            'items_with_difference': items_with_diff,
            'accuracy_rate': round((1 - items_with_diff / total_items) * 100, 2) if total_items > 0 else 100
        }
        
        return inventory
    
    @staticmethod
    def get_warehouse_statistics() -> Dict[str, Any]:
        """
        Получить статистику склада
        """
        with Session(engine) as session:
            stocks = session.exec(select(WarehouseStock)).all()

            total_value = Decimal('0')
            total_items = 0
            critical_items = 0

            for stock in stocks:
                total_items += 1
                if stock.status == 'CRITICAL':
                    critical_items += 1
                # Считаем общую стоимость (временно используем количество * 100 как цену)
                total_value += stock.quantity * 100

            return {
                'total_materials': total_items,
                'total_value': float(total_value),
                'low_stock_count': critical_items,
                'warehouse_items': stocks,  # Передаем все складские остатки
                'last_updated': datetime.now().isoformat()
            }

    @staticmethod
    def has_stock_for_material(material_id: str) -> bool:
        """Проверить, есть ли складские остатки для материала"""
        with Session(engine) as session:
            statement = select(WarehouseStock).where(WarehouseStock.material_id == material_id)
            result = session.exec(statement)
            return result.first() is not None