# Module 3 - Dataset Management

## datasets

| Column | Type | Constraint |
|--------|------|------------|
| id | UUID | PK |
| organization_id | UUID | FK -> organizations.id |
| workspace_id | UUID | FK -> workspaces.id |
| uploaded_by | UUID | FK -> users.id |
| name | VARCHAR(255) | NOT NULL |
| description | TEXT | NULL |
| file_name | VARCHAR(255) | NOT NULL |
| file_type | VARCHAR(50) | NOT NULL |
| storage_path | TEXT | NOT NULL |
| checksum | VARCHAR(255) | NULL |
| storage_provider | VARCHAR(50) | DEFAULT 'Neon Storage' |
| file_size | BIGINT | NOT NULL |
| total_rows | INTEGER | DEFAULT 0 |
| total_columns | INTEGER | DEFAULT 0 |
| processing_status | VARCHAR(50) | DEFAULT 'Pending' |
| created_at | TIMESTAMP | NOT NULL |
| updated_at | TIMESTAMP | NOT NULL |
| created_by | UUID | FK -> users.id |
| updated_by | UUID | FK -> users.id |
| status | VARCHAR(20) | DEFAULT 'ACTIVE' |
| is_deleted | BOOLEAN | DEFAULT FALSE |
| deleted_at | TIMESTAMP | NULL |

---

## dataset_versions

| Column | Type | Constraint |
|--------|------|------------|
| id | UUID | PK |
| dataset_id | UUID | FK -> datasets.id |
| version | INTEGER | NOT NULL |
| change_summary | TEXT | NULL |
| created_by | UUID | FK -> users.id |
| created_at | TIMESTAMP | NOT NULL |

---

## dataset_columns

| Column | Type | Constraint |
|--------|------|------------|
| id | UUID | PK |
| dataset_id | UUID | FK -> datasets.id |
| column_name | VARCHAR(255) | NOT NULL |
| data_type | VARCHAR(100) | NOT NULL |
| nullable | BOOLEAN | DEFAULT TRUE |
| unique_values | INTEGER | DEFAULT 0 |
| missing_values | INTEGER | DEFAULT 0 |

---

## dataset_uploads

| Column | Type | Constraint |
|--------|------|------------|
| id | UUID | PK |
| dataset_id | UUID | FK -> datasets.id |
| uploaded_by | UUID | FK -> users.id |
| upload_status | VARCHAR(50) | DEFAULT 'Completed' |
| uploaded_at | TIMESTAMP | NOT NULL |