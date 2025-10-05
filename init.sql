-- Script d'initialisation de la base de données avec support vectoriel
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "vector";  -- Extension pour les embeddings RAG

-- Les index seront créés par les migrations Alembic
-- Index pour améliorer les performances (seront créés après les tables)
-- CREATE INDEX IF NOT EXISTS idx_t7_users_username ON t7_users(username);
-- CREATE INDEX IF NOT EXISTS idx_t7_chat_sessions_user_id ON t7_chat_sessions(user_id);
-- CREATE INDEX IF NOT EXISTS idx_t7_chat_messages_session_id ON t7_chat_messages(session_id);
