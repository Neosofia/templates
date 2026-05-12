-- Event triggers to protect the main tables and keep the audit table schema in sync 

-- 1. Prevent DROP COLUMN on audited tables
CREATE OR REPLACE FUNCTION audit.prevent_audited_column_drop()
RETURNS event_trigger AS $$
DECLARE
    obj record;
BEGIN
    -- Look for dropped columns in tables that have an active '_audit' variant
    FOR obj IN SELECT * FROM pg_event_trigger_dropped_objects()
    LOOP
        IF obj.object_type = 'table column' THEN
            -- In a true environment, we'd verify if the table is currently audited.
            -- This raises an exception halting the DROP COLUMN statement.
            RAISE EXCEPTION 'Column deletion is prohibited for audited tables (attempted on %). Set change_type = 3 or ignore it in the app instead.', obj.object_identity;
        END IF;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- To enable the drop prevention (caution: this applies globally to column drops, so filter logic normally added):
-- CREATE EVENT TRIGGER trg_prevent_column_drop 
-- ON sql_drop 
-- EXECUTE FUNCTION audit.prevent_audited_column_drop();


-- 2. Handle RENAME COLUMN (Note: PG event triggers for ALTERS require parsing command data)
-- In a simple setup without heavy C-extensions or detailed JSON parsing of event commands,
-- the prevailing pattern is to hook onto ddl_command_end where command_tag = 'ALTER TABLE'
-- and then synchronize column structures to the _audit mirror.
CREATE OR REPLACE FUNCTION audit.sync_audit_columns_on_alter()
RETURNS event_trigger AS $$
DECLARE
    obj record;
BEGIN
    FOR obj IN SELECT * FROM pg_event_trigger_ddl_commands()
    LOOP
        IF obj.command_tag = 'ALTER TABLE' THEN
            -- When a column is renamed or added on a tracked table, we can diff the 
            -- system catalogs (pg_attribute) between the main table and the _audit table
            -- to apply missing columns or rename logic.
            
            -- Because raw RENAME event parsing is complex in pure PG PL/pgSQL, a robust
            -- implementation reconstructs missing columns on the _audit table matching the main table.
            -- Logic to inject matching ALTER TABLE ... ADD COLUMN ... or RENAME.
            NULL;
        END IF;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- CREATE EVENT TRIGGER trg_sync_columns
-- ON ddl_command_end
-- WHEN TAG IN ('ALTER TABLE')
-- EXECUTE FUNCTION audit.sync_audit_columns_on_alter();


-- 3. Auto-Enrollment Hook (Zero-Touch Auditing)
-- Intercept CREATE TABLE commands and automatically apply audit tracking
CREATE OR REPLACE FUNCTION audit.auto_enroll_tables()
RETURNS event_trigger AS $$
DECLARE
    obj record;
    target_table text;
BEGIN
    FOR obj IN SELECT * FROM pg_event_trigger_ddl_commands()
    LOOP
        -- Only act on standard tables, and heavily filter out system schemas and our own generated tables
        -- to prevent infinite recursion
        IF obj.object_type = 'table' 
           AND obj.schema_name NOT IN ('pg_catalog', 'information_schema', 'audit')
           AND obj.object_identity NOT LIKE '%_audit'
        THEN
            -- pg_event_trigger_ddl_commands returns the full identity (schema.name), so we extract just the name
            target_table := split_part(obj.object_identity, '.', 2);
            IF target_table = '' THEN
                target_table := obj.object_identity;
            END IF;

            -- Automatically execute the tracking and view setups
            PERFORM audit.setup_tracking(obj.schema_name, target_table);
            PERFORM audit.setup_views(obj.schema_name, target_table);
        END IF;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- To enable zero-touch auditing:
-- CREATE EVENT TRIGGER trg_auto_enroll_audit 
-- ON ddl_command_end
-- WHEN TAG IN ('CREATE TABLE')
-- EXECUTE FUNCTION audit.auto_enroll_tables();
