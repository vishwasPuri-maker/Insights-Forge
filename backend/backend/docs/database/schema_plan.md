# Insight Forge Database Schema Blueprint
**Version:** 1.0.0
**Author:** Shlok Yadav (Backend Developer)
**Project:** Insight Forge
**Database:** PostgreSQL (Neon)
**ORM:** SQLAlchemy 2.0
**Migration Tool:** Alembic
**Architecture:** Multi-Tenant
**Status:** Draft v1

---

# Purpose

This document serves as the master database blueprint for the Insight Forge platform.

It defines the logical database architecture that will be implemented using SQLAlchemy 2.0 and PostgreSQL. The schema is designed to support all project modules including Authentication, Dataset Management, Analytics, AI Recommendations, Forecasting, Dashboards, Reporting, and Notifications.

This document is considered the Single Source of Truth (SSOT) for database design.

---

# Database Design Principles

The database follows the following principles:

- Multi-Tenant Architecture
- UUID Primary Keys
- Soft Delete Support
- Audit Trail
- SQLAlchemy Compatible
- PostgreSQL Optimized
- Third Normal Form (3NF)
- Role-Based Access Control (RBAC)
- High Scalability
- Future AI Expansion Support

---

# Technology Stack

Database:
- PostgreSQL (Neon)

ORM:
- SQLAlchemy 2.0

Migration:
- Alembic

Backend:
- FastAPI

Language:
- Python 3.12

---

# Core Business Modules

The database is divided into the following modules:

1. Identity & Access Management
2. Organization Management
3. Workspace Management
4. Dataset Management
5. Analytics Engine
6. Dashboard Management
7. AI Recommendation Engine
8. Forecasting Engine
9. Reporting System
10. Notification System
11. System Monitoring & Audit

---

# Global Database Standards

Every major table should contain the following standard fields:

- id (UUID Primary Key)
- tenant_id (UUID Foreign Key)
- created_at
- updated_at
- created_by
- updated_by
- status

These fields ensure consistency across all business modules.

---

# Current Status

✅ Database Architecture Planning

⬜ Entity Design

⬜ Relationship Design

⬜ ER Diagram

⬜ SQLAlchemy Models

⬜ Alembic Migration

⬜ API Integration

---

# Notes

This document will evolve during development but all architectural changes must be reviewed before implementation.
