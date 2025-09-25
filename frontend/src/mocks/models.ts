import {
  CuttingPartUsage,
  HardwareItemOption,
  HardwareSet,
  InsoleOption,
  Model,
  ModelSuperBOM,
  ModelVariant,
  PerforationOption,
  SoleOption,
} from '../types';
import { mockMaterials } from './materials';
import { mockCuttingParts, mockPerforationTypes } from './references';

const isoNow = new Date('2024-09-20T11:00:00Z').toISOString();

const materialLookup = new Map(
  mockMaterials.map((material) => [material.id, material]),
);

const asReference = (materialId: string) => {
  const material = materialLookup.get(materialId);
  if (!material) {
    throw new Error(`Unknown material id: ${materialId}`);
  }
  return {
    id: material.id,
    code: material.code,
    name: material.name,
    group: material.group,
    unit: material.specs.unitPrimary,
    color: material.color,
  };
};

const superBom: ModelSuperBOM = {
  perforationOptions: mockPerforationTypes.map<PerforationOption>((option, index) => ({
    id: option.id,
    name: option.name,
    code: option.code,
    description: option.description,
    isDefault: index === 0,
    isActive: option.isActive,
  })),
  insoleOptions: [
    {
      id: 'insole-basic',
      name: 'Стелька EVA стандарт',
      material: 'EVA',
      seasonality: 'ALL_SEASON',
      thicknessMm: 4,
      isDefault: true,
      isActive: true,
    },
    {
      id: 'insole-fleece',
      name: 'Стелька утеплённая',
      material: 'Войлок',
      seasonality: 'FALL_WINTER',
      thicknessMm: 6,
      isActive: true,
    },
  ] satisfies InsoleOption[],
  hardwareSets: [
    {
      id: 'hardware-hooks-laces',
      name: 'Крючки + шнурки',
      description: 'Стандартный комплект для высоких моделей',
      items: [
        {
          id: 'hardware-hooks',
          name: 'Крючки металлические',
          materialGroup: 'HARDWARE',
          compatibleMaterials: [asReference('mat-hooks-black')],
          requiresExactSelection: false,
        },
        {
          id: 'hardware-laces',
          name: 'Шнурки круглые 150 см',
          materialGroup: 'HARDWARE',
          compatibleMaterials: [
            {
              id: 'mat-laces-waxed',
              code: 'LACE150',
              name: 'Шнурки плоские вощеные 150см',
              group: 'HARDWARE',
              unit: 'пар',
              color: 'Чёрный',
            },
          ],
          requiresExactSelection: true,
        },
      ] satisfies HardwareItemOption[],
      isDefault: true,
      isActive: true,
    },
  ] satisfies HardwareSet[],
};

const cuttingParts: CuttingPartUsage[] = [
  {
    id: 'cutting-1',
    part: mockCuttingParts[0],
    material: asReference('mat-leather-black'),
    quantity: 2,
    consumptionPerPair: 15.5,
    laborCost: 120,
  },
  {
    id: 'cutting-2',
    part: mockCuttingParts[1],
    material: asReference('mat-leather-black'),
    quantity: 2,
    consumptionPerPair: 12.3,
    laborCost: 95,
  },
  {
    id: 'cutting-3',
    part: mockCuttingParts[2],
    material: asReference('mat-leather-black'),
    quantity: 1,
    consumptionPerPair: 4.8,
    laborCost: 45,
  },
];

const soleOptions: SoleOption[] = [
  {
    id: 'sole-888',
    name: 'Подошва 888',
    material: asReference('mat-sole-888'),
    sizeMin: 39,
    sizeMax: 46,
    isDefault: true,
    notes: 'Основной вариант для городской эксплуатации',
  },
  {
    id: 'sole-michelin',
    name: 'Подошва Michelin Trek',
    material: {
      id: 'mat-sole-michelin',
      code: 'SOLE-MIC',
      name: 'Подошва Michelin outdoor',
      group: 'SOLE',
      unit: 'пар',
      color: 'Чёрный',
    },
    sizeMin: 38,
    sizeMax: 47,
    notes: 'Повышенное сцепление, для outdoor-моделей',
  },
];

const baseModelId = 'model-sport-250';

const variants: ModelVariant[] = [
  {
    id: 'variant-sport-250-classic',
    modelId: baseModelId,
    name: 'SPORT 250 Classic',
    code: 'VAR-SPT-CL',
    isDefault: true,
    status: 'ACTIVE',
    specification: {
      perforationOptionId: 'perforation-none',
      insoleOptionId: 'insole-basic',
      hardwareSetId: 'hardware-hooks-laces',
      soleOptionId: 'sole-888',
    },
    totalMaterialCost: 2450,
    createdAt: isoNow,
    updatedAt: isoNow,
  },
  {
    id: 'variant-sport-250-winter',
    modelId: baseModelId,
    name: 'SPORT 250 Winter Edition',
    code: 'VAR-SPT-WIN',
    status: 'ACTIVE',
    specification: {
      perforationOptionId: 'perforation-quarter',
      insoleOptionId: 'insole-fleece',
      hardwareSetId: 'hardware-hooks-laces',
      soleOptionId: 'sole-michelin',
      notes: 'Использовать утеплённую подкладку',
    },
    totalMaterialCost: 2890,
    createdAt: isoNow,
    updatedAt: isoNow,
  },
];

export const mockModels: Model[] = [
  {
    id: baseModelId,
    uuid: 'model-uuid-1',
    name: 'SPORT 250',
    article: '250',
    gender: 'MALE',
    modelType: 'SPORT',
    category: 'SNEAKERS',
    collection: 'Осень-Зима 2024',
    season: 'FALL_WINTER',
    lastCode: '75',
    lastType: 'Ботиночная',
    sizeMin: 40,
    sizeMax: 46,
    lacingType: 'LASTING',
    defaultSoleOptionId: 'sole-888',
    isActive: true,
    retailPrice: 7200,
    wholesalePrice: 5100,
    materialCost: 2800,
    laborCost: 950,
    overheadCost: 450,
    description: 'Городские хайкеры с защитой от влаги',
    superBom,
    cuttingParts,
    soleOptions,
    notes: 'Основная модель для розничных сетей',
    attachments: [],
    variants,
    createdAt: isoNow,
    updatedAt: isoNow,
    kpis: [
      {
        title: 'В заказах',
        value: 23,
        trend: 'up',
        helperText: '+5 за неделю',
      },
      {
        title: 'Маржинальность',
        value: '37%',
        trend: 'neutral',
      },
    ],
  },
];
