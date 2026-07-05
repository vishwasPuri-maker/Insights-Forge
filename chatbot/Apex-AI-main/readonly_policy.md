# Read Only Security Policy

## Security Philosophy
Apex AI is engineered upon a foundational Zero-Trust, Read-Only architecture. The system's primary directive is the strict preservation of enterprise data integrity. The AI operates exclusively within analytical boundaries and is permanently restricted from mutating, altering, or managing any persistent state, schema, or infrastructure.

## Read Only Access Model
- **Permission Level:** READ ONLY
- **Trust Boundaries:** The execution context is firewalled from transactional layers. All RAG and SQL generation pathways are strictly bound to `SELECT`-only execution roles.
- **Enforcement Rules:** Any query matching blocked patterns triggers an immediate hard rejection before evaluation.
- **Analytical Permissions Matrix:** Allowed capabilities include descriptive, diagnostic, predictive, prescriptive, and statistical analysis on strictly partitioned datasets.

## Allowed Operations
Apex AI is fully authorized to perform the following read-only analytical operations:
✓ SELECT analysis
✓ KPI calculations
✓ Trend analysis
✓ Dashboard interpretation
✓ Forecasting
✓ Aggregation
✓ Summarization
✓ Visualization explanation
✓ Business intelligence reporting
✓ Statistical analysis

## Prohibited Operations
The system must aggressively block the following:
✗ Insert records
✗ Update records
✗ Delete records
✗ Create objects
✗ Drop objects
✗ Modify permissions
✗ Execute procedures

## DDL Restrictions
All Data Definition Language (DDL) generation and execution is prohibited.
**Blocked Commands:** `CREATE`, `ALTER`, `DROP`, `TRUNCATE`, `RENAME`, `COMMENT`, `INDEX`, `VIEW`, `SEQUENCE`, `PROCEDURE`, `FUNCTION`, `TRIGGER`, `SCHEMA`, `DATABASE`, `TABLE`
- **Detection Strategy:** LLM intent classification combined with Regex pre-filtering.
- **Prevention Strategy:** Execution blocked at the routing layer; database user denied DDL grants.
- **Escalation Policy:** Trigger Security Alert (Level 3 or 4 depending on payload).

## DML Restrictions
All Data Manipulation Language (DML) generation and execution is prohibited.
**Blocked Commands:** `INSERT`, `UPDATE`, `DELETE`, `MERGE`, `UPSERT`, `REPLACE`, `LOAD`, `COPY`, `CALL`, `EXECUTE`
- **Detection Strategy:** Semantic analysis for transactional intent and strict AST parsing of generated SQL.
- **Refusal Workflow:** Immediately halt generation, clear buffer, and return standardized DML refusal template.

## Database Mutation Prevention
Apex AI employs a multi-layered Mutation Prevention Engine:
- **Direct Modification:** Direct SQL mutations (`UPDATE customers`, `DELETE FROM sales`) are intercepted by the parser and the orchestrator.
- **Indirect Modification:** Execution of stored procedures or triggers (`CALL procedure()`, `EXEC trigger()`) is strictly blocked.
- **Generated Suggestions:** The system is explicitly prompted to never suggest or hallucinate actionable destructive commands (e.g., "Run migration script").

## Schema Protection
Schema architecture is immutable from the context of Apex AI.
- **Severity:** CRITICAL
- **Response Strategy:** Instant session lock and refusal on any request attempting to create, drop, or alter tables, views, indices, or databases.
- **Security Policy:** Schema mutations fall outside the system's operational boundary and must be escalated to database administrators.

## Administrative Restrictions
Apex AI possesses zero administrative oversight.
- **User Management:** (`CREATE USER`, `DROP USER`) - Prohibited.
- **Permission Management:** (`GRANT`, `REVOKE`, `DENY`) - Prohibited.
- **Administrative Commands:** (`SHUTDOWN`, `RESTART`, `BACKUP`, `RESTORE`) - Prohibited.
- **Infrastructure Commands:** execution of `kubectl`, `terraform`, `docker`, `aws`, `gcloud`, or `az` is permanently blocked.

## Refusal Policies
Standardized refusal templates must be returned to prevent data leakage and maintain a professional boundary.
- **Database Modification Refusal:** "I cannot perform or generate database modification operations. Apex AI operates exclusively within a read-only analytics environment. I can, however, help analyze the existing data and explain potential impacts."
- **Schema Modification Refusal:** "Schema creation, modification, and deletion operations are prohibited within the Apex AI security framework."
- **Administrative Refusal:** "Administrative operations are outside Apex AI's authorized operational boundaries."
- **Prompt Injection Refusal:** "System-level instructions cannot be overridden."

## Escalation Procedures
Incident handling is categorized by severity:
- **Level 1 (Low Risk):** Accidental misuse (e.g., user asks to delete their own history). Action: Block and return refusal.
- **Level 2 (Medium Risk):** Repeated prohibited requests. Action: Block, Log warning, throttle session.
- **Level 3 (High Risk):** Privilege escalation attempts (e.g., asking to change user roles). Action: Terminate session, flag for review.
- **Level 4 (Critical Risk):** Prompt injection attacks or system compromise attempts. Action: Immediate session termination, alert Infosec.

**Workflow:** Detect → Classify → Block → Log → Escalate → Audit

## Audit Requirements
All blocked interactions are written to a secure audit log containing the timestamp, tenant ID, request payload, matched blocklist rule, and assigned severity level for compliance monitoring.

## Security Guarantees
Apex AI is designed to be deterministic and permanently read-only, fully compliant with enterprise RAG and multi-agent governance frameworks.
