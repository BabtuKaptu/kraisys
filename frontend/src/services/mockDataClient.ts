import {
  ListQuery,
  Material,
  MaterialDraft,
  MaterialsListQuery,
  MaterialsListResult,
  Model,
  ModelDraft,
  ModelVariant,
  ModelsListQuery,
  ModelsListResult,
  ReferenceItem,
  ReferenceListQuery,
  WarehouseIssueDraft,
  WarehouseListQuery,
  WarehouseListResult,
  WarehouseReceiptDraft,
  WarehouseInventoryDraft,
  WarehouseStockListItem,
  WarehouseTransaction,
} from '../types';
import {
  mockCuttingParts,
  mockLiningTypes,
  mockMaterials,
  mockModels,
  mockPerforationTypes,
  mockWarehouseStocks,
  mockWarehouseTransactions,
} from '../mocks';

const delay = (ms = 120) => new Promise((resolve) => setTimeout(resolve, ms));

const deepClone = <T>(value: T): T => JSON.parse(JSON.stringify(value));

const createId = () => `id-${Math.random().toString(36).slice(2)}-${Date.now()}`;

let modelsDb: Model[] = deepClone(mockModels);
let materialsDb: Material[] = deepClone(mockMaterials);
let warehouseDb: WarehouseStockListItem[] = deepClone(mockWarehouseStocks);
let transactionsDb: WarehouseTransaction[] = deepClone(mockWarehouseTransactions);

const paginate = <T>(items: T[], query: ListQuery) => {
  const pageSize = query.pageSize ?? 10;
  const page = query.page ?? 1;
  const start = (page - 1) * pageSize;
  const end = start + pageSize;
  return {
    items: items.slice(start, end),
    total: items.length,
    page,
    pageSize,
  };
};

export const mockModelClient = {
  async list(query: ModelsListQuery = {}): Promise<ModelsListResult> {
    await delay();
    const filtered = modelsDb.filter((model) => {
      const matchSearch = query.search
        ? `${model.article} ${model.name}`
            .toLowerCase()
            .includes(query.search.toLowerCase())
        : true;
      const matchGender = query.gender ? model.gender === query.gender : true;
      const matchType = query.modelType ? model.modelType === query.modelType : true;
      const matchCategory = query.category
        ? model.category === query.category
        : true;
      const matchStatus = query.status
        ? (query.status === 'ACTIVE' ? model.isActive : !model.isActive)
        : true;
      return matchSearch && matchGender && matchType && matchCategory && matchStatus;
    });

    const mapped = filtered.map((model) => {
      const status: 'ACTIVE' | 'INACTIVE' = model.isActive ? 'ACTIVE' : 'INACTIVE';
      return {
      id: model.id,
      article: model.article,
      name: model.name,
      gender: model.gender,
      modelType: model.modelType,
      category: model.category,
      sizeRange: `${model.sizeMin}-${model.sizeMax}`,
      defaultSole: model.soleOptions.find((sole) => sole.id === model.defaultSoleOptionId)?.name,
      status,
      updatedAt: model.updatedAt,
    };
    });

    return paginate(mapped, query);
  },

  async getById(id: string): Promise<Model | undefined> {
    await delay();
    return modelsDb.find((model) => model.id === id);
  },

  async create(payload: ModelDraft): Promise<Model> {
    await delay();
    const now = new Date().toISOString();
    const model: Model = {
      ...payload,
      id: createId(),
      uuid: createId(),
      variants: [],
      createdAt: now,
      updatedAt: now,
    };
    modelsDb.unshift(model);
    return model;
  },

  async update(id: string, payload: Partial<ModelDraft>): Promise<Model | undefined> {
    await delay();
    const modelIndex = modelsDb.findIndex((model) => model.id === id);
    if (modelIndex === -1) {
      return undefined;
    }
    const original = modelsDb[modelIndex];
    const updated: Model = {
      ...original,
      ...payload,
      updatedAt: new Date().toISOString(),
    };
    modelsDb[modelIndex] = updated;
    return updated;
  },

  async remove(id: string): Promise<void> {
    await delay();
    modelsDb = modelsDb.filter((model) => model.id !== id);
  },

  async upsertVariant(modelId: string, variantPayload: ModelVariant): Promise<Model | undefined> {
    await delay();
    const model = modelsDb.find((item) => item.id === modelId);
    if (!model) {
      return undefined;
    }
    const variantIndex = model.variants.findIndex((variant) => variant.id === variantPayload.id);
    if (variantIndex === -1) {
      model.variants.push(variantPayload);
    } else {
      model.variants[variantIndex] = variantPayload;
    }
    model.updatedAt = new Date().toISOString();
    return model;
  },

  async deleteVariant(modelId: string, variantId: string): Promise<Model | undefined> {
    await delay();
    const model = modelsDb.find((item) => item.id === modelId);
    if (!model) {
      return undefined;
    }
    model.variants = model.variants.filter((variant) => variant.id !== variantId);
    model.updatedAt = new Date().toISOString();
    return model;
  },
};

export const mockMaterialClient = {
  async list(query: MaterialsListQuery = {}): Promise<MaterialsListResult> {
    await delay();
    const filtered = materialsDb.filter((material) => {
      const matchSearch = query.search
        ? `${material.code} ${material.name}`
            .toLowerCase()
            .includes(query.search.toLowerCase())
        : true;
      const matchGroup = query.group ? material.group === query.group : true;
      const matchSubgroup = query.subgroup
        ? material.subgroup?.toLowerCase().includes(query.subgroup.toLowerCase())
        : true;
      const matchActive = query.isActive === undefined
        ? true
        : query.isActive
          ? material.isActive
          : !material.isActive;
      const matchCritical = query.isCritical === undefined
        ? true
        : query.isCritical === material.isCritical;
      const matchPriceMin = query.priceMin ? (material.supply.price ?? 0) >= query.priceMin : true;
      const matchPriceMax = query.priceMax ? (material.supply.price ?? 0) <= query.priceMax : true;
      return (
        matchSearch &&
        matchGroup &&
        matchSubgroup &&
        matchActive &&
        matchCritical &&
        matchPriceMin &&
        matchPriceMax
      );
    });

    const mapped = filtered.map((item) => ({
      id: item.id,
      code: item.code,
      name: item.name,
      group: item.group,
      subgroup: item.subgroup,
      unit: item.specs.unitPrimary,
      price: item.supply.price,
      supplierName: item.supply.supplierName,
      leadTimeDays: item.supply.leadTimeDays,
      isActive: item.isActive,
      isCritical: item.isCritical,
      updatedAt: item.updatedAt,
    }));

    return paginate(mapped, query);
  },

  async getById(id: string): Promise<Material | undefined> {
    await delay();
    return materialsDb.find((item) => item.id === id);
  },

  async create(payload: MaterialDraft): Promise<Material> {
    await delay();
    const now = new Date().toISOString();
    const material: Material = {
      ...payload,
      id: createId(),
      uuid: createId(),
      createdAt: now,
      updatedAt: now,
    };
    materialsDb.unshift(material);
    return material;
  },

  async update(id: string, payload: Partial<MaterialDraft>): Promise<Material | undefined> {
    await delay();
    const index = materialsDb.findIndex((item) => item.id === id);
    if (index === -1) {
      return undefined;
    }
    const updated = {
      ...materialsDb[index],
      ...payload,
      updatedAt: new Date().toISOString(),
    } as Material;
    materialsDb[index] = updated;
    return updated;
  },

  async remove(id: string): Promise<void> {
    await delay();
    materialsDb = materialsDb.filter((item) => item.id !== id);
  },
};

export const mockWarehouseClient = {
  async list(query: WarehouseListQuery = {}): Promise<WarehouseListResult> {
    await delay();
    let items = [...warehouseDb];
    if (query.search) {
      const text = query.search.toLowerCase();
      items = items.filter((stock) =>
        `${stock.material.code} ${stock.material.name}`.toLowerCase().includes(text),
      );
    }
    if (query.warehouseCode) {
      items = items.filter((stock) => stock.warehouseCode === query.warehouseCode);
    }
    if (query.status) {
      items = items.filter((stock) => stock.status === query.status);
    }
    const paginated = paginate(items, query);
    return {
      ...paginated,
      items: paginated.items,
    };
  },

  async transactions(stockId?: string): Promise<WarehouseTransaction[]> {
    await delay();
    return stockId
      ? transactionsDb.filter((trx) => trx.stockId === stockId)
      : [...transactionsDb];
  },

  async receipt(draft: WarehouseReceiptDraft): Promise<void> {
    await delay();
    draft.lines.forEach((line, index) => {
      const materialInfo = mockMaterials.find((material) => material.id === line.materialId);
      const stock: WarehouseStockListItem = {
        id: `stock-${Date.now()}-${index}`,
        material: materialInfo
          ? {
              id: materialInfo.id,
              code: materialInfo.code,
              name: materialInfo.name,
              group: materialInfo.group,
              unit: materialInfo.specs.unitPrimary,
              color: materialInfo.color,
            }
          : {
              id: line.materialId,
              code: 'UNKNOWN',
              name: 'Неизвестный материал',
              group: 'OTHER',
              unit: line.unit,
              color: undefined,
            },
        batchNumber: line.batchNumber ?? `BATCH-${Date.now()}`,
        warehouseCode: line.warehouseCode,
        location: line.location,
        quantity: line.quantity,
        reservedQuantity: 0,
        unit: line.unit,
        purchasePrice: line.price,
        totalValue: line.price ? line.price * line.quantity : undefined,
        receiptDate: line.receiptDate,
        lastReceiptDate: line.receiptDate,
        lastIssueDate: undefined,
        updatedAt: new Date().toISOString(),
        availableQuantity: line.quantity,
        status: line.quantity < 100 ? 'LOW' : 'OK',
      };
      warehouseDb.unshift(stock);
    });
  },

  async issue(draft: WarehouseIssueDraft): Promise<void> {
    await delay();
    draft.lines.forEach((line) => {
      const stock = warehouseDb.find((item) => item.id === line.stockId);
      if (!stock) {
        return;
      }
      stock.quantity -= line.quantity;
      stock.availableQuantity = stock.quantity - stock.reservedQuantity;
      stock.status = stock.quantity < 100 ? 'LOW' : stock.quantity < 30 ? 'CRITICAL' : 'OK';
      stock.lastIssueDate = new Date().toISOString();
      stock.totalValue = stock.purchasePrice ? stock.purchasePrice * stock.quantity : stock.totalValue;
    });
  },

  async inventory(_draft: WarehouseInventoryDraft): Promise<void> {
    await delay();
    // Placeholder: no state mutation for mock inventory
  },
};

export const mockReferenceClient = {
  async list(query: ReferenceListQuery = {}): Promise<ReferenceItem[]> {
    await delay();
    const pools = [
      mockPerforationTypes,
      mockLiningTypes,
      mockCuttingParts,
    ];

    const merged = pools.flat();
    return merged.filter((item) => {
      const matchType = query.type ? item.type === query.type : true;
      const matchActive = query.isActive === undefined
        ? true
        : item.isActive === query.isActive;
      const matchSearch = query.search
        ? item.name.toLowerCase().includes(query.search.toLowerCase()) ||
          (item.code ?? '').toLowerCase().includes(query.search.toLowerCase())
        : true;
      return matchType && matchActive && matchSearch;
    });
  },
};

export const mockKpiService = {
  async models(): Promise<ModelsListResult> {
    await delay();
    return mockModelClient.list({ page: 1, pageSize: 5 });
  },

  async warehouse(): Promise<WarehouseListResult> {
    await delay();
    return mockWarehouseClient.list({ page: 1, pageSize: 5 });
  },
};

export const resetMockData = () => {
  modelsDb = deepClone(mockModels);
  materialsDb = deepClone(mockMaterials);
  warehouseDb = deepClone(mockWarehouseStocks);
  transactionsDb = deepClone(mockWarehouseTransactions);
};
