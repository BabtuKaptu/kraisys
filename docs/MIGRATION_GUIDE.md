# Migration Guide: v0.5 → v0.6

🔄 **Руководство по миграции с PyQt6 на Web-архитектуру**

## 📋 Обзор изменений

### Что меняется

| Компонент | v0.5 (PyQt6) | v0.6 (Web) |
|-----------|--------------|------------|
| **Frontend** | PyQt6 Desktop | React + TypeScript |
| **Backend** | SQLModel встроенный | FastAPI отдельный |
| **Database** | JSONB поля | Нормализованные таблицы |
| **Auth** | Отсутствует | JWT + 2FA |
| **API** | Нет | REST API |

## 🗄️ Схема миграции БД

### Основные изменения

#### 1. Модели обуви
```sql
-- Старая структура
models {
  properties: JSONB  -- {"color": "black", "season": "winter"}
  photos: JSONB      -- ["photo1.jpg", "photo2.jpg"]
}

-- Новая структура
models + model_properties + model_photos
```

#### 2. Спецификации
```sql
-- Старая структура
specifications {
  cutting_parts: JSONB  -- [{"cutting_part_id": 123, "quantity": 2}]
  hardware: JSONB       -- [{"material_id": 456, "quantity": 1}]
  variants: JSONB       -- {"perforation": ["без перфорации"]}
}

-- Новая структура
specifications + specification_cutting_parts +
specification_hardware + specification_variant_options
```

#### 3. Справочники
```sql
-- Старая структура
cutting_parts {
  properties: JSONB  -- {"category": "SOYUZKA"}
}

-- Новая структура
cutting_parts + cutting_part_properties +
perforation_types + lining_types + lasting_types + sole_options
```

## 🚀 Пошаговая миграция

### Этап 1: Подготовка

1. **Создать бэкап БД**
```bash
pg_dump krai_system > backup_v05.sql
```

2. **Клонировать ветку v0.6**
```bash
git checkout version-0.6-architecture-refactor
```

3. **Установить зависимости**
```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd ../frontend
npm install
```

### Этап 2: Миграция БД

1. **Создать новую схему**
```bash
cd backend
alembic revision --autogenerate -m "Create normalized schema v0.6"
alembic upgrade head
```

2. **Запустить миграционные скрипты**
```bash
python migrate_data_v05_to_v06.py
```

### Этап 3: Проверка данных

1. **Проверить целостность**
```sql
-- Проверить количество записей
SELECT 'models' as table_name, count(*) from models
UNION ALL
SELECT 'specifications', count(*) from specifications
UNION ALL
SELECT 'materials', count(*) from materials;
```

2. **Валидировать связи**
```sql
-- Проверить foreign keys
SELECT * FROM model_properties WHERE model_id NOT IN (SELECT id FROM models);
```

## 📊 Скрипт миграции данных

Создать файл `backend/migrate_data_v05_to_v06.py`:

```python
"""
Data migration script from v0.5 to v0.6
Converts JSONB fields to normalized tables
"""

from sqlalchemy import create_engine, text
from app.core.config import settings

def migrate_model_properties():
    """Migrate model properties from JSONB to normalized table"""
    engine = create_engine(settings.DATABASE_URL)

    with engine.connect() as conn:
        # Get models with properties
        result = conn.execute(text("""
            SELECT id, properties
            FROM models_old
            WHERE properties IS NOT NULL AND properties != '{}'
        """))

        for row in result:
            model_id = row.id
            properties = row.properties

            # Insert each property
            for key, value in properties.items():
                conn.execute(text("""
                    INSERT INTO model_properties
                    (model_id, property_name, property_value, property_type)
                    VALUES (:model_id, :name, :value, 'string')
                """), {
                    'model_id': model_id,
                    'name': key,
                    'value': str(value)
                })

        conn.commit()

# Аналогично для других таблиц...
```

## ⚠️ Важные моменты

### 1. Сохранение функциональности

Убедитесь что сохранена вся функциональность:

- ✅ Создание/редактирование моделей
- ✅ Управление спецификациями
- ✅ Варианты исполнения
- ✅ Справочники
- ✅ Расчёт себестоимости

### 2. Производительность

Новая нормализованная схема должна работать быстрее:

- 📈 Индексы на foreign keys
- 🔍 Быстрый поиск по свойствам
- 📊 Эффективная аналитика

### 3. Обратная совместимость

При необходимости можно вернуться к v0.5:

```bash
git checkout version-0.5-ready-for-production
```

## 🧪 Тестирование миграции

### 1. Автоматические тесты
```bash
cd backend
pytest tests/test_migration.py -v
```

### 2. Ручная проверка
- [ ] Все модели загружаются
- [ ] Спецификации корректны
- [ ] Варианты отображаются
- [ ] Поиск работает
- [ ] Производственное планирование

## 📞 Поддержка

Если возникли проблемы при миграции:

1. 📧 Создать Issue в GitHub
2. 💬 Написать в Telegram
3. 📋 Приложить логи ошибок

---

**🎯 Цель: Безопасная миграция без потери данных и функциональности**