# Module 4 - Analytics

##  analysis_jobs

| Column | Type | Constraint |
|--------|------|------------|
| id | UUID | PK |
| dataset_id | UUID | FK -> datasets.id |
| initiated_by | UUID | FK -> users.id |
| job_type | VARCHAR(100) | NOT NULL |
| status | VARCHAR(50) | DEFAULT 'Pending' |
| progress | INTEGER | DEFAULT 0 |
| error_message | TEXT | NULL |
| started_at | TIMESTAMP | NULL |
| completed_at | TIMESTAMP | NULL |
| created_at | TIMESTAMP | NOT NULL |
| created_by | UUID | FK -> users.id |
| updated_by | UUID | FK -> users.id |

---

## analysis_results

| Column | Type | Constraint |
|--------|------|------------|
| id | UUID | PK |
| job_id | UUID | FK -> analysis_jobs.id |
| dataset_id | UUID | FK -> datasets.id |
| metric_name | VARCHAR(255) | NOT NULL |
| metric_value | JSONB | NOT NULL |
| visualization_type | VARCHAR(100) | NULL |
| created_at | TIMESTAMP | NOT NULL |