-- Grant the application role access to the audit schema (created in 01_dml_hooks.sql).
-- Must run after 01–04.

GRANT USAGE ON SCHEMA audit TO app;
