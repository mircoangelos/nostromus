-- Create Keycloak user and database
CREATE USER keycloak WITH PASSWORD 'keycloakpass';

-- Create Keycloak database
CREATE DATABASE keycloak WITH OWNER keycloak ENCODING 'UTF8';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE keycloak TO keycloak;
GRANT ALL PRIVILEGES ON DATABASE nostromus TO nostromus;

-- Connect to keycloak DB and grant schema permissions
\c keycloak;
GRANT ALL ON SCHEMA public TO keycloak;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO keycloak;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO keycloak;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO keycloak;

-- Connect back to default
\c postgres;
