# Анализ проблем интеграции фронтенда с бэкендом

## Анализ проблемы с созданием модели через API

### Что произошло при попытке создания модели:

1. **Команда curl была прервана** - видно в логах, что запрос на создание модели начался:
   ```
   2025-09-24 20:37:18,219 | INFO | API Request: {"method": "POST", "path": "http://localhost:8001/api/v1/models/", "params": {}, "body": "{\"name\": \"Test Model\", \"article\": \"TEST001\"}", "timestamp": "2025-09-24T20:37:18.219303"}
   ```

2. **Сервер перезагрузился во время обработки запроса** - сразу после этого появилось:
   ```
   WARNING: WatchFiles detected changes in 'backend/app/models/model.py'. Reloading...
   INFO: Shutting down
   INFO: Waiting for connections to close. (CTRL+C to force quit)
   ```

### Почему это произошло:

1. **Автоматическая перезагрузка uvicorn** - сервер запущен с флагом `--reload`, который отслеживает изменения файлов
2. **Изменения в модели** - в логах видно, что был изменен файл `backend/app/models/model.py`
3. **Прерывание запроса** - когда uvicorn перезагружается, он завершает все активные соединения, включая наш curl запрос

### Дополнительные проблемы в логах:

1. **SQLAlchemy ошибка** - в более ранних логах видна ошибка:
   ```
   sqlalchemy.exc.InvalidRequestError: Could not determine join condition between parent/child tables on relationship Model.sole_options - there are multiple foreign key paths linking the tables
   ```

2. **Проблемы с материалами** - множественные 307 редиректы:
   ```
   INFO: 127.0.0.1:59796 - "GET /api/v1/materials?page=1&pageSize=10 HTTP/1.1" 307 Temporary Redirect
   ```

3. **Ошибки импорта** - множественные ошибки:
   ```
   ModuleNotFoundError: No module named 'pydantic_settings'
   ImportError: cannot import name 'MaterialListResult' from 'app.schemas.material'
   ```

### Рекомендации:

1. **Исправить SQLAlchemy отношения** в модели `Model.sole_options`
2. **Проверить роутинг материалов** - 307 редиректы указывают на проблемы с URL
3. **Установить недостающие зависимости** - `pydantic-settings`
4. **Исправить импорты схем** - `MaterialListResult` vs `MaterialsListResult`
5. **Запустить создание модели заново** после исправления ошибок

### Статус системы:

- ✅ **PostgreSQL**: Работает, подключение установлено
- ✅ **Health endpoint**: Отвечает корректно
- ✅ **GET /api/v1/models/**: Работает, возвращает пустой список
- ❌ **POST /api/v1/models/**: Прерывается из-за перезагрузки сервера
- ❌ **GET /api/v1/materials/**: 307 редиректы
- ❌ **SQLAlchemy модели**: Ошибки в отношениях

## Выполненные шаги

### 1. Подготовка окружения
```bash
cd /Users/four/Documents/krai/kr2/forDesktop/krai_desktop
source venv/bin/activate
```

### 2. Настройка базы данных
```bash
# Создание БД и пользователя
psql postgres -c "CREATE DATABASE krai_mrp_v06;"
psql postgres -c "CREATE USER krai_user WITH PASSWORD 'change-me';"
psql postgres -c "GRANT ALL PRIVILEGES ON DATABASE krai_mrp_v06 TO krai_user;"

# Создание .env файла
echo "DATABASE_URL=postgresql://krai_user:change-me@localhost:5432/krai_mrp_v06" > backend/.env
```

### 3. Установка зависимостей
```bash
pip install -r backend/requirements.txt
pip install -e .  # Установка пакета в режиме разработки
```

### 4. Инициализация базы данных
```bash
python -m backend.app.db.init_db
# Результат: ✅ Database initialisation completed
```

### 5. Исправление ошибок импорта
**Проблема**: Неправильные имена классов в схемах
- `MaterialListResult` → `MaterialsListResult`
- Исправлено в файлах:
  - `backend/app/schemas/__init__.py`
  - `backend/app/services/material_service.py`

### 6. Исправление ошибок FastAPI
**Проблема**: Статус код 204 не должен иметь тело ответа
```python
# Было:
def delete_model(model_id: UUID, service: ModelService = Depends(get_service)) -> None:

# Стало:
def delete_model(model_id: UUID, service: ModelService = Depends(get_service)):
```
Исправлено в файлах:
- `backend/app/api/api_v1/endpoints/models.py`
- `backend/app/api/api_v1/endpoints/materials.py`
- `backend/app/api/api_v1/endpoints/references.py`

### 7. Запуск серверов
```bash
# Бэкенд
uvicorn backend.app.main:app --host 0.0.0.0 --port 8001 --reload

# Фронтенд
cd frontend && npm run dev -- --host 0.0.0.0 --port 5174
```

## Текущие проблемы

### 1. Ошибка SQLAlchemy relationships
```
sqlalchemy.exc.InvalidRequestError: One or more mappers failed to initialize - can't proceed with initialization of other mappers. Triggering mapper: 'Mapper[Model(models)]'. Original exception was: Could not determine join condition between parent/child tables on relationship Model.sole_options - there are multiple foreign key paths linking the tables. Specify the 'foreign_keys' argument, providing a list of those columns which should be counted as containing a foreign key reference to the parent table.
```

**Причина**: В модели `Model` есть relationship `sole_options`, но SQLAlchemy не может определить, какой foreign key использовать, так как есть несколько путей связи между таблицами.

### 2. API endpoints возвращают Internal Server Error
```bash
curl http://localhost:8001/api/v1/models/
# Результат: Internal Server Error
```

**Причина**: Ошибка SQLAlchemy при инициализации моделей не позволяет API endpoints работать корректно.

### 3. Проблемы с правами доступа к БД
```bash
psql postgresql://krai_user:change-me@localhost:5432/krai_mrp_v06 -c "SELECT COUNT(*) FROM models;"
# Результат: ERROR: permission denied for table models
```

**Решение**: Выданы права пользователю `krai_user`:
```bash
psql postgresql://four@localhost:5432/krai_mrp_v06 -c "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO krai_user;"
psql postgresql://four@localhost:5432/krai_mrp_v06 -c "GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO krai_user;"
```

## Текущий статус

### ✅ Работает:
- База данных создана и инициализирована
- Бэкенд сервер запускается (health check отвечает)
- Фронтенд сервер запускается
- OpenAPI документация доступна по `/docs`
- Swagger UI работает

### ❌ Не работает:
- API endpoints возвращают 500 Internal Server Error
- Проблема с SQLAlchemy relationships в модели `Model`
- Создание моделей через API не работает

## Следующие шаги для решения

1. **Исправить SQLAlchemy relationships** в модели `Model`:
   - Указать явно `foreign_keys` для relationship `sole_options`
   - Проверить все relationships в моделях на корректность

2. **Проверить структуру таблиц** в БД:
   - Убедиться, что foreign keys созданы правильно
   - Проверить соответствие моделей SQLAlchemy и реальной структуры БД

3. **Протестировать API endpoints** после исправления relationships

## Команды для диагностики

```bash
# Проверка структуры таблиц
psql postgresql://krai_user:change-me@localhost:5432/krai_mrp_v06 -c "\dt"

# Проверка health check
curl http://localhost:8001/health

# Проверка OpenAPI схемы
curl http://localhost:8001/openapi.json

# Проверка фронтенда
curl -I http://localhost:5174
```

## Детальная ошибка SQLAlchemy

```
sqlalchemy.exc.InvalidRequestError: One or more mappers failed to initialize - can't proceed with initialization of other mappers. Triggering mapper: 'Mapper[Model(models)]'. Original exception was: Could not determine join condition between parent/child tables on relationship Model.sole_options - there are multiple foreign key paths linking the tables. Specify the 'foreign_keys' argument, providing a list of those columns which should be counted as containing a foreign key reference to the parent table.
```

**Анализ**: Эта ошибка указывает на то, что в модели `Model` есть relationship `sole_options`, но SQLAlchemy не может автоматически определить, какой foreign key использовать для связи между таблицами `models` и `model_sole_options` (или аналогичной таблицей).

**Возможные причины**:
1. В таблице `model_sole_options` есть несколько колонок, которые могут быть foreign keys к таблице `models`
2. Не указан явно `foreign_keys` в определении relationship
3. Неправильная структура таблиц в БД

**Решение**: Нужно найти файл с моделью `Model` и исправить relationship `sole_options`, указав явно `foreign_keys`.

## Структура таблиц в БД

```sql
-- Список таблиц в БД krai_mrp_v06
cutting_parts
materials
model_cutting_parts
model_hardware_item_materials
model_hardware_items
model_hardware_sets
model_insole_options
model_perforations
model_sole_options
model_variant_cutting_parts
model_variants
models
reference_items
warehouse_stock
warehouse_transactions
```

## Заключение

Основная проблема - это ошибка в SQLAlchemy relationships, которая блокирует работу всех API endpoints. После исправления этой проблемы система должна заработать корректно.

**Приоритет исправления**: Высокий - без исправления relationships API полностью неработоспособен.
