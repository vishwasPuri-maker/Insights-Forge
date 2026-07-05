# Module 5 - Dashboard

## dashboards

| Column | Type | Constraint |
|--------|------|------------|
| id | UUID | PK |
| organization_id | UUID | FK -> organizations.id |
| workspace_id | UUID | FK -> workspaces.id |
| created_by | UUID | FK -> users.id |
| name | VARCHAR(255) | NOT NULL |
| description | TEXT | NULL |
| layout | JSONB | NOT NULL |
| is_default | BOOLEAN | DEFAULT FALSE |
| created_at | TIMESTAMP | NOT NULL |
| updated_at | TIMESTAMP | NOT NULL |
| created_by | UUID | FK -> users.id |
| updated_by | UUID | FK -> users.id |
| status | VARCHAR(20) | DEFAULT 'ACTIVE' |
| is_deleted | BOOLEAN | DEFAULT FALSE |
| deleted_at | TIMESTAMP | NULL |

---

## dashboard_widgets

| Column | Type | Constraint |
|--------|------|------------|
| id | UUID | PK |
| dashboard_id | UUID | FK -> dashboards.id |
| widget_type | VARCHAR(100) | NOT NULL |
| title | VARCHAR(255) | NOT NULL |
| chart_type | VARCHAR(100) | NOT NULL |
| data_source | VARCHAR(255) | NOT NULL |
| position | JSONB | NOT NULL |
| settings | JSONB | NULL |
| created_at | TIMESTAMP | NOT NULL |
| created_by | UUID | FK -> users.id |
| updated_by | UUID | FK -> users.id |
| status | VARCHAR(20) | DEFAULT 'ACTIVE' |
| is_deleted | BOOLEAN | DEFAULT FALSE |
| deleted_at | TIMESTAMP | NULL |