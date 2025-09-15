# krai_system/services/finance.py
from typing import Dict, List, Any
from datetime import datetime, timedelta
from decimal import Decimal
from ..models.production_orders import ProductionOrder
from ..models.models import Model
from .database import DatabaseService
from .mrp import MRPService

class FinanceService:
    """Сервис для финансовых расчетов"""
    
    @staticmethod
    def calculate_order_profitability(order_id: str) -> Dict[str, Any]:
        """
        Рассчитать рентабельность заказа
        """
        order = DatabaseService.get_by_id(ProductionOrder, order_id)
        if not order:
            return {"error": "Order not found"}
        
        model = DatabaseService.get_by_id(Model, order.model_id)
        if not model:
            return {"error": "Model not found"}
        
        # Получаем себестоимость производства
        production_cost = MRPService.calculate_production_cost(order_id)
        
        if 'error' in production_cost:
            return production_cost
        
        # Расчет выручки
        total_pairs = production_cost['total_pairs']
        revenue = total_pairs * float(model.retail_price)
        
        # Расчет прибыли
        gross_profit = revenue - production_cost['total_cost']
        
        # Учитываем налоги и дополнительные расходы
        taxes = revenue * 0.20  # НДС 20%
        marketing_cost = revenue * 0.05  # Маркетинг 5%
        logistics_cost = total_pairs * 100  # 100 руб за пару на логистику
        
        net_profit = gross_profit - taxes - marketing_cost - logistics_cost
        
        # Рентабельность
        profitability = (net_profit / revenue * 100) if revenue > 0 else 0
        margin = (gross_profit / revenue * 100) if revenue > 0 else 0
        
        return {
            'order_id': order_id,
            'model': model.name,
            'total_pairs': total_pairs,
            'revenue': round(revenue, 2),
            'production_cost': round(production_cost['total_cost'], 2),
            'gross_profit': round(gross_profit, 2),
            'taxes': round(taxes, 2),
            'marketing_cost': round(marketing_cost, 2),
            'logistics_cost': round(logistics_cost, 2),
            'net_profit': round(net_profit, 2),
            'profitability_percent': round(profitability, 2),
            'margin_percent': round(margin, 2),
            'calculated_at': datetime.now().isoformat()
        }
    
    @staticmethod
    def generate_cash_flow_forecast(days: int = 30) -> Dict[str, Any]:
        """
        Прогноз денежного потока
        """
        forecast = {
            'period_days': days,
            'start_date': datetime.now().isoformat(),
            'end_date': (datetime.now() + timedelta(days=days)).isoformat(),
            'daily_forecast': []
        }
        
        # Начальный баланс (заглушка)
        balance = 1000000.0
        
        for day in range(days):
            date = datetime.now() + timedelta(days=day)
            
            # Имитация поступлений и расходов
            # В реальном приложении здесь будут данные из заказов и платежей
            income = 50000 if day % 3 == 0 else 20000  # Поступления каждые 3 дня
            expenses = 15000  # Ежедневные расходы
            
            balance += income - expenses
            
            forecast['daily_forecast'].append({
                'date': date.isoformat(),
                'income': income,
                'expenses': expenses,
                'net_flow': income - expenses,
                'balance': round(balance, 2)
            })
        
        # Итоговая статистика
        total_income = sum(d['income'] for d in forecast['daily_forecast'])
        total_expenses = sum(d['expenses'] for d in forecast['daily_forecast'])
        
        forecast['summary'] = {
            'total_income': round(total_income, 2),
            'total_expenses': round(total_expenses, 2),
            'net_cash_flow': round(total_income - total_expenses, 2),
            'final_balance': round(balance, 2),
            'average_daily_income': round(total_income / days, 2),
            'average_daily_expenses': round(total_expenses / days, 2)
        }
        
        return forecast
    
    @staticmethod
    def calculate_break_even_point(model_id: str) -> Dict[str, Any]:
        """
        Рассчитать точку безубыточности для модели
        """
        model = DatabaseService.get_by_id(Model, model_id)
        if not model:
            return {"error": "Model not found"}
        
        # Фиксированные затраты (заглушка)
        fixed_costs = {
            'rent': 100000,
            'salaries': 300000,
            'utilities': 50000,
            'depreciation': 30000,
            'other': 20000
        }
        total_fixed = sum(fixed_costs.values())
        
        # Переменные затраты на единицу (из расчета себестоимости)
        # Заглушка - в реальности берем из MRP расчетов
        variable_cost_per_unit = 2500
        
        # Цена продажи
        selling_price = float(model.retail_price)
        
        # Маржинальная прибыль
        contribution_margin = selling_price - variable_cost_per_unit
        
        # Точка безубыточности в единицах
        break_even_units = total_fixed / contribution_margin if contribution_margin > 0 else 0
        
        # Точка безубыточности в деньгах
        break_even_revenue = break_even_units * selling_price
        
        # Запас прочности (при планируемом объеме продаж)
        planned_sales = 1000  # Заглушка
        safety_margin = ((planned_sales - break_even_units) / planned_sales * 100) if planned_sales > 0 else 0
        
        return {
            'model_id': model_id,
            'model_name': model.name,
            'fixed_costs': fixed_costs,
            'total_fixed_costs': round(total_fixed, 2),
            'variable_cost_per_unit': round(variable_cost_per_unit, 2),
            'selling_price': round(selling_price, 2),
            'contribution_margin': round(contribution_margin, 2),
            'break_even_units': round(break_even_units, 0),
            'break_even_revenue': round(break_even_revenue, 2),
            'planned_sales': planned_sales,
            'safety_margin_percent': round(safety_margin, 2),
            'calculated_at': datetime.now().isoformat()
        }
    
    @staticmethod
    def get_financial_dashboard() -> Dict[str, Any]:
        """
        Получить финансовую сводку
        """
        # В реальном приложении здесь будут агрегированные данные из БД
        # Пока используем заглушки
        
        current_month = datetime.now().strftime('%Y-%m')
        
        dashboard = {
            'period': current_month,
            'revenue': {
                'current_month': 5000000,
                'previous_month': 4500000,
                'growth_percent': 11.11
            },
            'expenses': {
                'production': 2500000,
                'materials': 1500000,
                'labor': 800000,
                'overhead': 200000,
                'total': 3000000
            },
            'profit': {
                'gross': 2000000,
                'net': 1600000,
                'margin_percent': 32.0
            },
            'cash_position': {
                'cash_on_hand': 3000000,
                'accounts_receivable': 1500000,
                'accounts_payable': 800000,
                'working_capital': 3700000
            },
            'key_metrics': {
                'average_order_value': 150000,
                'cost_per_pair': 2500,
                'average_margin': 35.0,
                'inventory_turnover': 8.5
            },
            'top_profitable_models': [
                {'model': 'Оксфорды', 'profit': 500000, 'margin': 40},
                {'model': 'Броги', 'profit': 450000, 'margin': 38},
                {'model': 'Монки', 'profit': 400000, 'margin': 35}
            ],
            'updated_at': datetime.now().isoformat()
        }
        
        return dashboard
    
    @staticmethod
    def calculate_roi(investment: float, returns: float, period_days: int) -> Dict[str, Any]:
        """
        Рассчитать ROI (Return on Investment)
        """
        roi = ((returns - investment) / investment * 100) if investment > 0 else 0
        
        # Годовая доходность
        annual_roi = roi * (365 / period_days) if period_days > 0 else 0
        
        return {
            'investment': round(investment, 2),
            'returns': round(returns, 2),
            'profit': round(returns - investment, 2),
            'roi_percent': round(roi, 2),
            'annual_roi_percent': round(annual_roi, 2),
            'period_days': period_days,
            'calculated_at': datetime.now().isoformat()
        }