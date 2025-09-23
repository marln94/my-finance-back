-- migrate:up
INSERT INTO banks (name, code)
VALUES
    ('BAC', 'BAC'),
    ('Atlantida', 'ATL'),
    ('Banpais', 'BAP'),
    ('Ficohsa', 'FIC');

-- migrate:down
DELETE FROM banks;
