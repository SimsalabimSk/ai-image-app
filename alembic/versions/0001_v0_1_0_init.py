from alembic import op
import sqlalchemy as sa

revision = '0001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'users',
        sa.Column('user_id', sa.String(), primary_key=True),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now())
    )

    op.create_table(
        'projects',
        sa.Column('project_id', sa.String(), primary_key=True),
        sa.Column('user_id', sa.String(), sa.ForeignKey('users.user_id')),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now())
    )

    op.create_table(
        'intents',
        sa.Column('intent_id', sa.String(), primary_key=True),
        sa.Column('project_id', sa.String(), sa.ForeignKey('projects.project_id')),
        sa.Column('task_type', sa.String(), nullable=False),
        sa.Column('intent_text', sa.Text(), nullable=False),
        sa.Column('intent_spec_json', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now())
    )

    op.create_table(
        'runs',
        sa.Column('run_id', sa.String(), primary_key=True),
        sa.Column('project_id', sa.String(), sa.ForeignKey('projects.project_id')),
        sa.Column('intent_id', sa.String(), sa.ForeignKey('intents.intent_id')),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('mode', sa.String(), nullable=False),
        sa.Column('policy_profile', sa.String(), nullable=False),
        sa.Column('orchestration_plan_json', sa.JSON(), nullable=False),
        sa.Column('latest_temp_asset_id', sa.String(), nullable=True),
        sa.Column('error_code', sa.String(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now())
    )

    op.create_table(
        'assets',
        sa.Column('asset_id', sa.String(), primary_key=True),
        sa.Column('run_id', sa.String(), sa.ForeignKey('runs.run_id')),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('mime_type', sa.String(), nullable=False),
        sa.Column('storage_provider', sa.String(), nullable=False),
        sa.Column('storage_bucket', sa.String(), nullable=False),
        sa.Column('storage_key', sa.String(), nullable=False),
        sa.Column('sha256', sa.String(), nullable=False),
        sa.Column('size_bytes', sa.Integer(), nullable=False),
        sa.Column('is_temp', sa.Boolean(), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now())
    )

    op.create_table(
        'events',
        sa.Column('event_id', sa.String(), primary_key=True),
        sa.Column('run_id', sa.String(), sa.ForeignKey('runs.run_id')),
        sa.Column('ts', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('event_type', sa.String(), nullable=False),
        sa.Column('run_mode', sa.String(), nullable=False),
        sa.Column('novelty_tier', sa.String(), nullable=False),
        sa.Column('feasibility_status', sa.String(), nullable=False),
        sa.Column('frontier_target', sa.String(), nullable=True),
        sa.Column('payload_json', sa.JSON(), nullable=True),
    )

    op.create_index('ix_events_run_ts', 'events', ['run_id', 'ts'])
    op.create_index('ix_assets_run', 'assets', ['run_id'])

def downgrade():
    op.drop_index('ix_assets_run', table_name='assets')
    op.drop_index('ix_events_run_ts', table_name='events')
    op.drop_table('events')
    op.drop_table('assets')
    op.drop_table('runs')
    op.drop_table('intents')
    op.drop_table('projects')
    op.drop_table('users')
