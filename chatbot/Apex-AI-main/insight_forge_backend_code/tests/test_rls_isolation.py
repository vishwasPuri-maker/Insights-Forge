"""Integration test: PostgreSQL RLS enforces multi-tenant isolation.

Proves that, with the policies from database/rls_policies.sql applied, a session
scoped to organization A **cannot read organization B's rows even with a direct,
unfiltered SQL query** (`SELECT ... FROM records` with no WHERE organization_id).

The test:
  1. inserts two orgs (A and B) each with a full data chain, before RLS is forced
     (table owner bypasses RLS until FORCE),
  2. applies database/rls_policies.sql (ENABLE + FORCE + org_isolation policy),
  3. sets the org context to A and runs raw unfiltered SELECTs — asserting only
     A's rows are visible and B's are completely hidden (and vice-versa),
  4. tears everything down (removes RLS from the data tables, deletes both orgs)
     so the database and the app's normal operation are left unchanged.

All rows are is_demo=true. Auth tables (organizations/users/user_sessions) are
intentionally NOT covered by RLS.
"""
import uuid

import pytest
from sqlalchemy import text

from app.auth.security import hash_password
from app.database import SessionLocal, engine
from app.models import Dataset, DecisionCard, Organization, Record, User

DATA_TABLES = ["datasets", "records", "decision_cards", "reports", "kpi_thresholds"]

# The app connects as the Neon owner role, which has BYPASSRLS — so RLS never
# constrains it (isolation there comes from the explicit organization_id filter in
# every query). To PROVE the RLS policies themselves work, this test creates a
# dedicated non-privileged role (no BYPASSRLS) and runs the direct queries as that
# role via SET ROLE. That's exactly the posture a locked-down app DB user would use.
TEST_ROLE = "rls_test_role"

# Mirrors database/rls_policies.sql. Applied per-table here (rather than executing
# the file's DO block) because psycopg treats the block's `format('%I')` specifiers
# as bind placeholders. The policy DDL below is identical to what the file installs.
_POLICY = (
    "USING (organization_id = NULLIF(current_setting('app.current_organization_id', true), '')::uuid) "
    "WITH CHECK (organization_id = NULLIF(current_setting('app.current_organization_id', true), '')::uuid)"
)


def _role_exists(conn) -> bool:
    return conn.exec_driver_sql(
        f"SELECT 1 FROM pg_roles WHERE rolname = '{TEST_ROLE}'"
    ).fetchone() is not None


def _setup_role() -> None:
    with engine.begin() as conn:
        if _role_exists(conn):
            for t in DATA_TABLES:
                conn.exec_driver_sql(f"REVOKE ALL ON {t} FROM {TEST_ROLE}")
            conn.exec_driver_sql(f"REVOKE ALL ON SCHEMA public FROM {TEST_ROLE}")
            conn.exec_driver_sql(f"DROP ROLE {TEST_ROLE}")
        conn.exec_driver_sql(f"CREATE ROLE {TEST_ROLE} NOLOGIN")  # NOBYPASSRLS by default
        # Let the current (owner) role SET ROLE into it for the proof queries.
        conn.exec_driver_sql(f"GRANT {TEST_ROLE} TO CURRENT_USER")
        conn.exec_driver_sql(f"GRANT USAGE ON SCHEMA public TO {TEST_ROLE}")
        for t in DATA_TABLES:
            conn.exec_driver_sql(f"GRANT SELECT ON {t} TO {TEST_ROLE}")


def _teardown_role() -> None:
    with engine.begin() as conn:
        if _role_exists(conn):
            for t in DATA_TABLES:
                conn.exec_driver_sql(f"REVOKE ALL ON {t} FROM {TEST_ROLE}")
            conn.exec_driver_sql(f"REVOKE ALL ON SCHEMA public FROM {TEST_ROLE}")
            conn.exec_driver_sql(f"DROP ROLE {TEST_ROLE}")


def _apply_rls() -> None:
    with engine.begin() as conn:
        for t in DATA_TABLES:
            conn.exec_driver_sql(f"ALTER TABLE {t} ENABLE ROW LEVEL SECURITY")
            conn.exec_driver_sql(f"ALTER TABLE {t} FORCE ROW LEVEL SECURITY")
            conn.exec_driver_sql(f"DROP POLICY IF EXISTS org_isolation ON {t}")
            conn.exec_driver_sql(f"CREATE POLICY org_isolation ON {t} {_POLICY}")


def _remove_rls() -> None:
    with engine.begin() as conn:
        for t in DATA_TABLES:
            conn.exec_driver_sql(f"ALTER TABLE {t} NO FORCE ROW LEVEL SECURITY")
            conn.exec_driver_sql(f"ALTER TABLE {t} DISABLE ROW LEVEL SECURITY")
            conn.exec_driver_sql(f"DROP POLICY IF EXISTS org_isolation ON {t}")


def _make_org(db, name: str) -> tuple[uuid.UUID, uuid.UUID]:
    """Create org + user + dataset + record + decision card. Returns (org_id, record_id)."""
    org = Organization(name=name, is_demo=True)
    db.add(org)
    db.flush()
    user = User(
        organization_id=org.id, email=f"rls-{uuid.uuid4().hex[:10]}@demo-decisiq.com",
        password_hash=hash_password("rls-pass-123"), role="admin", sector="retail", is_demo=True,
    )
    db.add(user)
    db.flush()
    ds = Dataset(
        organization_id=org.id, uploaded_by=user.id, sector="retail",
        original_filename="rls.csv", s3_key="rls/rls.csv", status="ready", is_demo=True,
    )
    db.add(ds)
    db.flush()
    rec = Record(
        organization_id=org.id, dataset_id=ds.id, sector="retail",
        data={"marker": name}, is_demo=True,
    )
    db.add(rec)
    db.add(DecisionCard(
        organization_id=org.id, sector="retail", title=f"{name} card", status="pending", is_demo=True,
    ))
    db.flush()
    return org.id, rec.id


@pytest.fixture
def two_orgs():
    db = SessionLocal()
    try:
        org_a, rec_a = _make_org(db, "RLS-Org-A")
        org_b, rec_b = _make_org(db, "RLS-Org-B")
        db.commit()
    finally:
        db.close()
    yield {"a": org_a, "b": org_b, "rec_a": rec_a, "rec_b": rec_b}
    # teardown: drop RLS + the test role, then delete everything we created
    _remove_rls()
    _teardown_role()
    db = SessionLocal()
    try:
        for oid in (org_a, org_b):
            db.execute(text("DELETE FROM decision_cards WHERE organization_id=:o"), {"o": oid})
            db.execute(text("DELETE FROM records WHERE organization_id=:o"), {"o": oid})
            db.execute(text("DELETE FROM datasets WHERE organization_id=:o"), {"o": oid})
            db.execute(text("DELETE FROM users WHERE organization_id=:o"), {"o": oid})
            db.execute(text("DELETE FROM organizations WHERE id=:o"), {"o": oid})
        db.commit()
    finally:
        db.close()


def _visible_org_ids(org_id: uuid.UUID) -> set[str]:
    """Raw, UNFILTERED select of records under the given org context, as the
    non-bypass TEST_ROLE (so RLS actually applies)."""
    with engine.begin() as conn:
        conn.exec_driver_sql(f"SET LOCAL ROLE {TEST_ROLE}")
        conn.exec_driver_sql(
            "SELECT set_config('app.current_organization_id', %s, true)", (str(org_id),)
        )
        rows = conn.exec_driver_sql("SELECT organization_id FROM records").fetchall()
    return {str(r[0]) for r in rows}


def test_org_cannot_read_other_orgs_rows(two_orgs):
    org_a, org_b = two_orgs["a"], two_orgs["b"]
    _setup_role()
    _apply_rls()

    # Under org A context, a direct unfiltered query sees ONLY org A rows.
    visible_a = _visible_org_ids(org_a)
    assert str(org_a) in visible_a, "org A should see its own rows"
    assert str(org_b) not in visible_a, "org A must NOT see org B's rows"
    assert visible_a == {str(org_a)}

    # Symmetric: org B sees only its own.
    visible_b = _visible_org_ids(org_b)
    assert visible_b == {str(org_b)}

    # Direct fetch of org B's specific record id, under org A context -> 0 rows.
    with engine.begin() as conn:
        conn.exec_driver_sql(f"SET LOCAL ROLE {TEST_ROLE}")
        conn.exec_driver_sql(
            "SELECT set_config('app.current_organization_id', %s, true)", (str(org_a),)
        )
        n = conn.exec_driver_sql(
            "SELECT count(*) FROM records WHERE id = %s", (str(two_orgs["rec_b"]),)
        ).scalar()
    assert n == 0, "org A must not be able to fetch org B's record even by its id"

    # With NO org context set, RLS hides everything (fail closed).
    with engine.begin() as conn:
        conn.exec_driver_sql(f"SET LOCAL ROLE {TEST_ROLE}")
        n = conn.exec_driver_sql("SELECT count(*) FROM records").scalar()
    assert n == 0, "with no org context, no rows should be visible"
