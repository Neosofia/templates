-- Grant the application role access to the audit schema (created in 01_dml_hooks.sql).
-- Must run after 01–04.

GRANT USAGE ON SCHEMA audit TO app;

CREATE OR REPLACE FUNCTION audit.grant_app_access(target_schema text, target_table text)
RETURNS void AS $$
BEGIN
    EXECUTE format('REVOKE INSERT, UPDATE, DELETE ON %I.%I FROM app', target_schema, target_table || '_audit');
    EXECUTE format('GRANT SELECT ON %I.%I TO app', target_schema, target_table || '_audit');
    EXECUTE format('GRANT SELECT ON %I.%I TO app', target_schema, target_table || '_history');
END;
$$ LANGUAGE plpgsql;
