-- Создание справочных таблиц для параметров моделей

-- Таблица вариантов перфорации
CREATE TABLE IF NOT EXISTS perforation_types (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица типов подкладки/стельки
CREATE TABLE IF NOT EXISTS lining_types (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    material_type VARCHAR(100), -- кожа, текстиль, синтетика
    thickness NUMERIC(5,2), -- толщина в мм
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица типов затяжки
CREATE TABLE IF NOT EXISTS lasting_types (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    process_type VARCHAR(100), -- клеевая, прошивная, литьевая
    equipment_required TEXT,
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица связи модели с возможными перфорациями (многие ко многим)
CREATE TABLE IF NOT EXISTS model_perforations (
    id SERIAL PRIMARY KEY,
    model_id INTEGER REFERENCES models(id) ON DELETE CASCADE,
    perforation_id INTEGER REFERENCES perforation_types(id) ON DELETE CASCADE,
    is_default BOOLEAN DEFAULT false,
    notes TEXT,
    UNIQUE(model_id, perforation_id)
);

-- Таблица связи модели с возможными подкладками (многие ко многим)
CREATE TABLE IF NOT EXISTS model_linings (
    id SERIAL PRIMARY KEY,
    model_id INTEGER REFERENCES models(id) ON DELETE CASCADE,
    lining_id INTEGER REFERENCES lining_types(id) ON DELETE CASCADE,
    is_default BOOLEAN DEFAULT false,
    notes TEXT,
    UNIQUE(model_id, lining_id)
);

-- Добавляем поле для типа затяжки в таблицу models
ALTER TABLE models
ADD COLUMN IF NOT EXISTS lasting_type_id INTEGER REFERENCES lasting_types(id);

-- Добавляем поля для конкретного варианта в таблицу specifications
ALTER TABLE specifications
ADD COLUMN IF NOT EXISTS perforation_id INTEGER REFERENCES perforation_types(id),
ADD COLUMN IF NOT EXISTS lining_id INTEGER REFERENCES lining_types(id);

-- Вставляем начальные данные для перфорации
INSERT INTO perforation_types (code, name, description) VALUES
    ('NONE', 'Без перфорации', 'Модель без перфорации'),
    ('PARTIAL', 'Частичная перфорация', 'Перфорация на отдельных деталях'),
    ('FULL', 'Полная перфорация', 'Перфорация на всех деталях верха'),
    ('DECORATIVE', 'Декоративная перфорация', 'Перфорация в виде узора или логотипа')
ON CONFLICT (code) DO NOTHING;

-- Вставляем начальные данные для подкладки/стельки
INSERT INTO lining_types (code, name, material_type, thickness) VALUES
    ('LEATHER_FULL', 'Кожаная полная', 'Кожа', 1.5),
    ('LEATHER_HALF', 'Кожаная половинная', 'Кожа', 1.2),
    ('TEXTILE_FULL', 'Текстильная полная', 'Текстиль', 2.0),
    ('TEXTILE_HALF', 'Текстильная половинная', 'Текстиль', 1.5),
    ('SYNTHETIC', 'Синтетическая', 'Синтетика', 1.8),
    ('COMBINED', 'Комбинированная', 'Комбинированная', 1.5)
ON CONFLICT (code) DO NOTHING;

-- Вставляем начальные данные для типов затяжки
INSERT INTO lasting_types (code, name, process_type, equipment_required) VALUES
    ('CEMENTED', 'Клеевая затяжка', 'Клеевая', 'Затяжная машина, пресс для подошвы'),
    ('BLAKE', 'Прошивная Blake', 'Прошивная', 'Машина Blake для прошивки'),
    ('GOODYEAR', 'Прошивная Goodyear', 'Прошивная', 'Машина Goodyear, рантовая машина'),
    ('INJECTION', 'Литьевая', 'Литьевая', 'Литьевая машина, пресс-формы'),
    ('VULCANIZED', 'Вулканизированная', 'Вулканизация', 'Вулканизационный пресс'),
    ('CALIFORNIA', 'Калифорнийская', 'Комбинированная', 'Специальное оборудование для California')
ON CONFLICT (code) DO NOTHING;

-- Создаем индексы для быстрого поиска
CREATE INDEX IF NOT EXISTS idx_model_perforations_model ON model_perforations(model_id);
CREATE INDEX IF NOT EXISTS idx_model_linings_model ON model_linings(model_id);
CREATE INDEX IF NOT EXISTS idx_models_lasting_type ON models(lasting_type_id);
CREATE INDEX IF NOT EXISTS idx_specifications_perforation ON specifications(perforation_id);
CREATE INDEX IF NOT EXISTS idx_specifications_lining ON specifications(lining_id);