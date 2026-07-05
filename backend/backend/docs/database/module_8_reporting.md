# Module 8 - Reporting

## reports

| Column | Type | Constraint |
|--------|------|------------|
| id | UUID | PK |
| organization_id | UUID | FK -> organizations.id |
| workspace_id | UUID | FK -> workspaces.id |
| created_by | UUID | FK -> users.id |
| report_name | VARCHAR(255) | NOT NULL |
| report_type | VARCHAR(100) | NOT NULL |
| report_config | JSONB | NOT NULL |
| created_at | TIMESTAMP | NOT NULL |
| updated_at | TIMESTAMP | NOT NULL |
| status | VARCHAR(20) | DEFAULT 'ACTIVE' |

---

## report_exports

| Column | Type | Constraint |
|--------|------|------------|
| id | UUID | PK |
| report_id | UUID | FK -> reports.id |
| exported_by | UUID | FK -> users.id |
| export_format | VARCHAR(20) | PDF / XLSX / CSV |
| file_path | TEXT | NOT NULL |
| file_size | BIGINT | NULL |
| exported_at | TIMESTAMP | NOT NULL |