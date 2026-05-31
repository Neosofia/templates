CREATE SCHEMA IF NOT EXISTS audit;

-- Generic DML trigger function to handle INSERT, UPDATE, DELETE
CREATE OR REPLACE FUNCTION audit.process_dml_hook()
RETURNS trigger AS $$
BEGIN
    IF (TG_OP = 'INSERT') THEN
        NEW.changed_at = now();
        NEW.change_type = 1;

        -- changed_by_uuid and changed_by_type must be supplied explicitly by the caller
        IF NEW.changed_by_uuid IS NULL OR NEW.changed_by_type IS NULL THEN
            RAISE EXCEPTION 'changed_by_uuid and changed_by_type are required for all INSERT operations on %', TG_TABLE_NAME;
        END IF;

        RETURN NEW;

    ELSIF (TG_OP = 'UPDATE') THEN
        IF NEW.changed_by_uuid IS NULL OR NEW.changed_by_type IS NULL THEN
            RAISE EXCEPTION 'changed_by_uuid and changed_by_type are required for all UPDATE operations on % (including soft-deletes)', TG_TABLE_NAME;
        END IF;

        IF NEW.change_type = 3 THEN
            NEW.changed_at = now();

            -- Archive the last active state, then the tombstone, and remove the live row.
            EXECUTE format(
                'INSERT INTO %I.%I SELECT uuidv7(), $1.*',
                TG_TABLE_SCHEMA, TG_TABLE_NAME || '_audit'
            ) USING OLD;

            EXECUTE format(
                'INSERT INTO %I.%I SELECT uuidv7(), $1.*',
                TG_TABLE_SCHEMA, TG_TABLE_NAME || '_audit'
            ) USING NEW;

            PERFORM set_config('audit.internal_delete', 'true', true);
            EXECUTE format(
                'DELETE FROM %I.%I WHERE ctid = $1',
                TG_TABLE_SCHEMA, TG_TABLE_NAME
            ) USING OLD.ctid;

            PERFORM set_config('audit.internal_delete', 'false', true);
            RETURN NULL;
        END IF;

        -- Insert the BEFORE image into the audit table
        EXECUTE format(
            'INSERT INTO %I.%I SELECT uuidv7(), $1.*',
            TG_TABLE_SCHEMA, TG_TABLE_NAME || '_audit'
        ) USING OLD;

        NEW.changed_at = now();
        NEW.change_type = 2;

        RETURN NEW;

    ELSIF (TG_OP = 'DELETE') THEN
        IF current_setting('audit.internal_delete', true) = 'true' THEN
            RETURN OLD;
        END IF;
        RAISE EXCEPTION 'Direct DELETE on % is prohibited; set change_type = 3 to soft-delete', TG_TABLE_NAME;
    END IF;

    RETURN NULL;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER SET search_path = audit, public;
