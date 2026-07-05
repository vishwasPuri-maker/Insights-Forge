# Module 6 - AI & Decision Engine

## ai_conversations

| Column | Type | Constraint |
|--------|------|------------|
| id | UUID | PK |
| organization_id | UUID | FK -> organizations.id |
| workspace_id | UUID | FK -> workspaces.id |
| user_id | UUID | FK -> users.id |
| title | VARCHAR(255) | NOT NULL |
| model_name | VARCHAR(100) | NOT NULL |
| created_at | TIMESTAMP | NOT NULL |
| updated_at | TIMESTAMP | NOT NULL |
| created_by | UUID | FK -> users.id |
| updated_by | UUID | FK -> users.id |
| status | VARCHAR(20) | DEFAULT 'ACTIVE' |
| is_deleted | BOOLEAN | DEFAULT FALSE |
| deleted_at | TIMESTAMP | NULL |

---

## ai_messages

| Column | Type | Constraint |
|--------|------|------------|
| id | UUID | PK |
| conversation_id | UUID | FK -> ai_conversations.id |
| sender_type | VARCHAR(20) | USER / AI |
| message | TEXT | NOT NULL |
| tokens_used | INTEGER | DEFAULT 0 |
| response_time_ms | INTEGER | NULL |
| created_at | TIMESTAMP | NOT NULL |

---

## ai_recommendations

| Column | Type | Constraint |
|--------|------|------------|
| id | UUID | PK |
| organization_id | UUID | FK -> organizations.id |
| dataset_id | UUID | FK -> datasets.id |
| analytics_result_id | UUID | FK -> analysis_results.id |
| recommendation_type | VARCHAR(100) | NOT NULL |
| recommendation | TEXT | NOT NULL |
| confidence_score | NUMERIC(5,2) | NOT NULL |
| priority | VARCHAR(20) | HIGH / MEDIUM / LOW |
| is_applied | BOOLEAN | DEFAULT FALSE |
| created_at | TIMESTAMP | NOT NULL |
| created_by | UUID | FK -> users.id |