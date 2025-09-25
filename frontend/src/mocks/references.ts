import { ReferenceItem } from '../types';

export const mockPerforationTypes: ReferenceItem<'perforation_type'>[] = [
  {
    id: 'perforation-none',
    code: 'PERF-000',
    name: 'Без перфорации',
    description: 'Глухой верх без перфорации',
    type: 'perforation_type',
    isActive: true,
  },
  {
    id: 'perforation-quarter',
    code: 'PERF-010',
    name: 'Перфорация по союзке',
    description: 'Перфорация вдоль линии союзки',
    type: 'perforation_type',
    isActive: true,
  },
  {
    id: 'perforation-full',
    code: 'PERF-020',
    name: 'Полная перфорация',
    description: 'Полный рисунок перфорации по верху',
    type: 'perforation_type',
    isActive: false,
  },
];

export const mockLiningTypes: ReferenceItem<'lining_type'>[] = [
  {
    id: 'lining-calf',
    code: 'LIN-001',
    name: 'Кожподклад (полный)',
    description: 'Натуральная кожа по всей поверхности',
    type: 'lining_type',
    isActive: true,
  },
  {
    id: 'lining-fleece',
    code: 'LIN-010',
    name: 'Байка',
    description: 'Утеплитель средней плотности',
    type: 'lining_type',
    isActive: true,
  },
  {
    id: 'lining-mesh',
    code: 'LIN-020',
    name: 'Дышащая сетка',
    description: 'Сетка для летних моделей',
    type: 'lining_type',
    isActive: true,
  },
];

export const mockCuttingParts: ReferenceItem<'cutting_part'>[] = [
  {
    id: 'cutting-quarter',
    code: 'CUT-001',
    name: 'Союзка',
    description: 'Основная деталь верха',
    type: 'cutting_part',
    isActive: true,
    attributes: {
      defaultQty: 2,
      unit: 'шт',
    },
  },
  {
    id: 'cutting-vamp',
    code: 'CUT-002',
    name: 'Берец',
    description: 'Боковые части верха',
    type: 'cutting_part',
    isActive: true,
    attributes: {
      defaultQty: 2,
      unit: 'шт',
    },
  },
  {
    id: 'cutting-tongue',
    code: 'CUT-010',
    name: 'Язычок',
    description: 'Центральная часть под шнуровку',
    type: 'cutting_part',
    isActive: true,
    attributes: {
      defaultQty: 1,
      unit: 'шт',
    },
  },
];

export const mockLastingTypes: ReferenceItem<'lasting_type'>[] = [
  {
    id: 'lasting-cemented',
    code: 'LAST-001',
    name: 'Клеевая затяжка',
    description: 'Стандартная клеевая технология',
    type: 'lasting_type',
    isActive: true,
  },
  {
    id: 'lasting-hand',
    code: 'LAST-002',
    name: 'Ручная затяжка',
    description: 'Ручной способ затяжки для лимитированных моделей',
    type: 'lasting_type',
    isActive: true,
  },
];

export const mockReferenceMap = {
  perforation: mockPerforationTypes,
  lining: mockLiningTypes,
  cutting: mockCuttingParts,
  lasting: mockLastingTypes,
};
