# Module 9 - Notifications

## notifications

| Column | Type | Constraint |
|--------|------|------------|
| id | UUID | PK |
| organization_id | UUID | FK -> organizations.id |
| user_id | UUID | FK -> users.id |
| title | VARCHAR(255) | NOT NULL |
| message | TEXT | NOT NULL |
| notification_type | VARCHAR(50) | INFO / WARNING / ERROR / SUCCESS |
| delivery_channel | VARCHAR(30) | IN_APP / EMAIL / SMS |
| is_read | BOOLEAN | DEFAULT FALSE |
| read_at | TIMESTAMP | NULL |
| created_at | TIMESTAMP | NOT NULL |
| updated_at | TIMESTAMP | NOT NULL |
| status | VARCHAR(20) | DEFAULT 'ACTIVE' |