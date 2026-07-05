# Module 2 - Workspace

## workspaces

| Column | Type | Constraint |
|--------|------|------------|
| id | UUID | PK |
| organization_id | UUID | FK -> organizations.id |
| name | VARCHAR(255) | NOT NULL |
| description | TEXT | NULL |
| industry_type | VARCHAR(100) | NOT NULL |
| created_by | UUID | FK -> users.id |
| created_at | TIMESTAMP | NOT NULL |
| updated_at | TIMESTAMP | NOT NULL |
| created_by | UUID | FK -> users.id |
| updated_by | UUID | FK -> users.id |
| status | VARCHAR(20) | DEFAULT 'ACTIVE' |
| is_deleted | BOOLEAN | DEFAULT FALSE |
| deleted_at | TIMESTAMP | NULL |

---

## workspace_members

| Column | Type | Constraint |
|--------|------|------------|
| id | UUID | PK |
| workspace_id | UUID | FK -> workspaces.id |
| user_id | UUID | FK -> users.id |
| member_role | VARCHAR(50) | NOT NULL |
| joined_at | TIMESTAMP | NOT NULL |