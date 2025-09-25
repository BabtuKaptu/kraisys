"""
API endpoints for Production Orders
"""

from typing import List
from fastapi import APIRouter, HTTPException, Query
from datetime import datetime, date

router = APIRouter()

# Mock production orders data
mock_production_orders = [
    {
        "id": 1,
        "uuid": "prod-uuid-1",
        "order_number": "ПЗ-2024-001",
        "model_id": 1,
        "model_name": "SPORT",
        "model_article": "250",
        "total_pairs": 120,
        "priority": "HIGH",
        "status": "IN_PROGRESS",
        "planned_start_date": "2024-09-20",
        "planned_end_date": "2024-10-05",
        "actual_start_date": "2024-09-20",
        "actual_end_date": None,
        "created_at": "2024-09-19T10:00:00",
        "order_sizes": [
            {"size": "40", "quantity": 15},
            {"size": "41", "quantity": 20},
            {"size": "42", "quantity": 25},
            {"size": "43", "quantity": 30},
            {"size": "44", "quantity": 20},
            {"size": "45", "quantity": 10}
        ],
        "material_requirements": [
            {
                "material_id": 1,
                "material_name": "Кожа натуральная черная",
                "required_quantity": 180.5,
                "unit": "дм²",
                "allocated_quantity": 150.0,
                "status": "PARTIAL"
            },
            {
                "material_id": 2,
                "material_name": "Подошва 888",
                "required_quantity": 120,
                "unit": "пар",
                "allocated_quantity": 120,
                "status": "ALLOCATED"
            }
        ]
    },
    {
        "id": 2,
        "uuid": "prod-uuid-2",
        "order_number": "ПЗ-2024-002",
        "model_id": 2,
        "model_name": "BRUNO",
        "model_article": "450",
        "total_pairs": 80,
        "priority": "MEDIUM",
        "status": "PLANNED",
        "planned_start_date": "2024-10-01",
        "planned_end_date": "2024-10-15",
        "actual_start_date": None,
        "actual_end_date": None,
        "created_at": "2024-09-18T14:30:00",
        "order_sizes": [
            {"size": "39", "quantity": 10},
            {"size": "40", "quantity": 15},
            {"size": "41", "quantity": 20},
            {"size": "42", "quantity": 20},
            {"size": "43", "quantity": 10},
            {"size": "44", "quantity": 5}
        ],
        "material_requirements": []
    }
]


@router.get("/orders")
async def get_production_orders(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    search: str = Query(None),
    status: str = Query(None),
    priority: str = Query(None)
):
    """Get production orders with filtering"""

    filtered_orders = mock_production_orders.copy()

    if search:
        filtered_orders = [
            o for o in filtered_orders
            if search.lower() in o["order_number"].lower() or search.lower() in o["model_name"].lower()
        ]

    if status:
        filtered_orders = [o for o in filtered_orders if o["status"] == status]

    if priority:
        filtered_orders = [o for o in filtered_orders if o["priority"] == priority]

    # Pagination
    total = len(filtered_orders)
    start = (page - 1) * size
    end = start + size
    paginated_orders = filtered_orders[start:end]

    return {
        "orders": paginated_orders,
        "total": total,
        "page": page,
        "size": size
    }


@router.get("/orders/{order_id}")
async def get_production_order(order_id: int):
    """Get specific production order"""
    order = next((o for o in mock_production_orders if o["id"] == order_id), None)
    if not order:
        raise HTTPException(status_code=404, detail="Production order not found")
    return order


@router.get("/stats/summary")
async def get_production_stats():
    """Get production statistics summary"""
    total_orders = len(mock_production_orders)
    in_progress = len([o for o in mock_production_orders if o["status"] == "IN_PROGRESS"])
    completed = len([o for o in mock_production_orders if o["status"] == "COMPLETED"])
    planned = len([o for o in mock_production_orders if o["status"] == "PLANNED"])

    total_pairs = sum(o["total_pairs"] for o in mock_production_orders)
    completed_pairs = sum(o["total_pairs"] for o in mock_production_orders if o["status"] == "COMPLETED")

    return {
        "total_orders": total_orders,
        "orders_in_progress": in_progress,
        "orders_completed": completed,
        "orders_planned": planned,
        "total_pairs_ordered": total_pairs,
        "total_pairs_completed": completed_pairs,
        "completion_rate": (completed_pairs / total_pairs * 100) if total_pairs > 0 else 0
    }


from pydantic import BaseModel

class ProductionOrderCreate(BaseModel):
    order_number: str
    model_article: str
    quantity: int
    priority: str = "normal"
    deadline: str
    size_distribution: dict

@router.post("/orders")
async def create_production_order(order_data: ProductionOrderCreate):
    """Create new production order"""
    new_id = max(o["id"] for o in mock_production_orders) + 1 if mock_production_orders else 1

    # Convert size distribution to order_sizes format
    order_sizes = [
        {"size": str(size), "quantity": qty}
        for size, qty in order_data.size_distribution.items()
    ]

    new_order = {
        "id": new_id,
        "uuid": f"prod-uuid-{new_id}",
        "order_number": order_data.order_number,
        "model_article": order_data.model_article,
        "total_pairs": order_data.quantity,
        "priority": order_data.priority.upper(),
        "status": "PLANNED",
        "planned_start_date": order_data.deadline,
        "planned_end_date": order_data.deadline,
        "actual_start_date": None,
        "actual_end_date": None,
        "created_at": datetime.now().isoformat(),
        "order_sizes": order_sizes,
        "material_requirements": []
    }

    mock_production_orders.append(new_order)
    return new_order


@router.put("/orders/{order_id}/status")
async def update_order_status(order_id: int, status: str):
    """Update production order status"""
    order = next((o for o in mock_production_orders if o["id"] == order_id), None)
    if not order:
        raise HTTPException(status_code=404, detail="Production order not found")

    old_status = order["status"]
    order["status"] = status

    # Update actual dates based on status
    if status == "IN_PROGRESS" and not order["actual_start_date"]:
        order["actual_start_date"] = datetime.now().date().isoformat()
    elif status == "COMPLETED" and not order["actual_end_date"]:
        order["actual_end_date"] = datetime.now().date().isoformat()

    return {
        "message": "Status updated successfully",
        "order_id": order_id,
        "old_status": old_status,
        "new_status": status
    }


@router.get("/stats/dashboard")
async def get_production_dashboard():
    """Get production dashboard statistics"""
    total_orders = len(mock_production_orders)
    planned_orders = len([o for o in mock_production_orders if o["status"] == "PLANNED"])
    in_progress_orders = len([o for o in mock_production_orders if o["status"] == "IN_PROGRESS"])
    completed_orders = len([o for o in mock_production_orders if o["status"] == "COMPLETED"])

    total_pairs = sum(o["total_pairs"] for o in mock_production_orders)
    completed_pairs = sum(o["total_pairs"] for o in mock_production_orders if o["status"] == "COMPLETED")

    return {
        "total_orders": total_orders,
        "planned_orders": planned_orders,
        "in_progress_orders": in_progress_orders,
        "completed_orders": completed_orders,
        "total_pairs": total_pairs,
        "completed_pairs": completed_pairs,
        "completion_rate": (completed_pairs / total_pairs * 100) if total_pairs > 0 else 0,
        "orders_by_priority": {
            "HIGH": len([o for o in mock_production_orders if o["priority"] == "HIGH"]),
            "MEDIUM": len([o for o in mock_production_orders if o["priority"] == "MEDIUM"]),
            "LOW": len([o for o in mock_production_orders if o["priority"] == "LOW"])
        }
    }