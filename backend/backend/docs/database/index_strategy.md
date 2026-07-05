# Database Index Strategy

## Primary Indexes
- id

## Foreign Key Indexes
- organization_id
- user_id
- workspace_id
- dataset_id
- report_id
- dashboard_id
- role_id

## Unique Indexes
- users.email
- organizations.slug
- permissions.permission_name

## Performance Indexes
- created_at
- status
- is_deleted

## Full Text Search
- datasets.name
- reports.report_name
- notifications.title