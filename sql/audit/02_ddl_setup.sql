-- Function to set up auditing for a specific table (The "CREATE TABLE" hook)
CREATE OR REPLACE FUNCTION audit.setup_tracking(target_schema text, target_table text)
RETURNS void AS $$
DECLARE
    main_table_id  regclass;
    audit_table_id regclass;
    col            RECORD;
BEGIN
    main_table_id := (target_schema || '.' || target_table)::regclass;

    -- 1. Ensure the main table has the required audit columns
    EXECUTE format('ALTER TABLE %I.%I ADD COLUMN IF NOT EXISTS changed_at timestamp with time zone NOT NULL DEFAULT now()', target_schema, target_table);
    EXECUTE format('ALTER TABLE %I.%I ADD COLUMN IF NOT EXISTS changed_by_uuid uuid NOT NULL', target_schema, target_table);
    EXECUTE format('ALTER TABLE %I.%I ADD COLUMN IF NOT EXISTS changed_by_type smallint NOT NULL CHECK (changed_by_type IN (1, 2))', target_schema, target_table);
    EXECUTE format('ALTER TABLE %I.%I ADD COLUMN IF NOT EXISTS change_type smallint NOT NULL DEFAULT 1 CHECK (change_type IN (1, 2, 3))', target_schema, target_table);

    -- 2. Create the _audit mirror table if it does not yet exist.
    -- It includes all columns from the main table, plus a surrogate history_uuid.
    -- We use 'CREATE TABLE ... (LIKE ...)' to clone the structure, but we skip foreign keys and primary keys.
    EXECUTE format(
        'CREATE TABLE IF NOT EXISTS %I.%I (
            history_uuid uuid PRIMARY KEY DEFAULT uuidv7(),
            LIKE %I.%I
        )',
        target_schema, target_table || '_audit',
        target_schema, target_table
    );

    -- 3. Sync any columns present in the source table but missing from the audit table.
    audit_table_id := (target_schema || '.' || target_table || '_audit')::regclass;
    FOR col IN
        SELECT a.attname                             AS column_name,
               format_type(a.atttypid, a.atttypmod) AS data_type
        FROM   pg_attribute a
        WHERE  a.attrelid = main_table_id
          AND  a.attnum > 0
          AND  NOT a.attisdropped
          AND  NOT EXISTS (
              SELECT 1
              FROM   pg_attribute b
              WHERE  b.attrelid = audit_table_id
                AND  b.attname  = a.attname
                AND  b.attnum   > 0
                AND  NOT b.attisdropped
          )
    LOOP
        EXECUTE format(
            'ALTER TABLE %I.%I ADD COLUMN IF NOT EXISTS %I %s',
            target_schema, target_table || '_audit',
            col.column_name, col.data_type
        );
    END LOOP;

    -- 4. Wire up the triggers
    EXECUTE format(
        'DROP TRIGGER IF EXISTS trg_audit_dml ON %I.%I',
        target_schema, target_table
    );

    EXECUTE format(
        'CREATE TRIGGER trg_audit_dml
         BEFORE INSERT OR UPDATE OR DELETE ON %I.%I
         FOR EACH ROW EXECUTE FUNCTION audit.process_dml_hook()',
        target_schema, target_table
    );

    -- 5. Remove legacy v1 RLS; main tables hold live rows only.
    EXECUTE format('DROP POLICY IF EXISTS hide_soft_deleted ON %I.%I', target_schema, target_table);
    EXECUTE format('ALTER TABLE %I.%I DISABLE ROW LEVEL SECURITY', target_schema, target_table);

    -- 6. History view and read-only audit access for the app role
    PERFORM audit.setup_views(target_schema, target_table);
    PERFORM audit.grant_app_access(target_schema, target_table);

END;
$$ LANGUAGE plpgsql;
