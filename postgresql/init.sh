#!/bin/sh

set -e

psql -U "${POSTGRES_USER}" <<-EOF
    -- WORKAROUND: Create a root user and database to silence errors
    -- FATAL: role "root" does not exist
    CREATE ROLE root WITH LOGIN PASSWORD NULL;
    -- FATAL:  database "root" does not exist
    CREATE DATABASE root WITH OWNER root;

    -- Create the zapier user
    CREATE ROLE ${ZAPIER_USER} WITH LOGIN PASSWORD '${ZAPIER_PASSWORD}';
EOF
