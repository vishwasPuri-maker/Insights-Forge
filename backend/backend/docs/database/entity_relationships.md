# Entity Relationships

organizations
│
├── users (1:N)
│   ├── user_sessions (1:N)
│   └── user_roles (1:N)
│
├── workspaces (1:N)
│   └── workspace_members (1:N)
│
├── datasets (1:N)
│   ├── dataset_versions (1:N)
│   ├── dataset_columns (1:N)
│   ├── dataset_uploads (1:N)
│   ├── analytics_jobs (1:N)
│   ├── analytics_results (1:N)
│   ├── ai_recommendations (1:N)
│   └── forecast_results (1:N)
│
├── dashboards (1:N)
│   └── dashboard_widgets (1:N)
│
├── reports (1:N)
│   └── report_exports (1:N)
│
├── notifications (1:N)
│
└── audit_logs (1:N)

roles
│
└── user_roles (1:N)

permissions
│
└── roles (M:N)