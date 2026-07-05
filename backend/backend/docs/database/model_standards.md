# Insights Forge Backend
# SQLAlchemy Model Standards v1.0

---

# Purpose

This document defines the standards every SQLAlchemy model must follow.

All backend contributors must follow these rules.

No model should violate these standards unless the team explicitly approves a change.

---

# 1. Base Classes

There are two abstract base classes.

## BaseModel

Inherited by every table.

Contains:

- id (UUID Primary Key)
- created_at
- updated_at
- is_deleted

Purpose:

Provide common fields to every table.

---

## AuditModel

Inherited only by business entities.

Contains:

- created_by
- updated_by
- deleted_at

Purpose:

Track who created and modified records.

Not every table requires audit fields.

---

# 2. Table Naming

Always use plural snake_case.

Examples

organizations

users

roles

permissions

datasets

dashboards

reports

notifications

Never use:

Organization

tbl_organization

OrganizationTable

organization_master

---

# 3. Primary Keys

Every table uses UUID.

Never use INTEGER.

Never use BIGINT.

Example

id

UUID

Primary Key

Generated automatically.

---

# 4. Foreign Keys

Always reference UUID.

Example

organization_id

user_id

role_id

Never reference names.

---

# 5. Timestamp Fields

Every table contains

created_at

updated_at

Automatically maintained.

---

# 6. Soft Delete

Every business table supports soft delete.

Fields

is_deleted

deleted_at (AuditModel only)

Records should never be physically deleted unless required.

---

# 7. Enum Usage

Do not store business statuses as unrestricted VARCHAR.

Use Python Enum + SQLAlchemy Enum.

Examples

OrganizationStatus

SubscriptionPlan

UserStatus

DatasetStatus

ForecastStatus

NotificationType

---

# 8. Relationships

Always define both sides.

Example

Organization.users

User.organization

Use back_populates.

Avoid one-way relationships.

---

# 9. Nullable Rules

Only make a field nullable when business logic requires it.

Never use nullable=True by default.

---

# 10. Indexes

Only add indexes to frequently queried columns.

Examples

email

slug

organization_id

status

created_at

Avoid indexing every column.

---

# 11. Unique Constraints

Use unique constraints for business identifiers.

Examples

organization.slug

user.email

role.name (per organization)

permission.code

---

# 12. Defaults

Prefer database defaults.

Examples

CURRENT_TIMESTAMP

FALSE

Enum defaults

Avoid Python defaults unless necessary.

---

# 13. Migration Rules

Every migration must:

Compile

Upgrade

Downgrade

Run on a clean database

Run on an existing database

Never edit old migrations.

Always create new ones.

---

# 14. Circular Dependencies

If two tables reference each other:

Create both tables first.

Add foreign keys in a later migration.

Do not force circular creation.

---

# 15. Model Review Checklist

Before merging any model:

✓ Naming follows standards

✓ UUID primary key

✓ Relationships complete

✓ Constraints added

✓ Indexes reviewed

✓ Migration generated

✓ Migration reviewed

✓ Migration tested

✓ Neon migration successful

✓ Swagger unaffected

Only after passing all checks may the model be committed.