-- Bootstrap the restricted application role used at runtime (APP_DATABASE_URL).
--
-- Contract: the migration runner MUST set the password before executing this file:
--   SELECT set_config('app.bootstrap_password', <password>, false);
-- Use a bound parameter; do not interpolate the raw password into SQL text.

DO $$
BEGIN
    EXECUTE format(
        'CREATE ROLE app WITH LOGIN PASSWORD %L',
        current_setting('app.bootstrap_password', true)
    );
EXCEPTION
    WHEN duplicate_object THEN NULL;
END $$;

DO $$
BEGIN
    EXECUTE format(
        'GRANT CONNECT ON DATABASE %I TO app',
        current_database()
    );
END $$;

GRANT USAGE ON SCHEMA public TO app;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT SELECT, INSERT, UPDATE ON TABLES TO app;
