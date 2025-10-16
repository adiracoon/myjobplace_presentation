"""Initial schema
Revision ID: 001
Revises:
Create Date: 2025-10-15
"""
from alembic import op
import sqlalchemy as sa
revision = '001'
down_revision = None
branch_labels = None
depends_on = None
def upgrade() -> None:
    op.create_table(
        'job',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('company', sa.String(length=200), nullable=False),
        sa.Column('url', sa.String(length=2000), nullable=True),
        sa.Column('source', sa.String(), nullable=True),
        sa.Column('org', sa.String(), nullable=True),
        sa.Column('external_id', sa.String(), nullable=True),
        sa.Column('location', sa.String(length=200), nullable=True),
        sa.Column('posted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_ext', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_demo', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_job_posted_at', 'job', ['posted_at'])
    op.create_index('ix_job_company_title', 'job', ['company', 'title'])
    op.create_index('ix_job_is_active', 'job', ['is_active'])
    op.create_index('ix_job_deleted_at', 'job', ['deleted_at'])
    op.execute("""
        CREATE UNIQUE INDEX uq_job_source_external
        ON job (source, external_id)
        WHERE source IS NOT NULL AND external_id IS NOT NULL
    """)
    op.create_table(
        'import_checkpoint',
        sa.Column('source', sa.String(length=50), nullable=False),
        sa.Column('org', sa.String(length=200), nullable=False),
        sa.Column('last_run_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('last_success_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('jobs_imported', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('jobs_updated', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('jobs_failed', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='success'),
        sa.PrimaryKeyConstraint('source', 'org')
    )
def downgrade() -> None:
    op.drop_table('import_checkpoint')
    op.execute('DROP INDEX IF EXISTS uq_job_source_external')
    op.drop_index('ix_job_deleted_at', table_name='job')
    op.drop_index('ix_job_is_active', table_name='job')
    op.drop_index('ix_job_company_title', table_name='job')
    op.drop_index('ix_job_posted_at', table_name='job')
    op.drop_table('job')
