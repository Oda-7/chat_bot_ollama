#!/bin/bash
set -e

echo "🚀 Initialisation de la base de données PostgreSQL..."

# Créer le superuser postgres si nécessaire
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    DO \$\$
    BEGIN
        IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'postgres') THEN
            CREATE ROLE postgres WITH SUPERUSER LOGIN PASSWORD 'postgres';
            RAISE NOTICE '✅ Superuser postgres créé';
        ELSE
            RAISE NOTICE 'ℹ️  Superuser postgres existe déjà';
        END IF;
    END
    \$\$;
    
    -- Activer l'extension pgvector
    CREATE EXTENSION IF NOT EXISTS vector;
    
    -- Grant permissions
    GRANT ALL PRIVILEGES ON DATABASE $POSTGRES_DB TO $POSTGRES_USER;
EOSQL

echo "✅ Database initialized successfully"