-- Function to generate the required views for an audited table
CREATE OR REPLACE FUNCTION audit.setup_views(target_schema text, target_table text)
RETURNS void AS $$
DECLARE
    col_list text;
BEGIN
    -- Get the comma-separated list of columns for the target table
    -- so we can safely UNION the main table and the _audit table.
    SELECT string_agg(quote_ident(column_name), ', ')
    INTO col_list
    FROM information_schema.columns
    WHERE table_schema = target_schema
      AND table_name = target_table;

    -- 1. Create the _history view (as defined in the spec)
    -- Unions the target table (current state) with the _audit table (historical states)
    EXECUTE format(
        'CREATE OR REPLACE VIEW %I.%I AS
         SELECT 
             history_uuid,
             %s
         FROM %I.%I
         
         UNION ALL
         
         SELECT 
             NULL::uuid AS history_uuid,
             %s
         FROM %I.%I',
        target_schema, target_table || '_history',
        col_list,
        target_schema, target_table || '_audit',
        col_list,
        target_schema, target_table
    );

END;
$$ LANGUAGE plpgsql;
