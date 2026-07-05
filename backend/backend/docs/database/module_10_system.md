# Module 10 - System

## audit_logs

| Column | Type | Constraint |
|--------|------|------------|
| id | UUID | PK |
| organization_id | UUID | FK -> organizations.id |
| user_id | UUID | FK -> users.id |
| entity_type | VARCHAR(100) | NOT NULL |
| entity_id | UUID | NOT NULL |
| action | VARCHAR(50) | CREATE / UPDATE / DELETE / LOGIN |
| old_values | JSONB | NULL |
| new_values | JSONB | NULL |
| ip_address | VARCHAR(45) | NULL |
| user_agent | TEXT | NULL |
| created_at | TIMESTAMP | NOT NULL |

---

## system_settings

| Column | Type | Constraint |
|--------|------|------------|
| id | UUID | PK |
| organization_id | UUID | FK -> organizations.id |
| setting_key | VARCHAR(100) | NOT NULL |
| setting_value | JSONB | NOT NULL |
| description | TEXT | NULL |
| updated_by | UUID | FK -> users.id |
| updated_at | TIMESTAMP | NOT NULL |