# KRAI Production System v0.6

🏭 **Система управления производством обуви**

Версия 0.6 представляет собой полную архитектурную переработку с переходом на современный веб-стек.

## 🎯 Что нового в v0.6

### ✨ Архитектурные изменения
- **🔄 Разделение backend/frontend** - FastAPI + React
- **📊 Нормализованная БД** - отказ от JSONB, 20 нормализованных таблиц
- **🚀 Современный стек** - TypeScript, Ant Design, React Query
- **🔐 Безопасность** - JWT аутентификация, 2FA через Telegram

### 🏗️ Техническая архитектура

```
krai-system/
├── backend/              # FastAPI приложение
│   ├── app/
│   │   ├── api/         # REST API endpoints
│   │   ├── models/      # SQLAlchemy модели (нормализованные)
│   │   ├── schemas/     # Pydantic схемы
│   │   ├── services/    # Бизнес-логика
│   │   └── core/        # Конфигурация, auth
│   └── alembic/         # Миграции БД
├── frontend/            # React приложение
│   ├── src/
│   │   ├── components/  # React компоненты
│   │   ├── pages/       # Страницы приложения
│   │   ├── services/    # API клиенты
│   │   └── types/       # TypeScript типы
└── shared/              # Общие типы/константы
```

## 🗄️ Нормализованная база данных

### Основные таблицы

1. **models** - модели обуви
2. **model_photos** - фотографии моделей
3. **model_properties** - дополнительные свойства моделей
4. **specifications** - спецификации моделей
5. **specification_cutting_parts** - детали кроя в спецификациях
6. **specification_hardware** - фурнитура в спецификациях
7. **specification_variant_options** - варианты исполнения
8. **materials** - материалы
9. **material_properties** - свойства материалов
10. **cutting_parts** - справочник деталей кроя
11. **cutting_part_properties** - свойства деталей кроя
12. **warehouse_stock** - складские остатки
13. **stock_transactions** - транзакции по складу
14. **production_orders** - производственные заказы
15. **order_sizes** - размеры в заказах
16. **order_material_requirements** - потребности в материалах
17. **production_schedule** - график производства
18. **purchase_plan** - планы закупок
19. **size_runs** - размерные ряды (из Excel таблицы)
20. **Справочники**: perforation_types, lining_types, lasting_types, sole_options

### Преимущества нормализации

✅ **Производительность** - быстрые запросы, индексы
✅ **Целостность данных** - внешние ключи, ограничения
✅ **Масштабируемость** - легко добавлять новые поля
✅ **Простота работы** - понятная структура для разработчиков

## 🚀 Быстрый старт

### Backend (FastAPI)

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend (React)

```bash
cd frontend
npm install
npm run dev
```

### База данных

```bash
# Создание миграции
cd backend
alembic revision --autogenerate -m "Initial migration"

# Применение миграций
alembic upgrade head
```

## 📋 Функциональность

### ✅ Реализовано

- 🏗️ Архитектура backend/frontend
- 📊 Нормализованная схема БД
- 🎨 Современный UI на React + Ant Design
- 📱 Адаптивный дизайн
- 🔍 Поиск и фильтрация

### 🔄 В разработке

- 👤 Система аутентификации
- 📊 API endpoints для всех сущностей
- 🏭 Производственное планирование
- 📦 Складской учёт с транзакциями
- 📈 Аналитика и отчёты

### 🎯 Запланировано

- 🔐 2FA через Telegram Bot
- ⚡ Redis кеширование
- 📱 PWA поддержка
- 🌍 Интернационализация

## 🎨 UI/UX

### Компоненты

- **Дашборд** - обзор системы, KPI
- **Модели** - каталог моделей обуви
- **Материалы** - справочник материалов
- **Склад** - управление остатками
- **Производство** - планирование и заказы
- **Справочники** - вспомогательные данные

### Дизайн-система

- 🎨 **Ant Design** - готовые компоненты
- 📱 **Responsive** - адаптивная вёрстка
- ⚡ **Fast** - React Query кеширование
- 🎯 **Intuitive** - понятный интерфейс

## 💾 Миграция данных

Данные из старой PyQt6 версии будут мигрированы через специальные скрипты:

1. **Модели** - из models таблицы (properties JSON → model_properties)
2. **Спецификации** - из specifications (JSONB → нормализованные таблицы)
3. **Материалы** - из materials (properties JSON → material_properties)
4. **Размерные ряды** - импорт из Excel таблицы

## 📞 Поддержка

- 📧 Email: support@krai.ru
- 📱 Telegram: @krai_support
- 📝 Issues: GitHub Issues

---

**🎉 KRAI v0.6 - Современная система управления производством обуви**