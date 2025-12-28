"""Add AI fields to documents and onboarding fields to users

Revision ID: 001
Revises: 
Create Date: 2025-01-30

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add AI fields to documents table
    op.add_column('documents', sa.Column('extracted_text', sa.Text(), nullable=True))
    op.add_column('documents', sa.Column('ai_validation_result', sa.Text(), nullable=True))
    op.add_column('documents', sa.Column('ai_confidence_score', sa.Float(), nullable=True))
    op.add_column('documents', sa.Column('ai_processed_at', sa.DateTime(), nullable=True))
    
    # Add onboarding fields to users table
    op.add_column('users', sa.Column('onboarding_status', sa.String(length=50), nullable=True, server_default='NOT_STARTED'))
    op.add_column('users', sa.Column('onboarding_started_at', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('onboarding_completed_at', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('onboarding_notes', sa.Text(), nullable=True))


def downgrade() -> None:
    # Remove AI fields from documents table
    op.drop_column('documents', 'ai_processed_at')
    op.drop_column('documents', 'ai_confidence_score')
    op.drop_column('documents', 'ai_validation_result')
    op.drop_column('documents', 'extracted_text')
    
    # Remove onboarding fields from users table
    op.drop_column('users', 'onboarding_notes')
    op.drop_column('users', 'onboarding_completed_at')
    op.drop_column('users', 'onboarding_started_at')
    op.drop_column('users', 'onboarding_status')
