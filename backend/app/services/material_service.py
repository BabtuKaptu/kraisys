"""Service layer for materials."""

from __future__ import annotations

from typing import List, Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Material
from app.schemas.material import (
    Material as MaterialSchema,
    MaterialCreateRequest,
    MaterialDraft,
    MaterialsListResult,
    MaterialReference,
    MaterialResponse,
    MaterialSpecs,
    MaterialStockSettings,
    MaterialSupplyInfo,
    MaterialUpdateRequest,
    MaterialsListItem,
    MaterialsListQuery,
)


class MaterialService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_materials(self, query: MaterialsListQuery) -> MaterialsListResult:
        base_stmt = select(Material)

        if query.search:
            pattern = f"%{query.search.lower()}%"
            base_stmt = base_stmt.where(
                func.lower(Material.name).like(pattern)
                | func.lower(Material.code).like(pattern)
            )
        if query.group:
            base_stmt = base_stmt.where(Material.group == query.group)
        if query.subgroup:
            base_stmt = base_stmt.where(Material.subgroup == query.subgroup)
        if query.isActive is not None:
            base_stmt = base_stmt.where(Material.is_active == query.isActive)
        if query.isCritical is not None:
            base_stmt = base_stmt.where(Material.is_critical == query.isCritical)
        if query.priceMin is not None:
            base_stmt = base_stmt.where(Material.price >= query.priceMin)
        if query.priceMax is not None:
            base_stmt = base_stmt.where(Material.price <= query.priceMax)

        count_stmt = select(func.count()).select_from(base_stmt.subquery())
        total = self.db.scalar(count_stmt) or 0

        stmt = (
            base_stmt.order_by(Material.updated_at.desc())
            .offset((query.page - 1) * query.pageSize)
            .limit(query.pageSize)
        )
        materials = self.db.scalars(stmt).all()

        items: List[MaterialsListItem] = [self._to_list_item(mat) for mat in materials]
        return MaterialsListResult(items=items, total=total, page=query.page, pageSize=query.pageSize)

    def get_material(self, material_id: UUID) -> MaterialResponse:
        material = self.db.get(Material, material_id)
        if not material:
            raise ValueError("Material not found")
        return self._to_response(material)

    def create_material(self, payload: MaterialCreateRequest) -> MaterialResponse:
        material = Material()
        self._apply_draft(material, payload)
        self.db.add(material)
        self.db.commit()
        self.db.refresh(material)
        return self._to_response(material)

    def update_material(self, material_id: UUID, payload: MaterialUpdateRequest) -> MaterialResponse:
        material = self.db.get(Material, material_id)
        if not material:
            raise ValueError("Material not found")
        self._apply_draft(material, payload)
        self.db.commit()
        self.db.refresh(material)
        return self._to_response(material)

    def delete_material(self, material_id: UUID) -> None:
        material = self.db.get(Material, material_id)
        if not material:
            return
        self.db.delete(material)
        self.db.commit()

    # ------------------------------------------------------------------
    @staticmethod
    def _apply_draft(material: Material, draft: MaterialDraft) -> None:
        material.code = draft.code
        material.name = draft.name
        material.name_en = draft.nameEn
        material.group = draft.group
        material.subgroup = draft.subgroup
        material.material_type = draft.materialType
        material.color = draft.color
        material.is_active = draft.isActive
        material.is_critical = draft.isCritical
        material.description = draft.description

        material.texture = draft.specs.texture
        material.thickness_mm = draft.specs.thicknessMm
        material.density = draft.specs.density
        material.unit_primary = draft.specs.unitPrimary
        material.unit_secondary = draft.specs.unitSecondary
        material.conversion_factor = draft.specs.conversionFactor
        material.specs_notes = draft.specs.notes

        material.price = draft.supply.price
        material.currency = draft.supply.currency
        material.supplier_name = draft.supply.supplierName
        material.supplier_code = draft.supply.supplierCode
        material.lead_time_days = draft.supply.leadTimeDays
        material.min_order_qty = draft.supply.minOrderQty
        material.order_multiplicity = draft.supply.orderMultiplicity
        material.storage_conditions = draft.supply.storageConditions
        material.warranty_months = draft.supply.warrantyMonths

        material.safety_stock = draft.stock.safetyStock
        material.reorder_point = draft.stock.reorderPoint
        material.max_stock = draft.stock.maxStock
        material.warehouse_code = draft.stock.warehouseCode
        material.lot_tracked = draft.stock.lotTracked

    @staticmethod
    def _to_list_item(material: Material) -> MaterialsListItem:
        return MaterialsListItem(
            id=material.material_id,
            code=material.code,
            name=material.name,
            group=material.group,
            subgroup=material.subgroup,
            unit=material.unit_primary,
            price=float(material.price) if material.price is not None else None,
            supplierName=material.supplier_name,
            leadTimeDays=material.lead_time_days,
            isActive=material.is_active,
            isCritical=material.is_critical,
            updatedAt=material.updated_at,
        )

    @staticmethod
    def _to_reference(material: Optional[Material]) -> Optional[MaterialReference]:
        if material is None:
            return None
        return MaterialReference(
            id=material.material_id,
            code=material.code,
            name=material.name,
            group=material.group,
            unit=material.unit_primary,
            color=material.color,
        )

    def _to_response(self, material: Material) -> MaterialResponse:
        specs = MaterialSpecs(
            texture=material.texture,
            thicknessMm=float(material.thickness_mm) if material.thickness_mm is not None else None,
            density=float(material.density) if material.density is not None else None,
            unitPrimary=material.unit_primary,
            unitSecondary=material.unit_secondary,
            conversionFactor=float(material.conversion_factor)
            if material.conversion_factor is not None
            else None,
            notes=material.specs_notes,
        )
        supply = MaterialSupplyInfo(
            price=float(material.price) if material.price is not None else None,
            currency=material.currency,
            supplierName=material.supplier_name,
            supplierCode=material.supplier_code,
            leadTimeDays=material.lead_time_days,
            minOrderQty=float(material.min_order_qty) if material.min_order_qty is not None else None,
            orderMultiplicity=float(material.order_multiplicity)
            if material.order_multiplicity is not None
            else None,
            storageConditions=material.storage_conditions,
            warrantyMonths=material.warranty_months,
        )
        stock = MaterialStockSettings(
            safetyStock=float(material.safety_stock) if material.safety_stock is not None else None,
            reorderPoint=float(material.reorder_point) if material.reorder_point is not None else None,
            maxStock=float(material.max_stock) if material.max_stock is not None else None,
            warehouseCode=material.warehouse_code,
            lotTracked=material.lot_tracked,
        )

        return MaterialResponse(
            id=material.material_id,
            uuid=material.material_id,
            code=material.code,
            name=material.name,
            nameEn=material.name_en,
            group=material.group,
            subgroup=material.subgroup,
            materialType=material.material_type,
            color=material.color,
            isActive=material.is_active,
            isCritical=material.is_critical,
            description=material.description,
            specs=specs,
            supply=supply,
            stock=stock,
            attachments=[],
            createdAt=material.created_at,
            updatedAt=material.updated_at,
        )
