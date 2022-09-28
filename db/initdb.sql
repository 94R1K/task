-- psql -U postgres # "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\PostgreSQL 14"
-- CREATE USER yaroslav WITH password '20031956';
-- CREATE DATABASE postgres_db OWNER yaroslav;

CREATE
    OR REPLACE FUNCTION trigger_set_timestamp()
    RETURNS TRIGGER AS
$$
BEGIN
    NEW.updated_at
        = NOW();
    RETURN NEW;
END;
$$
    LANGUAGE plpgsql;



CREATE TABLE Orders
(
    id                        SERIAL                    NOT NULL PRIMARY KEY,
    table_row_index           INTEGER                   NOT NULL UNIQUE,     -- номер строки в адресе вида A1:A50
    table_row_number          INTEGER                   NOT NULL,
    order_number              INTEGER                   NOT NULL UNIQUE,
    cost_usd                  NUMERIC(12, 2)            NOT NULL,
    cost_rub                  NUMERIC(12, 2)            NOT NULL,
    delivery_date             CHAR(10)                  NOT NULL,
    created_at                TIMESTAMPTZ               NOT NULL DEFAULT NOW(),
    updated_at                TIMESTAMPTZ               NOT NULL DEFAULT NOW()
);

CREATE TRIGGER set_timestamp
    BEFORE UPDATE
    ON Orders
    FOR EACH ROW
EXECUTE PROCEDURE trigger_set_timestamp();

CREATE
    OR REPLACE FUNCTION upsert_orders(
        arg_table_row_index INTEGER,
        arg_table_row_number INTEGER,
        arg_order_number INTEGER,
        arg_cost_usd DOUBLE PRECISION,
        arg_cost_rub DOUBLE PRECISION,
        arg_delivery_date CHAR(10)
    )
    RETURNS VOID AS
$$
DECLARE
BEGIN
    UPDATE Orders as o SET
        table_row_number = arg_table_row_number,
        order_number = arg_order_number,
        cost_usd = arg_cost_usd,
        cost_rub = arg_cost_rub,
        delivery_date = arg_delivery_date
    WHERE table_row_index = arg_table_row_index;

    IF NOT FOUND THEN

    INSERT INTO Orders(table_row_index, table_row_number, order_number, cost_rub, cost_usd, delivery_date)
    VALUES (arg_table_row_index, arg_table_row_number, arg_order_number, arg_cost_rub, arg_cost_usd, arg_delivery_date);

    END IF;
END;
$$
    LANGUAGE plpgsql;