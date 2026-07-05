# Module 7 - Forecasting

## forecast_models

| Column | Type | Constraint |
|--------|------|------------|
| id | UUID | PK |
| organization_id | UUID | FK -> organizations.id |
| dataset_id | UUID | FK -> datasets.id |
| model_name | VARCHAR(100) | NOT NULL |
| algorithm | VARCHAR(100) | NOT NULL |
| target_column | VARCHAR(100) | NOT NULL |
| parameters | JSONB | NULL |
| accuracy | NUMERIC(5,2) | NULL |
| created_by | UUID | FK -> users.id |
| created_at | TIMESTAMP | NOT NULL |
| updated_at | TIMESTAMP | NOT NULL |
| status | VARCHAR(20) | DEFAULT 'ACTIVE' |

---

## forecast_results

| Column | Type | Constraint |
|--------|------|------------|
| id | UUID | PK |
| forecast_model_id | UUID | FK -> forecast_models.id |
| prediction_date | DATE | NOT NULL |
| predicted_value | NUMERIC(18,4) | NOT NULL |
| confidence_interval | JSONB | NULL |
| actual_value | NUMERIC(18,4) | NULL |
| created_at | TIMESTAMP | NOT NULL |