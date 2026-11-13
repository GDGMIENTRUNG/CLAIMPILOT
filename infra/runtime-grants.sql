-- Run in the target database, as migration owner/admin, AFTER migration0005.
-- Roles must already exist. Passwords are set interactively outside this file.
-- claimpilot_migrator owns the tables; app never uses that credential.
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM claimpilot_runtime;
GRANT USAGE ON SCHEMA public TO claimpilot_runtime;
GRANT SELECT, INSERT, UPDATE ON
    complaints, case_messages, text_analysis_runs, complaint_decisions,
    case_replies, reply_operations, audit_events, evidence_assets,
    evidence_analyses, staff_sessions, integration_state, gmail_intake_failures
TO claimpilot_runtime;
GRANT SELECT ON orders TO claimpilot_runtime;
REVOKE UPDATE ON audit_events, complaint_decisions FROM claimpilot_runtime;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO claimpilot_runtime;
-- No DELETE, DDL, alembic_version access or blanket future-table grants.
