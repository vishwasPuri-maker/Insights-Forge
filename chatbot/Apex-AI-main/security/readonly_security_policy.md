# Apex AI Read-Only Security Policy

## Core Mandate
Apex AI operates in a strictly read-only capacity. It is absolutely forbidden from generating, authorizing, or executing any commands that modify data, schemas, or infrastructure state.

## Database Restrictions (SQL)
The following operations are hard-blocked at the guardrail layer:
- `INSERT`
- `UPDATE`
- `DELETE`
- `DROP`
- `ALTER`
- `CREATE`
- `TRUNCATE`
- `MERGE`
- `EXECUTE`
- `GRANT`
- `REVOKE`

## Infrastructure Restrictions (Bash/CLI)
The following infrastructure and OS-level operations are hard-blocked:
- `kubectl`
- `docker`
- `sudo`
- `chmod`
- `rm`
- `systemctl`
- `ssh`
- `terraform`
- `ansible`

## Enforcement
Any attempt by a user to request these operations will result in a `SECURITY` refusal and immediate audit logging.
