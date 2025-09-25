# KRAI Frontend UI Specification (v0.6 Mock Integration)

This document describes the React UI scaffolding that mirrors the legacy PyQt 0.4 desktop client. All screens currently operate on top of the local mock services declared in `src/services/mockDataClient.ts` and datasets from `src/mocks`.

## Shared Foundations

- **Types**: Domain contracts live in `src/types`. Key models: `Model`, `ModelDraft`, `Material`, `MaterialDraft`, `WarehouseStockListItem`, `ReferenceItem`.
- **Mock services**: `mockDataClient` exposes clients for models, materials, warehouse operations, and references. Each method returns `Promise` objects to emulate async APIs and supports basic filtering/pagination.
- **React Query**: All pages fetch data via `@tanstack/react-query`, enabling easy swap to real REST endpoints later.

## Models (`src/pages/Models.tsx`)

- **Filters & KPI**: Inline filters (search, gender, type, category, status) and KPI cards (`ModelKpiCards`) summarise catalogue state.
- **Table**: Extended columns reflect article, type, size range, default sole, status, and actions (edit, variants, delete).
- **Model drawer** (`ModelDrawer`): Full-screen drawer structured by tabs:
  - _Основное_: general metadata, pricing, size range.
  - _Конфигурация (SUPER-BOM)_: Form.List editors for perforation options, insole options, hardware sets (with nested items).
  - _Детали и подошвы_: Cutting parts (part/material/consumption/labour) and sole alternatives.
  - _Варианты_: Preview of saved variants with quick access to variant manager.
  - _Заметки_: Comments placeholder and attachment notice.
- **Variants manager** (`ModelVariantsManager`): Modal with table of variants and inline editor for assigning configuration options.

## Materials (`src/pages/Materials.tsx`)

- **Filters & KPI**: Search, group, status, criticality selectors plus KPI cards (`MaterialKpiCards`).
- **Table**: Displays subgroup, unit, price, supplier, lead time, status, criticality.
- **Material drawer** (`MaterialDrawer`): Tabs replicate desktop form — core info, characteristics (thickness, density, units), supply logistics (price, supplier, lead time, MOQ), and stock settings (safety stock, reorder point, lot tracking). Attachments and history remain placeholders.

## Warehouse (`src/pages/Warehouse.tsx`)

- **Stats**: Header cards for positions, total value, critical items.
- **Actions**: Buttons open dialogs for receipts, issues, and the inventory placeholder.
- **Filters**: Search, warehouse, status.
- **Table**: Mirrors desktop layout with material details, batch, quantities, value, warehouse/location, status tags, and relevant dates.
- **Dialogs** (`WarehouseDialogs.tsx`):
  - _Receipt_: Form.List for multiple incoming lines (material, qty, unit, price, warehouse, date).
  - _Issue_: Form.List for stock issues (party, quantity, reason, reference, comments).
  - _Inventory_: Informational modal until back-end integration.

## References (`src/pages/References.tsx`)

- **Navigation**: Sidebar `List` switches between perforation types, lining types, cutting parts, and lasting types.
- **Table**: Shows code, name, description, status, and provides edit/delete stubs.
- **Drawer** (`ReferenceDrawer`): Basic editor for code/name/description/status. Persistence currently displays an informational toast pending API wiring.

## Mock Data

- Defined under `src/mocks` (models, materials, warehouse, references).
- `resetMockData()` helper resets the in-memory stores for testing.

## Next Steps for API Integration

1. Replace calls in `mockDataClient` with real HTTP clients (e.g., Axios) once endpoints are ready.
2. Map backend DTOs to frontend types within service layer.
3. Extend reference drawer submit/delete handlers to call actual endpoints.
4. Enhance warehouse dialogs with validation against live stock balances.

This scaffold ensures feature parity in UI structure with the 0.4 desktop client while keeping mock data pathways isolated for a smooth migration to production APIs.
