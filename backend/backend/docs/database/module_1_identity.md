# Module 1 - Identity & Access

## organizations

| Column | Type | Constraint |
|--------|------|------------|
| id | UUID | PK |
| name | VARCHAR(255) | NOT NULL |
| slug | VARCHAR(100) | UNIQUE |
| industry | VARCHAR(100) | NOT NULL |
| subscription_plan | VARCHAR(50) | DEFAULT 'Free' |
| status | VARCHAR(20) | DEFAULT 'Active' |
| created_at | TIMESTAMP | NOT NULL |
| updated_at | TIMESTAMP | NOT NULL |
| created_by | UUID | FK -> users.id |
| updated_by | UUID | FK -> users.id |
| is_deleted | BOOLEAN | DEFAULT FALSE |
| deleted_at | TIMESTAMP | NULL |

---

## users

| Column | Type | Constraint |
|--------|------|------------|
| id | UUID | PK |
| organization_id | UUID | FK -> organizations.id |
| first_name | VARCHAR(100) | NOT NULL |
| last_name | VARCHAR(100) | NOT NULL |
| email | VARCHAR(255) | UNIQUE |
| password_hash | TEXT | NOT NULL |
| phone | VARCHAR(20) | NULL |
| is_verified | BOOLEAN | DEFAULT FALSE |
| status | VARCHAR(20) | DEFAULT 'Active' |
| created_at | TIMESTAMP | NOT NULL |
| updated_at | TIMESTAMP | NOT NULL |
| last_login | TIMESTAMP | NULL |
| profile_image | TEXT | NULL |
| created_by | UUID | FK -> users.id |
| updated_by | UUID | FK -> users.id |
| is_deleted | BOOLEAN | DEFAULT FALSE |
| deleted_at | TIMESTAMP | NULL |

---

## roles

| Column | Type | Constraint |
|--------|------|------------|
| id | UUID | PK |
| organization_id | UUID | FK |
| name | VARCHAR(100) | UNIQUE |
| description | TEXT | NULL |

---

## permissions

| Column | Type | Constraint |
|--------|------|------------|
| id | UUID | PK |
| permission_name | VARCHAR(100) | UNIQUE |
| description | TEXT | NULL |

---

## user_roles

| Column | Type | Constraint |
|--------|------|------------|
| id | UUID | PK |
| user_id | UUID | FK -> users.id |
| role_id | UUID | FK -> roles.id |

---

## user_sessions

| Column | Type | Constraint |
|--------|------|------------|
| id | UUID | PK |
| user_id | UUID | FK -> users.id |
| refresh_token | TEXT | NOT NULL |
| expires_at | TIMESTAMP | NOT NULL |
| created_at | TIMESTAMP | NOT NULL |