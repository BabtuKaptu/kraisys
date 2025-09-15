# krai_system/services/mrp.py
from typing import Dict, List, Optional, Any
from datetime import date, datetime, timedelta
from decimal import Decimal
from sqlmodel import Session, select
from ..models.production_orders import ProductionOrder
from ..models.mrp import ProductionSchedule, PurchasePlan, ScheduleStatus, PurchaseStatus
from ..models.materials import Material
from ..models.warehouse import WarehouseStock
from ..models.specifications import Specification
from .database import DatabaseService, engine

class MRPService:
    """Сервис планирования производства и закупок"""

    DAILY_CAPACITY = 150  # Максимальная мощность производства в день

    @staticmethod
    def calculate_material_requirements(order: ProductionOrder) -> Dict[str, Any]:
        """Рассчитать потребности в материалах для заказа"""
        requirements = {}

        # Получаем спецификацию
        if order.specification_id:
            with Session(engine) as session:
                spec = session.get(Specification, order.specification_id)
                if spec and spec.materials:
                    for mat_id, qty in spec.materials.items():
                        requirements[mat_id] = float(qty) * order.total_pairs

        # Добавляем выбранные материалы (кожа и подошва)
        if order.leather_material_id:
            requirements[str(order.leather_material_id)] = requirements.get(
                str(order.leather_material_id), 0
            ) + order.total_pairs * 2  # примерный расход кожи

        if order.sole_material_id:
            requirements[str(order.sole_material_id)] = requirements.get(
                str(order.sole_material_id), 0
            ) + order.total_pairs

        return requirements

    @staticmethod
    def check_material_availability(requirements: Dict[str, float]) -> Dict[str, Any]:
        """Проверить доступность материалов на складе"""
        availability = {}

        with Session(engine) as session:
            for mat_id, required_qty in requirements.items():
                # Получаем материал
                material = session.get(Material, int(mat_id))
                if not material:
                    continue

                # Получаем складские остатки
                statement = select(WarehouseStock).where(
                    WarehouseStock.material_id == int(mat_id)
                )
                stocks = session.exec(statement).all()
                available_qty = sum(float(stock.quantity) for stock in stocks)

                availability[mat_id] = {
                    "material_name": material.name,
                    "required": required_qty,
                    "available": available_qty,
                    "deficit": max(0, required_qty - available_qty),
                    "supplier": material.supplier_name
                }

        return availability

    @staticmethod
    def schedule_production(order: ProductionOrder) -> ProductionSchedule:
        """Запланировать производство заказа"""
        with Session(engine) as session:
            # Проверяем существующее расписание
            statement = select(ProductionSchedule).where(
                ProductionSchedule.order_id == order.id
            )
            existing = session.exec(statement).first()

            if existing:
                return existing

            # Находим первую доступную дату
            current_date = date.today() + timedelta(days=1)
            capacity_needed = order.total_pairs

            for _ in range(30):  # Ищем в пределах 30 дней
                # Проверяем загрузку на эту дату
                statement = select(ProductionSchedule).where(
                    ProductionSchedule.scheduled_date == current_date
                )
                schedules = session.exec(statement).all()
                used_capacity = sum(s.capacity_used for s in schedules)

                if used_capacity + capacity_needed <= MRPService.DAILY_CAPACITY:
                    # Создаем расписание
                    schedule = ProductionSchedule(
                        order_id=order.id,
                        scheduled_date=current_date,
                        capacity_used=capacity_needed,
                        workshop=order.workshop or "Основной цех",
                        status=ScheduleStatus.PLANNED
                    )
                    session.add(schedule)
                    session.commit()
                    session.refresh(schedule)
                    return schedule

                current_date += timedelta(days=1)

            # Если не нашли свободную дату, планируем на ближайшую
            schedule = ProductionSchedule(
                order_id=order.id,
                scheduled_date=current_date,
                capacity_used=capacity_needed,
                workshop=order.workshop or "Основной цех",
                status=ScheduleStatus.PLANNED
            )
            session.add(schedule)
            session.commit()
            session.refresh(schedule)
            return schedule

    @staticmethod
    def create_purchase_plan(order: ProductionOrder, availability: Dict[str, Any]) -> List[PurchasePlan]:
        """Создать план закупок для заказа"""
        purchase_plans = []

        with Session(engine) as session:
            for mat_id, info in availability.items():
                if info["deficit"] > 0:
                    # Создаем план закупки
                    plan = PurchasePlan(
                        material_id=int(mat_id),
                        material_name=info["material_name"],
                        required_qty=Decimal(str(info["required"])),
                        available_qty=Decimal(str(info["available"])),
                        deficit_qty=Decimal(str(info["deficit"])),
                        order_refs=[order.order_number],
                        supplier=info["supplier"],
                        planned_date=date.today() + timedelta(days=3),
                        status=PurchaseStatus.PENDING,
                        notes=f"Для заказа {order.order_number}"
                    )
                    session.add(plan)
                    purchase_plans.append(plan)

            session.commit()

        return purchase_plans

    @staticmethod
    def process_order(order: ProductionOrder) -> Dict[str, Any]:
        """Обработать заказ через MRP"""
        # Рассчитываем потребности
        requirements = MRPService.calculate_material_requirements(order)

        # Проверяем доступность
        availability = MRPService.check_material_availability(requirements)

        # Планируем производство
        schedule = MRPService.schedule_production(order)

        # Создаем план закупок
        purchase_plans = MRPService.create_purchase_plan(order, availability)

        # Обновляем заказ
        with Session(engine) as session:
            order_to_update = session.get(ProductionOrder, order.id)
            order_to_update.material_requirements = requirements
            order_to_update.planned_start_date = schedule.scheduled_date
            order_to_update.production_capacity_used = schedule.capacity_used
            session.commit()

        return {
            "schedule": schedule,
            "purchase_plans": purchase_plans,
            "availability": availability,
            "requirements": requirements
        }

    @staticmethod
    def get_production_schedule(start_date: date = None, end_date: date = None) -> List[Dict]:
        """Получить производственное расписание"""
        with Session(engine) as session:
            statement = select(ProductionSchedule)

            if start_date:
                statement = statement.where(ProductionSchedule.scheduled_date >= start_date)
            if end_date:
                statement = statement.where(ProductionSchedule.scheduled_date <= end_date)

            schedules = session.exec(statement.order_by(ProductionSchedule.scheduled_date)).all()

            result = []
            for schedule in schedules:
                order = session.get(ProductionOrder, schedule.order_id)
                result.append({
                    "date": schedule.scheduled_date,
                    "order_number": order.order_number if order else "N/A",
                    "capacity_used": schedule.capacity_used,
                    "workshop": schedule.workshop,
                    "status": schedule.status.value
                })

            return result

    @staticmethod
    def get_purchase_plans(status: PurchaseStatus = None) -> List[PurchasePlan]:
        """Получить планы закупок"""
        with Session(engine) as session:
            statement = select(PurchasePlan)

            if status:
                statement = statement.where(PurchasePlan.status == status)

            return session.exec(statement.order_by(PurchasePlan.planned_date)).all()