# Insight Forge Database Design

Version: 1.0.0

Status: Architecture Design

Owner: Backend Team

Author: Shlok Yadav

---

# Objective

This document defines the complete logical database architecture for the Insight Forge platform.

The database is designed to support:

- Multi-Tenant Organizations
- Authentication
- RBAC
- Dataset Management
- AI Analytics
- Dashboard Management
- Forecasting
- Reporting
- Notifications
- Audit Logs

The design follows PostgreSQL best practices and SQLAlchemy 2.0 conventions.

---

# Database Philosophy

The database has been designed using the following principles.

- PostgreSQL Native
- SQLAlchemy First
- Multi Tenant
- Highly Scalable
- Modular
- Third Normal Form (3NF)
- UUID Primary Keys
- Soft Delete Ready
- Audit Ready
- API First Design

---

# Core Modules

The system is divided into eleven logical modules.

## Module 1

Identity & Access

Responsible for

- Users
- Roles
- Permissions
- Sessions

---

## Module 2

Organization Management

Responsible for

- Organizations
- Departments
- Teams

---

## Module 3

Workspace Management

Responsible for

- Workspaces
- Members

---

## Module 4

Dataset Management

Responsible for

- Datasets
- Dataset Versions
- Dataset Columns
- Upload History

---

## Module 5

Analytics

Responsible for

- Processing Jobs
- Analytics Results
- KPI Storage

---

## Module 6

Dashboards

Responsible for

- Dashboards
- Widgets
- Layout

---

## Module 7

AI

Responsible for

- Conversations
- Messages
- Recommendations

---

## Module 8

Forecasting

Responsible for

- Forecast Models
- Forecast Results

---

## Module 9

Reporting

Responsible for

- Reports
- Report Exports

---

## Module 10

Notifications

Responsible for

- Notifications
- User Alerts

---

## Module 11

System

Responsible for

- Audit Logs
- Settings
- Activity Logs

---


---

# Global Database Standards

Every business table must follow these standards:

## Primary Key
- UUID
- Auto Generated

## Audit Fields
- created_at
- updated_at
- created_by
- updated_by

## Soft Delete
- is_deleted
- deleted_at

## Status
- status

## Multi Tenancy

Every business table belongs to exactly one Organization.

All business data must be isolated using:

organization_id (UUID)

## Naming Convention

Table Names:
snake_case plural

Examples

users

organizations

datasets

dashboard_widgets

Column Names:
snake_case

Foreign Keys:
<entity>_id

Examples

user_id

organization_id

workspace_id

dataset_id



# Next Step

The next document (table_dictionary.md) defines every table in detail.
---