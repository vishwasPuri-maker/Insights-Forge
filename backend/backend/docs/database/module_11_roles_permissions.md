# Module 11 - RBAC

## permissions

| Column | Type | Constraint |
|--------|------|------------|
| id | UUID | PK |
| permission_name | VARCHAR(100) | UNIQUE |
| description | TEXT | NULL |

---

## role_permissions

| Column | Type | Constraint |
|--------|------|------------|
| id | UUID | PK |
| role_id | UUID | FK -> roles.id |
| permission_id | UUID | FK -> permissions.id |