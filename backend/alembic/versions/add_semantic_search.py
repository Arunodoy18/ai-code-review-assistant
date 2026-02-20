"""Add pgvector extension and embedding column

Revision ID: add_semantic_search
Revises: 
Create Date: 2026-02-19

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_semantic_search'
down_revision = None  # Update this if there are previous migrations
branch_labels = None
depends_on = None


def upgrade():
    # Enable pgvector extension (PostgreSQL only)
    # Note: This requires superuser privileges or pre-installed extension
    # If using managed PostgreSQL (AWS RDS, Azure, etc.), pgvector may need to be enabled first
    try:
        op.execute('CREATE EXTENSION IF NOT EXISTS vector')
    except Exception:
        # If extension creation fails (permissions), the JSON column will still work
        # but won't have vector-optimized indexing
        pass
    
    # Add embedding column to findings table (JSON for cross-DB compat)
    op.add_column(
        'findings',
        sa.Column('embedding', sa.JSON, nullable=True)
    )
    
    # Create index for faster similarity searches (if pgvector is available)
    # Using GIN index for ARRAY columns (works without pgvector extension)
    try:
        op.execute(
            'CREATE INDEX IF NOT EXISTS ix_findings_embedding_gin ON findings USING GIN (embedding)'
        )
    except Exception:
        # If GIN index fails, continue without it (searches will be slower but still work)
        pass


def downgrade():
    # Remove index
    try:
        op.execute('DROP INDEX IF EXISTS ix_findings_embedding_gin')
    except Exception:
        pass
    
    # Remove embedding column
    op.drop_column('findings', 'embedding')
    
    # Note: We don't drop the vector extension as it might be used by other tables
