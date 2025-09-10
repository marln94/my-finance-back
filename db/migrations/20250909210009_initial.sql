-- migrate:up
-- Esquema base de contabilidad

CREATE TABLE accounts (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('activo', 'pasivo', 'patrimonio', 'ingresos', 'egresos')),
    code TEXT NOT NULL UNIQUE,
    normal_side TEXT NOT NULL CHECK (normal_side IN ('debe', 'haber')),
    extra_data JSONB,
    parent_id INT REFERENCES accounts(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE banks (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    description TEXT,
    transaction_date DATE NOT NULL DEFAULT CURRENT_DATE,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE journal_entries (
    id SERIAL PRIMARY KEY,
    transaction_id INT REFERENCES transactions(id) ON DELETE CASCADE,
    account_id INT NOT NULL REFERENCES accounts(id),
    debit NUMERIC(14,2) DEFAULT 0,
    credit NUMERIC(14,2) DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE tags (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE entry_tags (
    entry_id INT NOT NULL REFERENCES journal_entries(id) ON DELETE CASCADE,
    tag_id INT NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (entry_id, tag_id)
);

-- migrate:down
DROP TABLE entry_tags;
DROP TABLE tags;
DROP TABLE journal_entries;
DROP TABLE transactions;
DROP TABLE banks;
DROP TABLE accounts;
