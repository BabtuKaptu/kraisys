import React, { useMemo, useState } from 'react';
import { Select, SelectProps } from 'antd';
import { useQuery } from '@tanstack/react-query';
import { ReferenceItem, ReferenceListQuery } from '../../types';
import { referenceApi } from '../../services/referenceApi';
import { useDebounce } from '../../hooks/useDebounce';

interface ReferenceSelectorProps extends Omit<SelectProps, 'options' | 'loading'> {
  value?: string;
  onChange?: (value: string | undefined) => void;
  referenceType: string; // 'cutting_part', 'sole_type', etc.
  filters?: Partial<ReferenceListQuery>;
  showCode?: boolean;
}

interface ReferenceOption {
  label: string;
  value: string;
  reference: ReferenceItem;
}

export const ReferenceSelector: React.FC<ReferenceSelectorProps> = ({
  value,
  onChange,
  referenceType,
  filters = {},
  showCode = false,
  placeholder = 'Выберите элемент',
  showSearch = true,
  allowClear = true,
  style,
  ...selectProps
}) => {
  const [searchText, setSearchText] = useState('');
  const debouncedSearch = useDebounce(searchText, 300);

  // Запрос справочных данных
  const { data: referencesData, isLoading } = useQuery({
    queryKey: ['references', 'selector', {
      type: referenceType,
      ...filters,
      search: debouncedSearch || undefined,
      pageSize: 100,
    }],
    queryFn: () => referenceApi.list({
      type: referenceType,
      pageSize: 100,
      search: debouncedSearch || undefined,
      ...filters,
    }),
    staleTime: 10 * 60 * 1000, // 10 минут кэш для справочников
  });

  // Форматирование опций
  const referenceOptions: ReferenceOption[] = useMemo(() => {
    if (!referencesData) return [];
    
    return referencesData.map((reference) => ({
      label: showCode && reference.code 
        ? `${reference.code} · ${reference.name}`
        : reference.name,
      value: reference.id,
      reference,
    }));
  }, [referencesData, showCode]);

  const handleSearch = (searchValue: string) => {
    setSearchText(searchValue);
  };

  const handleChange = (selectedValue: string | undefined) => {
    onChange?.(selectedValue);
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
      options={referenceOptions}
      style={style}
      filterOption={false} // Используем server-side поиск
      notFoundContent={isLoading ? 'Загрузка...' : 'Элементы не найдены'}
    />
  );
};

export default ReferenceSelector;
