-- migrate:up
INSERT INTO credit_cards (bank_id, name, account_hnl_id, account_usd_id, holder_name, last_digits, is_active, description)
VALUES
    (
        (SELECT id FROM banks WHERE code='BAC'), 
        'Economía', 
        (SELECT id FROM accounts WHERE name='TC Economía HNL' LIMIT 1), 
        (SELECT id FROM accounts WHERE name='TC Economía USD' LIMIT 1), 
        'Marlon Calderón', 
        '0588', 
        TRUE, 
        'Tarjeta de crédito con descuento en supermercados (7% cash) y tiendas por departamentos (puntos BAC)'
    ),
    (
        (SELECT id FROM banks WHERE code='BAC'), 
        'Economía', 
        (SELECT id FROM accounts WHERE name='TC Economía HNL' LIMIT 1), 
        (SELECT id FROM accounts WHERE name='TC Economía USD' LIMIT 1), 
        'Gerardo Calderón', 
        '0596', 
        TRUE, 
        'Tarjeta de crédito con descuento en supermercados (7% cash) y tiendas por departamentos (puntos BAC)'
    ),
    (
        (SELECT id FROM banks WHERE code='BAC'), 
        'Conecta', 
        (SELECT id FROM accounts WHERE name='TC Conecta HNL' LIMIT 1), 
        (SELECT id FROM accounts WHERE name='TC Conecta USD' LIMIT 1), 
        'Marlon Calderón', 
        '2158', 
        TRUE, 
        'Tarjeta de crédito con descuento en telefonía, delivery, restaurantes, streaming, Amazon y más (7% cash)'
    ),
    (
        (SELECT id FROM banks WHERE code='BAC'), 
        'Conecta', 
        (SELECT id FROM accounts WHERE name='TC Conecta HNL' LIMIT 1), 
        (SELECT id FROM accounts WHERE name='TC Conecta USD' LIMIT 1), 
        'Yisela Durón', 
        '3667', 
        TRUE, 
        'Tarjeta de crédito con descuento en telefonía, delivery, restaurantes, streaming, Amazon y más (7% cash)'
    ),
    (
        (SELECT id FROM banks WHERE code='BAC'), 
        'Visa internacional', 
        (SELECT id FROM accounts WHERE name='TC Visa internacional HNL' LIMIT 1), 
        (SELECT id FROM accounts WHERE name='TC Visa internacional USD' LIMIT 1), 
        'Marlon Calderón', 
        '7166', 
        TRUE, 
        'Tarjeta de crédito sin beneficios, solo permite extrafinanciamiento sin intereses'
    ),
    (
        (SELECT id FROM banks WHERE code='BAP'), 
        'Platinum', 
        (SELECT id FROM accounts WHERE name='TC Platinum HNL' LIMIT 1), 
        (SELECT id FROM accounts WHERE name='TC Platinum USD' LIMIT 1), 
        'Marlon Calderón', 
        '2039', 
        TRUE, 
        'Tarjeta de crédito con descuento en gasolineras (10% en estado de cuenta)'
    ),
    (
        (SELECT id FROM banks WHERE code='BAP'), 
        'Platinum', 
        (SELECT id FROM accounts WHERE name='TC Platinum HNL' LIMIT 1), 
        (SELECT id FROM accounts WHERE name='TC Platinum USD' LIMIT 1), 
        'Yisela Durón', 
        '8127', 
        TRUE, 
        'Tarjeta de crédito con descuento en gasolineras (10% en estado de cuenta)'
    ),
    (
        (SELECT id FROM banks WHERE code='BAP'), 
        'Platinum', 
        (SELECT id FROM accounts WHERE name='TC Platinum HNL' LIMIT 1), 
        (SELECT id FROM accounts WHERE name='TC Platinum USD' LIMIT 1), 
        'Jael Álvarez', 
        '9547', 
        TRUE, 
        'Tarjeta de crédito con descuento en gasolineras (10% en estado de cuenta)'
    ),
    (
        (SELECT id FROM banks WHERE code='BAP'), 
        'Platinum', 
        (SELECT id FROM accounts WHERE name='TC Platinum HNL' LIMIT 1), 
        (SELECT id FROM accounts WHERE name='TC Platinum USD' LIMIT 1), 
        'Gerardo Calderón', 
        '3755', 
        TRUE, 
        'Tarjeta de crédito con descuento en gasolineras (10% en estado de cuenta)'
    ),
    (
        (SELECT id FROM banks WHERE code='BAP'), 
        'Platinum', 
        (SELECT id FROM accounts WHERE name='TC Platinum HNL' LIMIT 1), 
        (SELECT id FROM accounts WHERE name='TC Platinum USD' LIMIT 1), 
        'Yael Calderón', 
        '9645', 
        TRUE, 
        'Tarjeta de crédito con descuento en gasolineras (10% en estado de cuenta)'
    ),
    (
        (SELECT id FROM banks WHERE code='ATL'), 
        'Cash', 
        (SELECT id FROM accounts WHERE name='TC Cash HNL' LIMIT 1), 
        (SELECT id FROM accounts WHERE name='TC Cash USD' LIMIT 1), 
        'Marlon Calderón', 
        '7010', 
        TRUE, 
        'Tarjeta de crédito con descuento en restaurantes, educación y farmacias (8% cash)'
    ),
    (
        (SELECT id FROM banks WHERE code='ATL'), 
        'Cash', 
        (SELECT id FROM accounts WHERE name='TC Cash HNL' LIMIT 1), 
        (SELECT id FROM accounts WHERE name='TC Cash USD' LIMIT 1), 
        'Gerardo Calderón', 
        '9486', 
        TRUE, 
        'Tarjeta de crédito con descuento en restaurantes, educación y farmacias (8% cash)'
    ),
    (
        (SELECT id FROM banks WHERE code='ATL'), 
        'Cash', 
        (SELECT id FROM accounts WHERE name='TC Cash HNL' LIMIT 1), 
        (SELECT id FROM accounts WHERE name='TC Cash USD' LIMIT 1), 
        'Jael Álvarez', 
        '4951', 
        TRUE, 
        'Tarjeta de crédito con descuento en restaurantes, educación y farmacias (8% cash)'
    );

-- migrate:down
DELETE FROM credit_cards;
