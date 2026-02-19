"""Phase 3B: Add billing and subscription tables

Revision ID: phase3b_billing
Revises: phase3a_security
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision = 'phase3b_billing'
down_revision = 'phase3a_security'
branch_labels = None
depends_on = None


def upgrade():
    """Add billing and subscription tables."""
    
    # 1. Add subscription fields to users table
    op.add_column('users', sa.Column('subscription_tier', sa.String(), nullable=False, server_default='FREE'))
    op.add_column('users', sa.Column('stripe_customer_id', sa.String(), nullable=True))
    op.add_column('users', sa.Column('trial_ends_at', sa.DateTime(), nullable=True))
    
    # Create indexes
    op.create_index('ix_users_subscription_tier', 'users', ['subscription_tier'])
    op.create_index('ix_users_stripe_customer_id', 'users', ['stripe_customer_id'], unique=True)
    
    # 2. Create subscriptions table
    op.create_table(
        'subscriptions',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False, index=True),
        sa.Column('tier', sa.String(), nullable=False, index=True),
        sa.Column('status', sa.String(), nullable=False, index=True),
        sa.Column('billing_interval', sa.String(), nullable=True),
        sa.Column('stripe_subscription_id', sa.String(), nullable=True, index=True),
        sa.Column('stripe_price_id', sa.String(), nullable=True),
        sa.Column('stripe_current_period_start', sa.DateTime(), nullable=True),
        sa.Column('stripe_current_period_end', sa.DateTime(), nullable=True),
        sa.Column('stripe_cancel_at_period_end', sa.Boolean(), default=False),
        sa.Column('trial_start', sa.DateTime(), nullable=True),
        sa.Column('trial_end', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), default=datetime.utcnow, index=True),
        sa.Column('updated_at', sa.DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow),
        sa.Column('canceled_at', sa.DateTime(), nullable=True),
    )
    
    # Create unique constraint and index
    op.create_unique_constraint('uq_subscription_user', 'subscriptions', ['user_id'])
    op.create_index('ix_subscriptions_stripe_subscription_id', 'subscriptions', ['stripe_subscription_id'], unique=True)
    
    # 3. Create usage_tracking table
    op.create_table(
        'usage_tracking',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False, index=True),
        sa.Column('month', sa.String(), nullable=False, index=True),
        sa.Column('analyses_used', sa.Integer(), nullable=False, default=0),
        sa.Column('analyses_limit', sa.Integer(), nullable=False),
        sa.Column('total_lines_analyzed', sa.Integer(), nullable=False, default=0),
        sa.Column('total_findings_generated', sa.Integer(), nullable=False, default=0),
        sa.Column('created_at', sa.DateTime(), default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow),
    )
    
    # Create unique constraint and composite index
    op.create_unique_constraint('uq_user_month_usage', 'usage_tracking', ['user_id', 'month'])
    op.create_index('idx_usage_user_month', 'usage_tracking', ['user_id', 'month'])
    
    # 4. Create default FREE subscriptions for existing users
    op.execute("""
        INSERT INTO subscriptions (user_id, tier, status, created_at, updated_at)
        SELECT id, 'FREE', 'ACTIVE', NOW(), NOW()
        FROM users
        WHERE id NOT IN (SELECT user_id FROM subscriptions);
    """)


def downgrade():
    """Remove billing and subscription tables."""
    
    # Drop tables
    op.drop_table('usage_tracking')
    op.drop_table('subscriptions')
    
    # Remove columns from users table
    op.drop_index('ix_users_stripe_customer_id', 'users')
    op.drop_index('ix_users_subscription_tier', 'users')
    op.drop_column('users', 'trial_ends_at')
    op.drop_column('users', 'stripe_customer_id')
    op.drop_column('users', 'subscription_tier')
