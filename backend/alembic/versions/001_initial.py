"""Initial migration - All tables in one file

Revision ID: 001_initial
Revises: 
Create Date: 2025-09-20 00:45:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = inspector.get_table_names()

    # Table utilisateurs
    if 't7_users' not in existing_tables:
        op.create_table(
            't7_users',
            sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
            sa.Column('username', sa.String(length=50), nullable=False),
            sa.Column('email', sa.String(length=100), nullable=False),
            sa.Column('hashed_password', sa.String(length=255), nullable=False),
            sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=True),
            sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
            sa.Column('updated_at', sa.DateTime(), onupdate=sa.text('now()'), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('username'),
            sa.UniqueConstraint('email')
        )
        op.create_index('idx_t7_users_username', 't7_users', ['username'], unique=False)
        op.create_index('idx_t7_users_email', 't7_users', ['email'], unique=False)

    # Table sessions de chat
    if 't7_chat_sessions' not in existing_tables:
        op.create_table(
            't7_chat_sessions',
            sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
            sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('title', sa.String(length=200), server_default='Nouvelle conversation', nullable=True),
            sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=True),
            sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
            sa.ForeignKeyConstraint(['user_id'], ['t7_users.id']),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index('idx_t7_chat_sessions_user_id', 't7_chat_sessions', ['user_id'], unique=False)
        op.create_index('idx_t7_chat_sessions_created_at', 't7_chat_sessions', ['created_at'], unique=False)

    # Table messages
    if 't7_chat_messages' not in existing_tables:
        op.create_table(
            't7_chat_messages',
            sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
            sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('message_type', sa.String(length=20), nullable=False),
            sa.Column('content', sa.Text(), nullable=False),
            sa.Column('llm_used', sa.String(length=50), nullable=True),
            sa.Column('tokens_used', sa.Integer(), nullable=True),
            sa.Column('response_time', sa.Integer(), nullable=True),
            sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
            sa.Column('rag_sources', sa.JSON(), nullable=True),
            sa.ForeignKeyConstraint(['session_id'], ['t7_chat_sessions.id']),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index('idx_t7_chat_messages_session_id', 't7_chat_messages', ['session_id'], unique=False)
        op.create_index('idx_t7_chat_messages_created_at', 't7_chat_messages', ['created_at'], unique=False)

    # Table documents RAG
    if 't7_documents' not in existing_tables:
        op.create_table(
            't7_documents',
            sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
            sa.Column('filename', sa.String(length=255), nullable=False),
            sa.Column('content', sa.Text(), nullable=False),
            sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('status', sa.String(length=50), nullable=True),
            sa.Column('content_preview', sa.Text(), nullable=True),
            sa.Column('chunk_count', sa.Integer(), nullable=True),
            sa.Column('file_size', sa.Integer(), nullable=True), 
            sa.Column('is_processed', sa.Boolean(), server_default=sa.text('false'), nullable=True),
            sa.Column('uploaded_by', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
            sa.ForeignKeyConstraint(['uploaded_by'], ['t7_users.id']),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index('idx_t7_documents_uploaded_by', 't7_documents', ['uploaded_by'], unique=False)
        op.create_index('idx_t7_documents_created_at', 't7_documents', ['created_at'], unique=False)
        
    if 't7_document_chunks' not in existing_tables:
        op.create_table(
            't7_document_chunks',
            sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
            sa.Column('document_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('chunk_index', sa.Integer(), nullable=False),
            sa.Column('content', sa.Text(), nullable=False),
            sa.Column('embedding', sa.ARRAY(sa.Float()), nullable=True),  
            sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
            sa.Column('token_count', sa.Integer(), nullable=True),
            sa.ForeignKeyConstraint(['document_id'], ['t7_documents.id']),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index('idx_t7_document_chunks_document_id', 't7_document_chunks', ['document_id'], unique=False) 

def downgrade():
    op.drop_index('idx_t7_documents_created_at', table_name='t7_documents')
    op.drop_index('idx_t7_documents_uploaded_by', table_name='t7_documents')
    op.drop_index('idx_t7_chat_messages_created_at', table_name='t7_chat_messages')
    op.drop_index('idx_t7_chat_messages_session_id', table_name='t7_chat_messages')
    op.drop_index('idx_t7_chat_sessions_created_at', table_name='t7_chat_sessions')
    op.drop_index('idx_t7_chat_sessions_user_id', table_name='t7_chat_sessions')
    op.drop_index('idx_t7_users_email', table_name='t7_users')
    op.drop_index('idx_t7_users_username', table_name='t7_users')
    op.drop_table('t7_documents')
    op.drop_table('t7_chat_messages')
    op.drop_table('t7_chat_sessions')
    op.drop_table('t7_users')
    if 't7_document_chunks' not in existing_tables:
        op.create_index('ix_t7_document_chunks_document_id', 't7_document_chunks', ['document_id'])
    
    if 't7_chat_messages' not in existing_tables:
        op.create_table('t7_chat_messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('message_type', sa.String(length=20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('llm_used', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['session_id'], ['t7_chat_sessions.id'], ),
        sa.PrimaryKeyConstraint('id')
        )
        op.create_index('idx_t7_chat_messages_session_id', 't7_chat_messages', ['session_id'], unique=False)
        op.create_index('idx_t7_chat_messages_created_at', 't7_chat_messages', ['created_at'], unique=False)
        print("Table t7_chat_messages créée")
    else:
        print("Table t7_chat_messages existe déjà, ignorée")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('idx_t7_chat_messages_created_at', table_name='t7_chat_messages')
    op.drop_index('idx_t7_chat_messages_session_id', table_name='t7_chat_messages')
    op.drop_index('idx_t7_document_chunks_document_id', table_name='t7_document_chunks')
    op.drop_table('t7_document_chunks')
    op.drop_table('t7_documents')
    op.drop_index('idx_t7_chat_sessions_user_id', table_name='t7_chat_sessions')
    op.drop_index('idx_t7_chat_sessions_created_at', table_name='t7_chat_sessions')
    op.drop_table('t7_chat_sessions')
    op.drop_index('idx_t7_users_username', table_name='t7_users')
    op.drop_index('idx_t7_users_email', table_name='t7_users')
    op.drop_table('t7_users')
    
    # Désactiver l'extension pgvector (optionnel)
    # op.execute("DROP EXTENSION IF EXISTS vector;")
    # ### end Alembic commands ###
    # Désactiver l'extension pgvector (optionnel)
    # op.execute("DROP EXTENSION IF EXISTS vector;")
    # ### end Alembic commands ###
    # op.execute("DROP EXTENSION IF EXISTS vector;")
    # ### end Alembic commands ###
    # Désactiver l'extension pgvector (optionnel)
    # op.execute("DROP EXTENSION IF EXISTS vector;")
    # ### end Alembic commands ###
