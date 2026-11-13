-- Run as the Cloud SQL admin in database claimpilot, through a loopback
-- Cloud SQL Auth Proxy + psql. Then set passwords with psql \password prompts.
-- Do not create the runtime login with gcloud sql users create: its default
-- role memberships are broader than this application's DML-only requirement.
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'claimpilot_migrator') THEN
        CREATE ROLE claimpilot_migrator LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'claimpilot_runtime') THEN
        CREATE ROLE claimpilot_runtime LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT;
    END IF;
END
$$;
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
GRANT CONNECT ON DATABASE claimpilot TO claimpilot_migrator, claimpilot_runtime;
GRANT USAGE, CREATE ON SCHEMA public TO claimpilot_migrator;
-- After migration0005 run runtime-grants.sql as migration owner/admin.
