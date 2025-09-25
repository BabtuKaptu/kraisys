"""Service layer for footwear models working with SQLAlchemy models."""

from __future__ import annotations

from typing import Dict, Iterable, List, Optional
from uuid import UUID

from sqlalchemy import func, or_, select, text
from sqlalchemy.orm import Session, joinedload, selectinload

import logging

from app.models import (
    CuttingPart,
    Material,
    Model,
    ModelCuttingPart,
    ModelHardwareCompatibleMaterial,
    ModelHardwareItem,
    ModelHardwareSet,
    ModelInsoleOption,
    ModelPerforation,
    ModelSoleOption,
    ModelVariant,
    ModelVariantCuttingPart,
)
from app.schemas.material import MaterialReference
from app.schemas.model import (
    CuttingPartUsage,
    HardwareItemOption,
    HardwareSet as HardwareSetSchema,
    InsoleOption as InsoleOptionSchema,
    Model as ModelSchema,
    ModelCreateRequest,
    ModelDraft,
    ModelListItem,
    ModelResponse,
    ModelSuperBOM,
    ModelUpdateRequest,
    ModelVariant as ModelVariantSchema,
    ModelVariantSpecification,
    ModelsListQuery,
    ModelsListResult,
    PerforationOption as PerforationOptionSchema,
    SoleOption as SoleOptionSchema,
)
from app.schemas.reference import ReferenceItem


logger = logging.getLogger(__name__)

def _material_to_reference(material: Optional[Material]) -> Optional[MaterialReference]:
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


def _cutting_part_to_reference(part: Optional["CuttingPart"]):
    if part is None:
        return None
    return ReferenceItem(
        id=part.part_id,
        type="cutting_part",
        code=part.code,
        name=part.name,
        description=part.notes,
        isActive=True,
        attributes={"category": part.category, "unit": part.unit},
    )


class ModelService:
    """Encapsulates database operations for models."""

    def __init__(self, db: Session) -> None:
        self.db = db

    # ------------------------------------------------------------------
    # Query helpers
    # ------------------------------------------------------------------
    def list_models(self, query: ModelsListQuery) -> ModelsListResult:
        base_stmt = select(Model)

        if query.search:
            pattern = f"%{query.search.lower()}%"
            base_stmt = base_stmt.where(
                or_(
                    func.lower(Model.name).like(pattern),
                    func.lower(Model.article).like(pattern),
                )
            )
        if query.gender:
            base_stmt = base_stmt.where(Model.gender == query.gender)
        if query.modelType:
            base_stmt = base_stmt.where(Model.model_type == query.modelType)
        if query.category:
            base_stmt = base_stmt.where(Model.category == query.category)
        if query.status:
            is_active = query.status.upper() == "ACTIVE"
            base_stmt = base_stmt.where(Model.is_active == is_active)

        count_stmt = select(func.count()).select_from(base_stmt.subquery())
        total = self.db.scalar(count_stmt) or 0

        stmt = (
            base_stmt.options(selectinload(Model.sole_options))
            .order_by(Model.updated_at.desc())
            .offset((query.page - 1) * query.pageSize)
            .limit(query.pageSize)
        )

        models = self.db.scalars(stmt).all()

        items: List[ModelListItem] = []
        for model in models:
            default_sole = None
            if model.default_sole_option_id:
                default = next(
                    (s for s in model.sole_options if s.sole_option_id == model.default_sole_option_id),
                    None,
                )
                if default:
                    default_sole = default.name
            else:
                default = next((s for s in model.sole_options if s.is_default), None)
                if default:
                    default_sole = default.name

            items.append(
                ModelListItem(
                    id=model.model_id,
                    article=model.article,
                    name=model.name,
                    gender=model.gender,
                    modelType=model.model_type,
                    category=model.category,
                    sizeRange=f"{model.size_min}-{model.size_max}",
                    defaultSole=default_sole,
                    status="ACTIVE" if model.is_active else "INACTIVE",
                    updatedAt=model.updated_at,
                )
            )

        return ModelsListResult(items=items, total=total, page=query.page, pageSize=query.pageSize)

    # ------------------------------------------------------------------
    def get_model(self, model_id: UUID) -> ModelResponse:
        stmt = (
            select(Model)
            .options(
                selectinload(Model.perforation_options),
                selectinload(Model.insole_options),
                selectinload(Model.hardware_sets).selectinload(ModelHardwareSet.items).selectinload(
                    ModelHardwareItem.compatible_materials
                ),
                selectinload(Model.cutting_parts).selectinload(ModelCuttingPart.reference_part),
                selectinload(Model.cutting_parts).selectinload(ModelCuttingPart.material),
                selectinload(Model.sole_options).selectinload(ModelSoleOption.material),
                selectinload(Model.variants)
                .selectinload(ModelVariant.customized_cutting_parts)
                .selectinload(ModelVariantCuttingPart.material),
            )
            .where(Model.model_id == model_id)
        )
        model = self.db.scalars(stmt).first()
        if not model:
            raise ValueError("Model not found")
        return self._serialize_model(model)

    # ------------------------------------------------------------------
    def create_model(self, payload: ModelCreateRequest) -> ModelResponse:
        logger.info("create_model: start")

        # Single atomic transaction; staged flush for early error detection
        with self.db.begin():
            # Fail-fast on long-running statements inside this txn
            try:
                self.db.execute(text("SET LOCAL statement_timeout = 15000"))
            except Exception:
                # Not all backends accept statement_timeout; ignore if unsupported
                pass

            # 1) Base model
            model = Model()
            self._apply_base_fields(model, payload)
            self.db.add(model)
            self.db.flush()  # obtain model_id
            logger.info("create_model: base model flushed")

            sb = payload.superBom or ModelSuperBOM()

            # 2) Perforations
            for opt in (sb.perforationOptions or []):
                entity = ModelPerforation(
                    model_id=model.model_id,
                    name=opt.name,
                    code=opt.code,
                    description=opt.description,
                    preview_image=opt.previewImage,
                    is_default=bool(opt.isDefault),
                    is_active=bool(opt.isActive),
                )
                if opt.id:
                    entity.perforation_id = opt.id
                self.db.add(entity)
            self.db.flush()
            logger.info("create_model: perforations flushed")

            # 3) Insoles
            for opt in (sb.insoleOptions or []):
                entity = ModelInsoleOption(
                    model_id=model.model_id,
                    name=opt.name,
                    material=opt.material,
                    seasonality=opt.seasonality,
                    thickness_mm=opt.thicknessMm,
                    is_default=bool(opt.isDefault),
                    is_active=bool(opt.isActive),
                )
                if opt.id:
                    entity.insole_option_id = opt.id
                self.db.add(entity)
            self.db.flush()
            logger.info("create_model: insoles flushed")

            # 4) Hardware sets and items
            for hs in (sb.hardwareSets or []):
                hs_entity = ModelHardwareSet(
                    model_id=model.model_id,
                    name=hs.name,
                    description=hs.description,
                    is_default=bool(hs.isDefault),
                    is_active=bool(hs.isActive),
                )
                if hs.id:
                    hs_entity.hardware_set_id = hs.id
                self.db.add(hs_entity)
                self.db.flush()  # obtain hardware_set_id for items

                for item in (hs.items or []):
                    it_entity = ModelHardwareItem(
                        hardware_set_id=hs_entity.hardware_set_id,
                        name=item.name,
                        material_group=item.materialGroup,
                        requires_exact_selection=bool(item.requiresExactSelection),
                        notes=item.notes,
                    )
                    if item.id:
                        it_entity.hardware_item_id = item.id
                    self.db.add(it_entity)
                    self.db.flush()  # need id to link compatible materials

                    # Compatible materials links
                    for mat in (item.compatibleMaterials or []):
                        if getattr(mat, "id", None):
                            link = ModelHardwareCompatibleMaterial(
                                hardware_item_id=it_entity.hardware_item_id,
                                material_id=mat.id,
                            )
                            self.db.add(link)
            self.db.flush()
            logger.info("create_model: hardware flushed")

            # 5) Cutting parts
            for cp in (payload.cuttingParts or []):
                entity = ModelCuttingPart(
                    model_id=model.model_id,
                    reference_part_id=(cp.part.id if cp.part else None),
                    material_id=(cp.material.id if cp.material else None),
                    quantity=cp.quantity or 0,
                    consumption_per_pair=cp.consumptionPerPair,
                    labor_cost=cp.laborCost,
                    notes=cp.notes,
                )
                if cp.id:
                    entity.cutting_part_id = cp.id
                self.db.add(entity)
            self.db.flush()
            logger.info("create_model: cutting parts flushed")

            # 6) Sole options
            default_sole_id = payload.defaultSoleOptionId
            for so in (payload.soleOptions or []):
                entity = ModelSoleOption(
                    model_id=model.model_id,
                    name=so.name,
                    material_id=(so.material.id if so.material else None),
                    size_min=so.sizeMin,
                    size_max=so.sizeMax,
                    is_default=bool(so.isDefault),
                    color=so.color,
                    notes=so.notes,
                )
                if so.id:
                    entity.sole_option_id = so.id
                self.db.add(entity)
                self.db.flush()
                if default_sole_id is None and so.isDefault:
                    default_sole_id = entity.sole_option_id

            # Update default sole on model if provided or inferred
            model.default_sole_option_id = default_sole_id
            logger.info("create_model: sole options flushed")

        # Transaction committed here
        self.db.refresh(model)
        logger.info("create_model: committed and refreshed")
        return self.get_model(model.model_id)

    def _apply_base_fields(self, model: Model, draft: ModelDraft) -> None:
        """Apply only scalar/base fields from draft without touching collections."""
        model.name = draft.name
        model.article = draft.article
        model.gender = draft.gender
        model.model_type = draft.modelType
        model.category = draft.category
        model.collection = draft.collection
        model.season = draft.season
        model.last_code = draft.lastCode
        model.last_type = draft.lastType
        model.lacing_type = draft.lacingType
        model.size_min = draft.sizeMin
        model.size_max = draft.sizeMax
        model.is_active = draft.isActive
        model.retail_price = draft.retailPrice
        model.wholesale_price = draft.wholesalePrice
        model.material_cost = draft.materialCost
        model.labor_cost = draft.laborCost
        model.overhead_cost = draft.overheadCost
        model.description = draft.description
        model.notes = draft.notes

    # ------------------------------------------------------------------
    def update_model(self, model_id: UUID, payload: ModelUpdateRequest) -> ModelResponse:
        """Update model in a single atomic transaction with staged flush.

        Mirrors the staged approach used in create_model to avoid long-running
        operations and to surface FK/constraint errors early. Rolls back fully
        on any error.
        """
        logger.info("update_model: start")

        # Atomic transaction (begin BEFORE any DB I/O to avoid implicit txn)
        with self.db.begin():
            # Best-effort per-txn statement timeout (PostgreSQL); ignore if unsupported
            try:
                self.db.execute(text("SET LOCAL statement_timeout = 15000"))
            except Exception:
                pass

            # Load inside the transaction to avoid implicit pre-begin
            model = self.db.get(Model, model_id)
            if not model:
                raise ValueError("Model not found")

            # 1) Base/scalar fields first
            self._apply_base_fields(model, payload)
            self.db.flush()

            # 2) SUPER-BOM sections
            sb = payload.superBom or ModelSuperBOM()

            self._sync_perforations(model, sb.perforationOptions or [])
            self.db.flush()

            self._sync_insoles(model, sb.insoleOptions or [])
            self.db.flush()

            self._sync_hardware(model, sb.hardwareSets or [])
            self.db.flush()

            # 3) Cutting parts
            self._sync_cutting_parts(model, payload.cuttingParts or [])
            self.db.flush()

            # 4) Sole options and default
            self._sync_sole_options(model, payload.soleOptions or [], payload.defaultSoleOptionId)
            self.db.flush()

        # Transaction committed here if no errors
        self.db.refresh(model)
        logger.info("update_model: committed and refreshed")
        return self.get_model(model_id)

    # ------------------------------------------------------------------
    def delete_model(self, model_id: UUID) -> None:
        model = self.db.get(Model, model_id)
        if not model:
            return
        self.db.delete(model)
        self.db.commit()

    # ------------------------------------------------------------------
    def upsert_variant(self, model_id: UUID, payload: ModelVariantSchema) -> ModelResponse:
        model = self.db.get(Model, model_id)
        if not model:
            raise ValueError("Model not found")

        entity: Optional[ModelVariant] = None
        if payload.id:
            entity = next((variant for variant in model.variants if variant.variant_id == payload.id), None)

        if entity is None:
            entity = ModelVariant()
            if payload.id:
                entity.variant_id = payload.id
            model.variants.append(entity)

        specification = payload.specification or ModelVariantSpecification()

        entity.name = payload.name
        entity.code = payload.code
        entity.status = payload.status or 'ACTIVE'
        entity.is_default = bool(payload.isDefault)
        entity.notes = specification.notes
        entity.total_material_cost = payload.totalMaterialCost
        entity.perforation_option_id = specification.perforationOptionId
        entity.insole_option_id = specification.insoleOptionId
        entity.hardware_set_id = specification.hardwareSetId
        entity.sole_option_id = specification.soleOptionId

        self._sync_variant_cutting_parts(entity, specification.customizedCuttingParts or [])

        if entity.is_default:
            for variant in model.variants:
                if variant is not entity:
                    variant.is_default = False

        self.db.commit()
        self.db.refresh(model)
        return self._serialize_model(model)

    # ------------------------------------------------------------------
    def delete_variant(self, model_id: UUID, variant_id: UUID) -> ModelResponse:
        model = self.db.get(Model, model_id)
        if not model:
            raise ValueError("Model not found")
        entity = next((variant for variant in model.variants if variant.variant_id == variant_id), None)
        if not entity:
            raise ValueError("Variant not found")
        self.db.delete(entity)
        self.db.commit()
        self.db.refresh(model)
        return self._serialize_model(model)

    # ------------------------------------------------------------------
    # Serialization helpers
    # ------------------------------------------------------------------
    def _serialize_model(self, model: Model) -> ModelResponse:
        perforations = [
            PerforationOptionSchema(
                id=item.perforation_id,
                name=item.name,
                code=item.code,
                description=item.description,
                previewImage=item.preview_image,
                isDefault=item.is_default,
                isActive=item.is_active,
            )
            for item in model.perforation_options
        ]

        insoles = [
            InsoleOptionSchema(
                id=item.insole_option_id,
                name=item.name,
                material=item.material,
                seasonality=item.seasonality,
                thicknessMm=item.thickness_mm,
                isDefault=item.is_default,
                isActive=item.is_active,
            )
            for item in model.insole_options
        ]

        hardware_sets = []
        for hw_set in model.hardware_sets:
            items: List[HardwareItemOption] = []
            for hw_item in hw_set.items:
                compatible = [
                    _material_to_reference(link.material) for link in hw_item.compatible_materials
                ]
                items.append(
                    HardwareItemOption(
                        id=hw_item.hardware_item_id,
                        name=hw_item.name,
                        materialGroup=hw_item.material_group,
                        compatibleMaterials=[ref for ref in compatible if ref is not None],
                        requiresExactSelection=hw_item.requires_exact_selection,
                        notes=hw_item.notes,
                    )
                )
            hardware_sets.append(
                HardwareSetSchema(
                    id=hw_set.hardware_set_id,
                    name=hw_set.name,
                    description=hw_set.description,
                    items=items,
                    isDefault=hw_set.is_default,
                    isActive=hw_set.is_active,
                )
            )

        cutting_parts = [
            CuttingPartUsage(
                id=item.cutting_part_id,
                part=_cutting_part_to_reference(item.reference_part),
                material=_material_to_reference(item.material),
                quantity=item.quantity,
                consumptionPerPair=item.consumption_per_pair,
                laborCost=item.labor_cost,
                notes=item.notes,
            )
            for item in model.cutting_parts
        ]

        sole_options = [
            SoleOptionSchema(
                id=item.sole_option_id,
                name=item.name,
                material=_material_to_reference(item.material),
                sizeMin=item.size_min,
                sizeMax=item.size_max,
                isDefault=item.is_default,
                color=item.color,
                notes=item.notes,
            )
            for item in model.sole_options
        ]

        variants: List[ModelVariantSchema] = []
        for variant in model.variants:
            specification = ModelVariantSpecification(
                perforationOptionId=variant.perforation_option_id,
                insoleOptionId=variant.insole_option_id,
                hardwareSetId=variant.hardware_set_id,
                soleOptionId=variant.sole_option_id,
                customizedCuttingParts=[
                    CuttingPartUsage(
                        id=item.variant_cutting_part_id,
                        part=_cutting_part_to_reference(item.base_cutting_part.reference_part)
                        if item.base_cutting_part
                        else None,
                        material=_material_to_reference(item.material),
                        quantity=item.quantity,
                    )
                    for item in variant.customized_cutting_parts
                ],
            )
            variants.append(
                ModelVariantSchema(
                    id=variant.variant_id,
                    modelId=model.model_id,
                    name=variant.name,
                    code=variant.code,
                    isDefault=variant.is_default,
                    status=variant.status,
                    specification=specification,
                    totalMaterialCost=float(variant.total_material_cost)
                    if variant.total_material_cost is not None
                    else None,
                    createdAt=variant.created_at,
                    updatedAt=variant.updated_at,
                )
            )

        response = ModelSchema(
            id=model.model_id,
            uuid=model.model_id,
            name=model.name,
            article=model.article,
            gender=model.gender,
            modelType=model.model_type,
            category=model.category,
            collection=model.collection,
            season=model.season,
            lastCode=model.last_code,
            lastType=model.last_type,
            sizeMin=model.size_min,
            sizeMax=model.size_max,
            lacingType=model.lacing_type,
            defaultSoleOptionId=model.default_sole_option_id,
            isActive=model.is_active,
            retailPrice=float(model.retail_price) if model.retail_price is not None else None,
            wholesalePrice=float(model.wholesale_price) if model.wholesale_price is not None else None,
            materialCost=float(model.material_cost) if model.material_cost is not None else None,
            laborCost=float(model.labor_cost) if model.labor_cost is not None else None,
            overheadCost=float(model.overhead_cost) if model.overhead_cost is not None else None,
            description=model.description,
            superBom=ModelSuperBOM(
                perforationOptions=perforations,
                insoleOptions=insoles,
                hardwareSets=hardware_sets,
            ),
            cuttingParts=cutting_parts,
            soleOptions=sole_options,
            notes=model.notes,
            attachments=[],
            variants=variants,
            createdAt=model.created_at,
            updatedAt=model.updated_at,
            kpis=[],
        )

        return ModelResponse(**response.dict())

    # ------------------------------------------------------------------
    def _apply_draft(self, model: Model, draft: ModelDraft) -> None:
        logger.info("_apply_draft: start")
        model.name = draft.name
        model.article = draft.article
        model.gender = draft.gender
        model.model_type = draft.modelType
        model.category = draft.category
        model.collection = draft.collection
        model.season = draft.season
        model.last_code = draft.lastCode
        model.last_type = draft.lastType
        model.lacing_type = draft.lacingType
        model.size_min = draft.sizeMin
        model.size_max = draft.sizeMax
        model.is_active = draft.isActive
        model.retail_price = draft.retailPrice
        model.wholesale_price = draft.wholesalePrice
        model.material_cost = draft.materialCost
        model.labor_cost = draft.laborCost
        model.overhead_cost = draft.overheadCost
        model.description = draft.description
        model.notes = draft.notes
        model.default_sole_option_id = draft.defaultSoleOptionId

        self._sync_perforations(model, draft.superBom.perforationOptions)
        self._sync_insoles(model, draft.superBom.insoleOptions)
        self._sync_hardware(model, draft.superBom.hardwareSets)
        self._sync_cutting_parts(model, draft.cuttingParts)
        self._sync_sole_options(model, draft.soleOptions, draft.defaultSoleOptionId)
        logger.info("_apply_draft: completed")

    # ------------------------------------------------------------------
    def _sync_perforations(self, model: Model, items: Iterable[PerforationOptionSchema]) -> None:
        existing: Dict[UUID, ModelPerforation] = {p.perforation_id: p for p in model.perforation_options}
        updated: Dict[UUID, ModelPerforation] = {}

        for item in items:
            if item.id in existing:
                entity = existing[item.id]
            else:
                entity = ModelPerforation()
                if item.id:
                    entity.perforation_id = item.id
                model.perforation_options.append(entity)
            entity.name = item.name
            entity.code = item.code
            entity.description = item.description
            entity.preview_image = item.previewImage
            entity.is_default = item.isDefault
            entity.is_active = item.isActive
            if entity.perforation_id:
                updated[entity.perforation_id] = entity

        for pk, entity in existing.items():
            if pk not in updated:
                model.perforation_options.remove(entity)
                self.db.delete(entity)

    # ------------------------------------------------------------------
    def _sync_insoles(self, model: Model, items: Iterable[InsoleOptionSchema]) -> None:
        existing: Dict[UUID, ModelInsoleOption] = {i.insole_option_id: i for i in model.insole_options}
        updated: Dict[UUID, ModelInsoleOption] = {}

        for item in items:
            if item.id in existing:
                entity = existing[item.id]
            else:
                entity = ModelInsoleOption()
                if item.id:
                    entity.insole_option_id = item.id
                model.insole_options.append(entity)
            entity.name = item.name
            entity.material = item.material
            entity.seasonality = item.seasonality
            entity.thickness_mm = item.thicknessMm
            entity.is_default = item.isDefault
            entity.is_active = item.isActive
            if entity.insole_option_id:
                updated[entity.insole_option_id] = entity

        for pk, entity in existing.items():
            if pk not in updated:
                model.insole_options.remove(entity)
                self.db.delete(entity)

    # ------------------------------------------------------------------
    def _sync_hardware(self, model: Model, sets: Iterable[HardwareSetSchema]) -> None:
        existing_sets: Dict[UUID, ModelHardwareSet] = {s.hardware_set_id: s for s in model.hardware_sets}
        updated_sets: Dict[UUID, ModelHardwareSet] = {}

        for hw in sets:
            if hw.id in existing_sets:
                entity = existing_sets[hw.id]
            else:
                entity = ModelHardwareSet()
                if hw.id:
                    entity.hardware_set_id = hw.id
                model.hardware_sets.append(entity)
            entity.name = hw.name
            entity.description = hw.description
            entity.is_default = hw.isDefault
            entity.is_active = hw.isActive
            self._sync_hardware_items(entity, hw.items)
            if entity.hardware_set_id:
                updated_sets[entity.hardware_set_id] = entity

        for pk, entity in existing_sets.items():
            if pk not in updated_sets:
                model.hardware_sets.remove(entity)
                self.db.delete(entity)

    def _sync_hardware_items(
        self, hardware_set: ModelHardwareSet, items: Iterable[HardwareItemOption]
    ) -> None:
        existing_items: Dict[UUID, ModelHardwareItem] = {
            item.hardware_item_id: item for item in hardware_set.items
        }
        updated_items: Dict[UUID, ModelHardwareItem] = {}

        for item in items:
            if item.id in existing_items:
                entity = existing_items[item.id]
            else:
                entity = ModelHardwareItem()
                if item.id:
                    entity.hardware_item_id = item.id
                hardware_set.items.append(entity)
            entity.name = item.name
            entity.material_group = item.materialGroup
            entity.requires_exact_selection = item.requiresExactSelection
            entity.notes = item.notes
            self._sync_hardware_item_materials(entity, item.compatibleMaterials)
            if entity.hardware_item_id:
                updated_items[entity.hardware_item_id] = entity

        for pk, entity in existing_items.items():
            if pk not in updated_items:
                hardware_set.items.remove(entity)
                self.db.delete(entity)

    def _sync_hardware_item_materials(
        self, hardware_item: ModelHardwareItem, materials: Iterable[MaterialReference]
    ) -> None:
        existing: Dict[UUID, ModelHardwareCompatibleMaterial] = {
            link.material_id: link for link in hardware_item.compatible_materials
        }
        updated: Dict[UUID, ModelHardwareCompatibleMaterial] = {}

        for mat in materials:
            if mat.id is None:
                continue
            if mat.id in existing:
                link = existing[mat.id]
            else:
                link = ModelHardwareCompatibleMaterial(material_id=mat.id)
                hardware_item.compatible_materials.append(link)
            updated[link.material_id] = link

        for pk, link in existing.items():
            if pk not in updated:
                hardware_item.compatible_materials.remove(link)
                self.db.delete(link)

    # ------------------------------------------------------------------
    def _sync_cutting_parts(self, model: Model, parts: Iterable[CuttingPartUsage]) -> None:
        existing: Dict[UUID, ModelCuttingPart] = {p.cutting_part_id: p for p in model.cutting_parts}
        updated: Dict[UUID, ModelCuttingPart] = {}

        for item in parts:
            if item.id in existing:
                entity = existing[item.id]
            else:
                entity = ModelCuttingPart()
                if item.id:
                    entity.cutting_part_id = item.id
                model.cutting_parts.append(entity)
            entity.reference_part_id = item.part.id if item.part else None
            entity.material_id = item.material.id if item.material else None
            entity.quantity = item.quantity
            entity.consumption_per_pair = item.consumptionPerPair
            entity.labor_cost = item.laborCost
            entity.notes = item.notes
            if entity.cutting_part_id:
                updated[entity.cutting_part_id] = entity

        for pk, entity in existing.items():
            if pk not in updated:
                model.cutting_parts.remove(entity)
                self.db.delete(entity)

    # ------------------------------------------------------------------
    def _sync_sole_options(
        self, model: Model, options: Iterable[SoleOptionSchema], default_id: Optional[UUID]
    ) -> None:
        existing: Dict[UUID, ModelSoleOption] = {s.sole_option_id: s for s in model.sole_options}
        updated: Dict[UUID, ModelSoleOption] = {}

        for item in options:
            if item.id in existing:
                entity = existing[item.id]
            else:
                entity = ModelSoleOption()
                if item.id:
                    entity.sole_option_id = item.id
                model.sole_options.append(entity)
            entity.name = item.name
            entity.material_id = item.material.id if item.material else None
            entity.size_min = item.sizeMin
            entity.size_max = item.sizeMax
            entity.is_default = item.isDefault or (default_id is not None and item.id == default_id)
            entity.color = item.color
            entity.notes = item.notes
            if entity.sole_option_id:
                updated[entity.sole_option_id] = entity

        for pk, entity in existing.items():
            if pk not in updated:
                model.sole_options.remove(entity)
                self.db.delete(entity)

        if default_id:
            model.default_sole_option_id = default_id
        else:
            default_option = next((s for s in model.sole_options if s.is_default), None)
            model.default_sole_option_id = default_option.sole_option_id if default_option else None

    # ------------------------------------------------------------------
    def _sync_variant_cutting_parts(
        self, variant: ModelVariant, parts: Iterable[CuttingPartUsage]
    ) -> None:
        existing = list(variant.customized_cutting_parts)
        processed: List[ModelVariantCuttingPart] = []

        for item in parts:
            entity: Optional[ModelVariantCuttingPart] = None
            if item.id:
                entity = next(
                    (link for link in existing if link.variant_cutting_part_id == item.id),
                    None,
                )
            if entity is None:
                entity = ModelVariantCuttingPart()
                if item.id:
                    entity.variant_cutting_part_id = item.id
                variant.customized_cutting_parts.append(entity)

            entity.cutting_part_id = item.part.id if item.part else None
            entity.material_id = item.material.id if item.material else None
            entity.quantity = item.quantity or 0
            processed.append(entity)

        for entity in existing:
            if entity not in processed:
                variant.customized_cutting_parts.remove(entity)
                self.db.delete(entity)
