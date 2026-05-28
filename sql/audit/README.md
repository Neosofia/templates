# Postgres 18+ Audit Schema Templates

This directory houses the raw, language-agnostic SQL templates that generate the authoritative audit infrastructure for Clinical Data Platform (CDP) services. 

These templates enforce the [before-image history table pattern](../../../cdp/architecture/structurizr/decisions/0004-full-row-audit-history-over-sparse-deltas.md) platform-wide. By separating the SQL source-of-truth from any specific framework (Alembic/Python, Active Record/Ruby, SQLx/Rust), any service can parse and execute these templates during migration-time to stay compliant.

## Design Thinking & Guiding Principles

### 1. Full-Row Snapshots, No Sparse Deltas
Every `.sql` template operates on the principle that the `_audit` table receives a complete verbatim copy of the main row *before* an update occurs. This prevents developers or auditors from having to reconstruct the state of a row at time *T* by walking a chain of partial deltas.

### 2. Autonomous History
Audit rows are strictly immutable and structurally independent.
- **No Foreign Keys**: `_audit` tables intentionally strip out any foreign key constraints. A history row must survive the deletion of related records in the database.
- **Surrogate PKs**: Each audit entry gets a time-ordered surrogate UUID (`history_uuid` using `uuid_generate_v7()`) to maintain a clean sequence of history without relying on the target table's primary key.

### 3. Database-Enforced Triggers (Atomic Writes)
The audit trail is guaranteed by the database engine, not the application logic. 
- **Atomic Execution**: Triggers fire in the exact same transaction as the modifying statement (INSERT/UPDATE/DELETE). If the audit copy fails, the main transaction aborts.
- **Timestamp Integrity**: The update trigger forcibly overwrites `changed_at` to `now()` on the target row regardless of what the application sets.
- **Hard Deletes are Prohibited**: The delete trigger actively blocks `DELETE` statements (throwing an error), enforcing our soft-delete only standard (`change_type = 3`).

### 4. Continuous History Views
The generated `_history` views seamlessly union the primary table (the *current* state) with the `_audit` table (the *historical* states). They are ordered by the entity's primary key and the `changed_at` timestamp to present a single correct timeline of evolution.

### 5. Postgres 18+ Target
These templates assume a modern Postgres 18+ environment. Constructs like standard UUID generation (e.g., native v7 UUIDs via `uuid_generate_v7()`) and modern PL/pgSQL syntax apply.

## Architecture Summary

To summarize the complete lifecycle of a record under this audit system:

1. **Inserts**: An `INSERT` to the main table is intercepted by the trigger. The trigger automatically sets `change_type = 1` (Insert) and `changed_at = now()`. The application *must* provide `changed_by_uuid` and `changed_by_type` (1 for human, 2 for service), either in the payload or via Postgres session variables (`app.current_actor_uuid` / `app.current_actor_type`). If these attribution fields are missing, the database halts the transaction. No record is written to the `_audit` table during an insert because the main table holds the initial state.
2. **Updates**: An `UPDATE` intercepts the old row *before* changes are applied, generates a `uuid_generate_v7()`, and inserts that before-image into the `_audit` history table. The trigger then modifies the incoming main table row: enforcing `changed_at = now()`, setting `change_type = 2` (Update), and refreshing the `changed_by_*` attribution fields.
3. **Deletes (Soft Deletes)**: Hard `DELETE` SQL commands are strictly prohibited by the trigger (it throws an exception). Deletions must be performed as an `UPDATE` that sets `change_type = 3` (Delete). The trigger treats this like an update: the pre-delete state is copied to the `_audit` table, and the main table row is marked as deleted.
4. **History View**: A unified `_history` view automatically `UNION ALL`s the `_audit` table and the main table. This gives auditors a complete timeline of a row—from initial creation, through all intermediate updates, ending with its current state (even if that state is a `change_type = 3` soft delete).
5. **Row-Level Security (RLS)**: The main table implements RLS (`USING change_type != 3`). This transparently hides soft-deleted records from all standard application `SELECT` queries without requiring `WHERE` clauses in application code. An escape hatch (`audit.show_deleted = 'true'`) allows authorized auditor queries to bypass this filter when necessary.

## SQL Templates

Execute in numeric order during platform init migration (`000`).

*   **`00_bootstrap_app.sql`**: Creates the restricted `app` role and `public` schema grants. Requires the migration runner to set `app.bootstrap_password` via `SELECT set_config('app.bootstrap_password', <password>, false)` with a bound parameter before executing this file.
*   **`01_dml_hooks.sql`**: Contains the generic row-level trigger `audit.process_dml_hook()` responsible for timestamping, actor attribution, and moving before-images to the audit table.
*   **`02_ddl_setup.sql`**: Exposes `audit.setup_tracking('schema', 'table')` to construct the `_audit` clone table, wire up the triggers, and apply the RLS policies.
*   **`03_ddl_protection.sql`**: Provides cluster-level event triggers to protect audited tables against rogue `DROP COLUMN` commands.
*   **`04_views.sql`**: Generates the unified `_history` timeline views.
*   **`05_grant_app_audit.sql`**: Grants the `app` role `USAGE` on the `audit` schema (must run after `01` creates that schema).

## Migration runner contract

Migration runners (Alembic or otherwise) should:
1. read the app-role password from service configuration,
2. set `app.bootstrap_password` in-session via a bound parameter (`SELECT set_config('app.bootstrap_password', <password>, false)`),
3. execute `00` through `05` in numeric order.