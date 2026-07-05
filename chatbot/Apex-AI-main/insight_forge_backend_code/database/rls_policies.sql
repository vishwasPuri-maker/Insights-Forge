-- Row-Level Security policies for the data tables (multi-tenant isolation).
--
-- Isolation is keyed on organization_id. Before any org-scoped query the API sets
--   SELECT set_config('app.current_organization_id', '<org-uuid>', true);
-- (see app/database.py: set_organization_context). These policies compare each
-- row's organization_id against that setting so an org only ever sees its own rows.
--
-- Auth tables (organizations, users, user_sessions) are NOT RLS-protected — they
-- are accessed by uuid/email during login before any org context exists.
--
-- Apply with:  psql "$DATABASE_URL" -f database/rls_policies.sql
--
-- NOTE: the app currently ALSO filters by organization_id in every query as
-- defense in depth, so isolation holds even before these policies are applied.
-- FORCE is used so the table owner is subject to the policy too.

DO $$
DECLARE
    tbl text;
BEGIN
    FOREACH tbl IN ARRAY ARRAY['datasets', 'records', 'decision_cards', 'reports', 'kpi_thresholds']
    LOOP
        EXECUTE format('ALTER TABLE %I ENABLE ROW LEVEL SECURITY;', tbl);
        EXECUTE format('ALTER TABLE %I FORCE ROW LEVEL SECURITY;', tbl);
        EXECUTE format('DROP POLICY IF EXISTS org_isolation ON %I;', tbl);
        -- NULLIF(..., '') so an unset/empty context yields NULL (no rows) instead of
        -- erroring on ''::uuid — fail closed when no org context is set.
        EXECUTE format($f$
            CREATE POLICY org_isolation ON %I
            USING (organization_id = NULLIF(current_setting('app.current_organization_id', true), '')::uuid)
            WITH CHECK (organization_id = NULLIF(current_setting('app.current_organization_id', true), '')::uuid);
        $f$, tbl);
    END LOOP;
END $$;
