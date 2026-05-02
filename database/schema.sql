-- =====================================================
-- DinoReserve ERP — Esquema y datos de demostración
-- =====================================================

PRAGMA foreign_keys = ON;

-- ---------- USERS ----------
CREATE TABLE IF NOT EXISTS users (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    username        TEXT NOT NULL UNIQUE,
    password_hash   TEXT NOT NULL,
    role            TEXT NOT NULL DEFAULT 'admin',
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

-- ---------- ENCLOSURES ----------
CREATE TABLE IF NOT EXISTS enclosures (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    name              TEXT NOT NULL UNIQUE,
    zone_type         TEXT NOT NULL,
    max_capacity      INTEGER NOT NULL CHECK (max_capacity > 0),
    current_capacity  INTEGER NOT NULL DEFAULT 0 CHECK (current_capacity >= 0),
    fence_voltage     REAL NOT NULL DEFAULT 0,
    security_level    INTEGER NOT NULL CHECK (security_level BETWEEN 1 AND 5),
    status            TEXT NOT NULL DEFAULT 'active',
    created_at        TEXT NOT NULL DEFAULT (datetime('now'))
);

-- ---------- DINOSAURS ----------
CREATE TABLE IF NOT EXISTS dinosaurs (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT NOT NULL,
    species         TEXT NOT NULL,
    diet_type       TEXT NOT NULL CHECK (diet_type IN ('carnivore','herbivore','omnivore')),
    danger_level    INTEGER NOT NULL CHECK (danger_level BETWEEN 1 AND 5),
    health_status   TEXT NOT NULL DEFAULT 'healthy',
    enclosure_id    INTEGER,
    feeding_level   INTEGER NOT NULL DEFAULT 100 CHECK (feeding_level BETWEEN 0 AND 100),
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (enclosure_id) REFERENCES enclosures(id) ON DELETE SET NULL
);

-- ---------- EMPLOYEES ----------
CREATE TABLE IF NOT EXISTS employees (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    name             TEXT NOT NULL,
    role             TEXT NOT NULL,
    salary           REAL NOT NULL CHECK (salary >= 0),
    assigned_zone    INTEGER,
    technical_level  INTEGER NOT NULL DEFAULT 1 CHECK (technical_level BETWEEN 1 AND 5),
    status           TEXT NOT NULL DEFAULT 'active',
    created_at       TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (assigned_zone) REFERENCES enclosures(id) ON DELETE SET NULL
);

-- ---------- TICKETS ----------
CREATE TABLE IF NOT EXISTS tickets (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    visitor_name    TEXT NOT NULL,
    ticket_type     TEXT NOT NULL,
    price           REAL NOT NULL CHECK (price >= 0),
    iva             REAL NOT NULL CHECK (iva >= 0),
    total           REAL NOT NULL CHECK (total >= 0),
    locator_code    TEXT NOT NULL UNIQUE,
    sale_date       TEXT NOT NULL DEFAULT (datetime('now'))
);

-- ---------- INVENTORY ----------
CREATE TABLE IF NOT EXISTS inventory (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    item_name       TEXT NOT NULL,
    category        TEXT NOT NULL,
    quantity        INTEGER NOT NULL DEFAULT 0 CHECK (quantity >= 0),
    minimum_stock   INTEGER NOT NULL DEFAULT 0 CHECK (minimum_stock >= 0),
    supplier        TEXT,
    price           REAL NOT NULL DEFAULT 0 CHECK (price >= 0),
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

-- ---------- MAINTENANCE TASKS ----------
CREATE TABLE IF NOT EXISTS maintenance_tasks (
    id                   INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_name           TEXT NOT NULL,
    asset_type           TEXT NOT NULL,
    priority             TEXT NOT NULL DEFAULT 'medium',
    assigned_employee_id INTEGER,
    status               TEXT NOT NULL DEFAULT 'pending',
    description          TEXT,
    created_at           TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (assigned_employee_id) REFERENCES employees(id) ON DELETE SET NULL
);

-- ---------- RANDOM EVENTS ----------
CREATE TABLE IF NOT EXISTS random_events (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type   TEXT NOT NULL,
    description  TEXT NOT NULL,
    severity     TEXT NOT NULL DEFAULT 'info',
    affected_id  INTEGER,
    created_at   TEXT NOT NULL DEFAULT (datetime('now'))
);

-- ---------- ÍNDICES DE RENDIMIENTO ----------
CREATE INDEX IF NOT EXISTS idx_dinosaurs_enclosure_id
    ON dinosaurs(enclosure_id);
CREATE INDEX IF NOT EXISTS idx_dinosaurs_diet_type
    ON dinosaurs(diet_type);
CREATE INDEX IF NOT EXISTS idx_tickets_sale_date
    ON tickets(sale_date);
CREATE INDEX IF NOT EXISTS idx_maintenance_status
    ON maintenance_tasks(status);
CREATE INDEX IF NOT EXISTS idx_random_events_created_at
    ON random_events(created_at);

-- =====================================================
-- DATOS DE DEMOSTRACIÓN
-- =====================================================

-- Usuario administrador (password: admin123 — hash sha256)
INSERT OR IGNORE INTO users (username, password_hash, role) VALUES
    ('admin', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', 'admin'),
    ('operador', '1725165c9a0b3698a3d01016e0d8205155820b8d7f21835ca64c0f81c728d880', 'operador');

-- Recintos
INSERT OR IGNORE INTO enclosures (id, name, zone_type, max_capacity, current_capacity, fence_voltage, security_level, status) VALUES
    (1, 'Valle del T-Rex',        'carnivore_zone',  3,  2, 12000, 5, 'active'),
    (2, 'Pradera Triceratops',    'herbivore_zone', 10,  6,  3000, 3, 'active'),
    (3, 'Laguna Brachiosaurus',   'herbivore_zone',  5,  3,  2500, 2, 'active'),
    (4, 'Foso Velociraptor',      'carnivore_zone',  6,  4, 15000, 5, 'active'),
    (5, 'Bosque Gallimimus',      'omnivore_zone',  15, 10,  2000, 2, 'maintenance'),
    (6, 'Pantano Spinosaurus',    'carnivore_zone',  2,  1, 14000, 5, 'active');

-- Dinosaurios
INSERT OR IGNORE INTO dinosaurs (name, species, diet_type, danger_level, health_status, enclosure_id, feeding_level) VALUES
    ('Rexy',        'Tyrannosaurus Rex',  'carnivore', 5, 'healthy',     1, 80),
    ('Bumpy',       'Tyrannosaurus Rex',  'carnivore', 4, 'observation', 1, 70),
    ('Tricia',      'Triceratops',        'herbivore', 2, 'healthy',     2, 90),
    ('Doc',         'Triceratops',        'herbivore', 2, 'healthy',     2, 85),
    ('Hammer',      'Triceratops',        'herbivore', 3, 'observation', 2, 60),
    ('Big Eatie',   'Brachiosaurus',      'herbivore', 1, 'healthy',     3, 95),
    ('Little Eatie','Brachiosaurus',      'herbivore', 1, 'healthy',     3, 90),
    ('Blue',        'Velociraptor',       'carnivore', 5, 'healthy',     4, 75),
    ('Charlie',     'Velociraptor',       'carnivore', 5, 'healthy',     4, 70),
    ('Delta',       'Velociraptor',       'carnivore', 5, 'observation', 4, 65),
    ('Echo',        'Velociraptor',       'carnivore', 5, 'healthy',     4, 80),
    ('Speedy',      'Gallimimus',         'omnivore',  1, 'healthy',     5, 88),
    ('Flash',       'Gallimimus',         'omnivore',  1, 'healthy',     5, 92),
    ('Spike',       'Spinosaurus',        'carnivore', 5, 'sick',        6, 55);

-- Empleados
INSERT OR IGNORE INTO employees (name, role, salary, assigned_zone, technical_level, status) VALUES
    ('Dra. Ellie Sattler',  'Veterinario',           3800.00, 2, 5, 'active'),
    ('Robert Muldoon',      'Guardia de seguridad',  3500.00, 1, 5, 'active'),
    ('Ray Arnold',          'Técnico',               3200.00, NULL, 4, 'active'),
    ('John Hammond',        'Gerente',               6000.00, NULL, 5, 'active'),
    ('Dennis Nedry',        'Técnico',               2900.00, NULL, 4, 'inactive'),
    ('Lex Murphy',          'Vendedor de tickets',   1900.00, NULL, 2, 'active'),
    ('Tim Murphy',          'Vendedor de tickets',   1850.00, NULL, 2, 'active'),
    ('Owen Grady',          'Veterinario',           4100.00, 4, 5, 'active'),
    ('Claire Dearing',      'Gerente',               5500.00, NULL, 5, 'active'),
    ('Barry Sembène',       'Guardia de seguridad',  3300.00, 4, 4, 'active'),
    ('Zach Mitchell',       'Limpiador',             1500.00, 2, 1, 'active'),
    ('Gray Mitchell',       'Limpiador',             1500.00, 3, 1, 'vacation');

-- Inventario
INSERT OR IGNORE INTO inventory (item_name, category, quantity, minimum_stock, supplier, price) VALUES
    ('Carne de res',          'food_carnivore',  500, 200, 'JurassicMeats',    8.50),
    ('Pollo congelado',       'food_carnivore',  300, 150, 'JurassicMeats',    5.20),
    ('Heno premium',          'food_herbivore', 1200, 500, 'EcoForage',        2.10),
    ('Hojas frescas',         'food_herbivore',  800, 400, 'EcoForage',        3.40),
    ('Frutas tropicales',     'food_omnivore',   250, 100, 'TropicalFarms',    4.75),
    ('Camisetas park',        'merchandise',     180,  50, 'ParkGear',        18.00),
    ('Gorras DinoReserve',    'merchandise',      90,  40, 'ParkGear',        14.50),
    ('Peluches Velociraptor', 'merchandise',     220,  80, 'ToyWorld',        22.00),
    ('Refrescos 500ml',       'beverage',        600, 250, 'BebidasSur',       1.80),
    ('Agua mineral 500ml',    'beverage',        750, 300, 'BebidasSur',       1.10),
    ('Botiquín médico',       'medical',          12,  10, 'MediSupply',      75.00),
    ('Tranquilizantes',       'medical',          25,  15, 'VetCare',         45.00),
    ('Combustible jeep',      'logistics',        45,  20, 'PetroSafari',      6.30),
    ('Filtros valla',         'logistics',         8,  10, 'TechFences',     120.00);

-- Tareas de mantenimiento
INSERT OR IGNORE INTO maintenance_tasks (asset_name, asset_type, priority, assigned_employee_id, status, description) VALUES
    ('Valla Valle del T-Rex',     'fence',      'critical', 3, 'in_progress', 'Revisión semanal del voltaje y sensores.'),
    ('Foso Velociraptor — puerta','fence',      'high',     3, 'pending',     'Cambiar bisagras hidráulicas.'),
    ('Bosque Gallimimus',         'enclosure',  'medium',   5, 'pending',     'Limpieza profunda y poda.'),
    ('Jeep Safari #2',            'vehicle',    'medium',   3, 'completed',   'Cambio de aceite y revisión.'),
    ('Atracción Mirador',         'attraction', 'low',      5, 'pending',     'Pintura general.'),
    ('Generador zona norte',      'power',      'high',     3, 'in_progress', 'Sustitución de baterías.');

-- Eventos aleatorios iniciales (semilla histórica)
INSERT OR IGNORE INTO random_events (event_type, description, severity, affected_id) VALUES
    ('calm_day',         'Día tranquilo en el parque. Sin incidentes.',                      'info',    NULL),
    ('feeding_delay',    'Retraso de 30 min en la alimentación de la zona herbívora.',      'warning', 2),
    ('stock_variation',  'Consumo elevado de heno premium en la mañana.',                   'info',    3);
