-- Event triggers to protect the main tables and keep the audit table schema in sync

-- 1. Prevent DROP COLUMN on audited tables
CREATE OR REPLACE FUNCTION audit.prevent_audited_column_drop()
RETURNS event_trigger AS $$
DECLARE
    obj record;
BEGIN
    FOR obj IN SELECT * FROM pg_event_trigger_dropped_objects()
    LOOP
        IF obj.object_type = 'table column' THEN
            RAISE EXCEPTION
                'Column deletion is prohibited on audited tables (attempted on %). '
                'Use change_type = 3 (soft-delete) or stop projecting the column in the app instead.',
                obj.object_identity;
        END IF;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- DROP COLUMN protection is disabled by default; enable per-deployment when policy requires it:
-- CREATE EVENT TRIGGER trg_prevent_column_drop
-- ON sql_drop
-- EXECUTE FUNCTION audit.prevent_audited_column_drop();


-- 2. Sync audit table when ALTER TABLE adds columns to a tracked table.
--
-- When a developer runs:
--   ALTER TABLE public.foo ADD COLUMN bar text;
-- and public.foo_audit already exists, this trigger calls setup_tracking so that
-- setup_tracking's pg_attribute diff (step 3) adds the missing column to foo_audit.
--
-- Recursion guard: setup_tracking itself issues ALTER TABLE statements (adding the
-- required audit columns to the main table and adding missing columns to the audit
-- table). Without the guard those internal ALTERs would re-enter this trigger
-- indefinitely. The session-local flag audit.syncing breaks the cycle.

CREATE OR REPLACE FUNCTION audit.sync_audit_columns_on_alter()
RETURNS event_trigger AS $$
DECLARE
    obj        record;
    tbl_schema text;
    tbl_name   text;
BEGIN
    IF current_setting('audit.syncing', true) = 'true' THEN
        RETURN;
    END IF;

    FOR obj IN SELECT * FROM pg_event_trigger_ddl_commands()
    LOOP
        IF obj.command_tag = 'ALTER TABLE' AND obj.object_type = 'table' THEN
            tbl_schema := obj.schema_name;
            tbl_name   := split_part(obj.object_identity, '.', 2);
            IF tbl_name = '' THEN
                tbl_name := obj.object_identity;
            END IF;

            -- Only act on tracked tables (those that already have an _audit mirror).
            -- Skip audit tables themselves and system schemas.
            IF tbl_schema NOT IN ('pg_catalog', 'information_schema', 'audit')
               AND tbl_name NOT LIKE '%_audit'
               AND to_regclass(tbl_schema || '.' || tbl_name || '_audit') IS NOT NULL
            THEN
                PERFORM set_config('audit.syncing', 'true', true);
                PERFORM audit.setup_tracking(tbl_schema, tbl_name);
                PERFORM set_config('audit.syncing', 'false', true);
            END IF;
        END IF;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

DROP EVENT TRIGGER IF EXISTS trg_sync_audit_columns;
CREATE EVENT TRIGGER trg_sync_audit_columns
ON ddl_command_end
WHEN TAG IN ('ALTER TABLE')
EXECUTE FUNCTION audit.sync_audit_columns_on_alter();


-- 3. Auto-Enrollment Hook (Zero-Touch Auditing)
--
-- Intercept CREATE TABLE and automatically wire up audit tracking and history views.
-- No developer action is required; every new table in public schema is enrolled.
--
-- Recursion guard: setup_tracking creates the _audit table (another CREATE TABLE)
-- and issues ALTER TABLE statements. The audit.syncing flag prevents re-entry from
-- both trg_auto_enroll_audit and trg_sync_audit_columns.

CREATE OR REPLACE FUNCTION audit.auto_enroll_tables()
RETURNS event_trigger AS $$
DECLARE
    obj          record;
    target_table text;
BEGIN
    IF current_setting('audit.syncing', true) = 'true' THEN
        RETURN;
    END IF;

    FOR obj IN SELECT * FROM pg_event_trigger_ddl_commands()
    LOOP
        target_table := split_part(obj.object_identity, '.', 2);
        IF target_table = '' THEN
            target_table := obj.object_identity;
        END IF;

        -- Only act on ordinary tables in non-system, non-audit schemas.
        -- Skip _audit mirrors and known migration bookkeeping tables.
        IF obj.object_type = 'table'
           AND obj.schema_name NOT IN ('pg_catalog', 'information_schema', 'audit')
           AND target_table NOT LIKE '%_audit'
           AND target_table NOT IN (
               'alembic_version',            -- Python / Alembic
               'schema_migrations',          -- Rails / golang-migrate / Flyway
               '__diesel_schema_migrations', -- Rust / Diesel
               'goose_db_version'            -- Go / Goose
           )
        THEN
            PERFORM set_config('audit.syncing', 'true', true);
            PERFORM audit.setup_tracking(obj.schema_name, target_table);
            PERFORM audit.setup_views(obj.schema_name, target_table);
            PERFORM set_config('audit.syncing', 'false', true);
        END IF;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

DROP EVENT TRIGGER IF EXISTS trg_auto_enroll_audit;
CREATE EVENT TRIGGER trg_auto_enroll_audit
ON ddl_command_end
WHEN TAG IN ('CREATE TABLE')
EXECUTE FUNCTION audit.auto_enroll_tables();
