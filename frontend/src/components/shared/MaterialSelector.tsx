import React, { useMemo, useState, useEffect } from 'react';
import { Select, SelectProps } from 'antd';
import { useQuery } from '@tanstack/react-query';
import { MaterialsListQuery, MaterialsListItem } from '../../types';
import { materialsApi } from '../../services/materialsApi';
import { useDebounce } from '../../hooks/useDebounce';

interface MaterialSelectorProps extends Omit<SelectProps, 'options' | 'loading'> {
  value?: string;
  onChange?: (value: string | undefined) => void;
  onMaterialSelect?: (material: MaterialsListItem | undefined) => void;
  filters?: Partial<MaterialsListQuery>;
  groupBy?: 'group' | 'none';
  showDetails?: boolean;
}

interface MaterialOption {
  label: string;
  value: string;
  material: MaterialsListItem;
}

interface GroupedOption {
  label: string;
  options: MaterialOption[];
}

const MATERIAL_GROUPS_LABELS = {
  LEATHER: 'Кожа',
  SOLE: 'Подошва', 
  HARDWARE: 'Фурнитура',
  LINING: 'Подкладка',
  CHEMICAL: 'Химия',
  PACKAGING: 'Упаковка',
  TEXTILE: 'Текстиль',
  OTHER: 'Прочее',
};

export const MaterialSelector: React.FC<MaterialSelectorProps> = ({
  value,
  onChange,
  onMaterialSelect,
  filters = {},
  groupBy = 'group',
  showDetails = true,
  placeholder = 'Выберите материал',
  showSearch = true,
  allowClear = true,
  style,
  ...selectProps
}) => {
  const [searchText, setSearchText] = useState('');
  const debouncedSearch = useDebounce(searchText, 300);

  // Запрос материалов с server-side поиском
  const { data: materialsData, isLoading } = useQuery({
    queryKey: ['materials', 'selector', {
      ...filters,
      search: debouncedSearch || undefined,
      pageSize: 100,
    }],
    queryFn: () => materialsApi.list({
      page: 1,
      pageSize: 100,
      search: debouncedSearch || undefined,
      ...filters,
    }),
    staleTime: 5 * 60 * 1000, // 5 минут кэш
  });

  // Форматирование опций
  const materialOptions: MaterialOption[] = useMemo(() => {
    if (!materialsData?.items) return [];
    
    return materialsData.items.map((material) => ({
      label: showDetails 
        ? `${material.code} · ${material.name} ${material.group ? `(${MATERIAL_GROUPS_LABELS[material.group] || material.group})` : ''}`
        : `${material.code} · ${material.name}`,
      value: material.id,
      material,
    }));
  }, [materialsData?.items, showDetails]);

  // Группировка опций
  const finalOptions = useMemo(() => {
    if (groupBy === 'none') {
      return materialOptions;
    }

    // Группировка по типу материала
    const grouped = materialOptions.reduce<Record<string, MaterialOption[]>>((acc, option) => {
      const group = option.material.group || 'OTHER';
      const groupLabel = MATERIAL_GROUPS_LABELS[group] || group;
      
      if (!acc[groupLabel]) {
        acc[groupLabel] = [];
      }
      acc[groupLabel].push(option);
      return acc;
    }, {});

    // Преобразование в формат Ant Design
    return Object.entries(grouped).map<GroupedOption>(([groupLabel, options]) => ({
      label: groupLabel,
      options: options.sort((a, b) => a.label.localeCompare(b.label)),
    }));
  }, [materialOptions, groupBy]);

  const handleSearch = (searchValue: string) => {
    setSearchText(searchValue);
  };

  const handleChange = (selectedValue: string | undefined) => {
    onChange?.(selectedValue);
    
    // Найти выбранный материал и передать его данные через callback
    if (selectedValue && materialsData?.items) {
      const selectedMaterial = materialsData.items.find(item => item.id === selectedValue);
      onMaterialSelect?.(selectedMaterial);
    } else {
      onMaterialSelect?.(undefined);
    }
  };

  return (
    <Select
      {...selectProps}
      value={value}
      onChange={handleChange}
      onSearch={showSearch ? handleSearch : undefined}
      placeholder={placeholder}
      showSearch={showSearch}
      allowClear={allowClear}
      loading={isLoading}
      options={finalOptions}
      style={style}
      filterOption={false} // Используем server-side поиск
      notFoundContent={isLoading ? 'Загрузка...' : 'Материалы не найдены'}
    />
  );
};

export default MaterialSelector;
