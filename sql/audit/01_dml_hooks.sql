CREATE SCHEMA IF NOT EXISTS audit;

-- Generic DML trigger function to handle INSERT, UPDATE, DELETE
CREATE OR REPLACE FUNCTION audit.process_dml_hook()
RETURNS trigger AS $$
DECLARE
    audit_table_name text := TG_TABLE_SCHEMA || '.' || TG_TABLE_NAME || '_audit';
BEGIN
    IF (TG_OP = 'INSERT') THEN
        -- Set defaults for audit columns on insert
        NEW.changed_at = now();
        NEW.change_type = 1;
        -- Read actor details from transaction session variables, falling back to the column payloads if provided
        NEW.changed_by_uuid = COALESCE(NEW.changed_by_uuid, NULLIF(current_setting('app.current_actor_uuid', true), '')::uuid);
        NEW.changed_by_type = COALESCE(NEW.changed_by_type, NULLIF(current_setting('app.current_actor_type', true), '')::smallint);
        
        -- Enforce attribution
        IF NEW.changed_by_uuid IS NULL OR NEW.changed_by_type IS NULL THEN
            RAISE EXCEPTION 'changed_by_uuid and changed_by_type are required for all INSERT operations on %', TG_TABLE_NAME;
        END IF;

        RETURN NEW;
        
    ELSIF (TG_OP = 'UPDATE') THEN
        -- Insert the BEFORE image into the audit table
        -- We generate a history_uuid for the audit row automatically (using time-ordered uuidv7)
        EXECUTE format(
            'INSERT INTO %I.%I SELECT uuid_generate_v7(), $1.*', 
            TG_TABLE_SCHEMA, TG_TABLE_NAME || '_audit'
        ) USING OLD;
        
        -- Enforce timestamp update
        NEW.changed_at = now();
        
        -- Default to 'update' (2) unless the app explicitly set it to 'delete' (3) for soft-delete
        IF NEW.change_type IS DISTINCT FROM 3 THEN
             NEW.change_type = 2;
        END IF;

        NEW.changed_by_uuid = COALESCE(NEW.changed_by_uuid, NULLIF(current_setting('app.current_actor_uuid', true), '')::uuid);
        NEW.changed_by_type = COALESCE(NEW.changed_by_type, NULLIF(current_setting('app.current_actor_type', true), '')::smallint);

        -- Enforce attribution
        IF NEW.changed_by_uuid IS NULL OR NEW.changed_by_type IS NULL THEN
            RAISE EXCEPTION 'changed_by_uuid and changed_by_type are required for all UPDATE operations on % (including soft-deletes)', TG_TABLE_NAME;
        END IF;
        
        RETURN NEW;
        
    ELSIF (TG_OP = 'DELETE') THEN
        RAISE EXCEPTION 'Direct DELETE on % is prohibited; set change_type = 3 to soft-delete', TG_TABLE_NAME;
    END IF;
    
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;
