-- Function to set up auditing for a specific table (The "CREATE TABLE" hook)
CREATE OR REPLACE FUNCTION audit.setup_tracking(target_schema text, target_table text)
RETURNS void AS $$
DECLARE
    main_table_id regclass;
BEGIN
    main_table_id := (target_schema || '.' || target_table)::regclass;

    -- 1. Ensure the main table has the required audit columns
    EXECUTE format('ALTER TABLE %I.%I ADD COLUMN IF NOT EXISTS changed_at timestamp with time zone NOT NULL DEFAULT now()', target_schema, target_table);
    EXECUTE format('ALTER TABLE %I.%I ADD COLUMN IF NOT EXISTS changed_by_uuid uuid NOT NULL', target_schema, target_table);
    EXECUTE format('ALTER TABLE %I.%I ADD COLUMN IF NOT EXISTS changed_by_type smallint NOT NULL CHECK (changed_by_type IN (1, 2))', target_schema, target_table);
    EXECUTE format('ALTER TABLE %I.%I ADD COLUMN IF NOT EXISTS change_type smallint NOT NULL DEFAULT 1 CHECK (change_type IN (1, 2, 3))', target_schema, target_table);

    -- 2. Create the _audit mirror table
    -- It includes all columns from the main table, plus a surrogate history_uuid.
    -- We use 'CREATE TABLE ... (LIKE ...)' to clone the structure, but we skip foreign keys and primary keys.
    EXECUTE format(
        'CREATE TABLE IF NOT EXISTS %I.%I (
            history_uuid uuid PRIMARY KEY DEFAULT uuid_generate_v7(),
            LIKE %I.%I
        )', 
        target_schema, target_table || '_audit',
        target_schema, target_table
    );

    -- 3. Wire up the triggers
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

    -- 4. Enable Row-Level Security to hide soft-deleted rows by default
    -- This enforces "change_type != 3" natively on all reads.
    -- Allows bypass if the application explicitly sets 'audit.show_deleted = true' in the transaction.
    EXECUTE format('ALTER TABLE %I.%I ENABLE ROW LEVEL SECURITY', target_schema, target_table);
    EXECUTE format('DROP POLICY IF EXISTS hide_soft_deleted ON %I.%I', target_schema, target_table);
    EXECUTE format(
        'CREATE POLICY hide_soft_deleted ON %I.%I 
         FOR SELECT 
         USING (change_type != 3 OR current_setting(''audit.show_deleted'', true) = ''true'')', 
        target_schema, target_table
    );

END;
$$ LANGUAGE plpgsql;
