"""add_today_pickup_tables

Revision ID: 3a1b4c5d6e7f
Revises: 2d2a94c72f62
Create Date: 2024-01-01 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '3a1b4c5d6e7f'
down_revision = '2d2a94c72f62'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create deliveries table
    op.create_table('deliveries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('invoice_number', sa.String(), nullable=True),
        sa.Column('sender_name', sa.String(), nullable=True),
        sa.Column('sender_phone', sa.String(), nullable=True),
        sa.Column('sender_zipcode', sa.String(), nullable=True),
        sa.Column('sender_address1', sa.String(), nullable=True),
        sa.Column('sender_address2', sa.String(), nullable=True),
        sa.Column('receiver_name', sa.String(), nullable=True),
        sa.Column('receiver_phone', sa.String(), nullable=True),
        sa.Column('receiver_zipcode', sa.String(), nullable=True),
        sa.Column('receiver_address1', sa.String(), nullable=True),
        sa.Column('receiver_address2', sa.String(), nullable=True),
        sa.Column('product_name', sa.String(), nullable=True),
        sa.Column('product_quantity', sa.Integer(), nullable=True),
        sa.Column('payment_type', sa.String(), nullable=True),
        sa.Column('collect_amount', sa.Integer(), nullable=True),
        sa.Column('delivery_memo', sa.Text(), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('delivery_date', sa.String(), nullable=True),
        sa.Column('is_flex', sa.Boolean(), nullable=True),
        sa.Column('external_response', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_deliveries_id'), 'deliveries', ['id'], unique=False)
    op.create_index(op.f('ix_deliveries_invoice_number'), 'deliveries', ['invoice_number'], unique=True)

    # Create delivery_trackings table
    op.create_table('delivery_trackings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('invoice_number', sa.String(), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('status_message', sa.String(), nullable=True),
        sa.Column('tracking_date', sa.DateTime(), nullable=True),
        sa.Column('location', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_delivery_trackings_id'), 'delivery_trackings', ['id'], unique=False)
    op.create_index(op.f('ix_delivery_trackings_invoice_number'), 'delivery_trackings', ['invoice_number'], unique=False)

    # Create return_deliveries table
    op.create_table('return_deliveries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('return_invoice_number', sa.String(), nullable=True),
        sa.Column('original_invoice_number', sa.String(), nullable=True),
        sa.Column('sender_name', sa.String(), nullable=True),
        sa.Column('sender_phone', sa.String(), nullable=True),
        sa.Column('sender_zipcode', sa.String(), nullable=True),
        sa.Column('sender_address1', sa.String(), nullable=True),
        sa.Column('sender_address2', sa.String(), nullable=True),
        sa.Column('receiver_name', sa.String(), nullable=True),
        sa.Column('receiver_phone', sa.String(), nullable=True),
        sa.Column('receiver_zipcode', sa.String(), nullable=True),
        sa.Column('receiver_address1', sa.String(), nullable=True),
        sa.Column('receiver_address2', sa.String(), nullable=True),
        sa.Column('product_name', sa.String(), nullable=True),
        sa.Column('product_quantity', sa.Integer(), nullable=True),
        sa.Column('return_reason', sa.String(), nullable=True),
        sa.Column('return_memo', sa.Text(), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('return_date', sa.String(), nullable=True),
        sa.Column('external_response', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_return_deliveries_id'), 'return_deliveries', ['id'], unique=False)
    op.create_index(op.f('ix_return_deliveries_return_invoice_number'), 'return_deliveries', ['return_invoice_number'], unique=True)
    op.create_index(op.f('ix_return_deliveries_original_invoice_number'), 'return_deliveries', ['original_invoice_number'], unique=False)

    # Create return_trackings table
    op.create_table('return_trackings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('return_invoice_number', sa.String(), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('status_message', sa.String(), nullable=True),
        sa.Column('tracking_date', sa.DateTime(), nullable=True),
        sa.Column('location', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_return_trackings_id'), 'return_trackings', ['id'], unique=False)
    op.create_index(op.f('ix_return_trackings_return_invoice_number'), 'return_trackings', ['return_invoice_number'], unique=False)

    # Create agencies table
    op.create_table('agencies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('agency_id', sa.String(), nullable=True),
        sa.Column('agency_name', sa.String(), nullable=True),
        sa.Column('agency_token', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_agencies_id'), 'agencies', ['id'], unique=False)
    op.create_index(op.f('ix_agencies_agency_id'), 'agencies', ['agency_id'], unique=True)

    # Create postal_codes table
    op.create_table('postal_codes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('agency_id', sa.String(), nullable=True),
        sa.Column('postal_code', sa.String(), nullable=True),
        sa.Column('region_name', sa.String(), nullable=True),
        sa.Column('is_deliverable', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_postal_codes_id'), 'postal_codes', ['id'], unique=False)
    op.create_index(op.f('ix_postal_codes_agency_id'), 'postal_codes', ['agency_id'], unique=False)
    op.create_index(op.f('ix_postal_codes_postal_code'), 'postal_codes', ['postal_code'], unique=False)

    # Create delivery_assignments table
    op.create_table('delivery_assignments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('agency_id', sa.String(), nullable=True),
        sa.Column('invoice_number', sa.String(), nullable=True),
        sa.Column('delivery_date', sa.String(), nullable=True),
        sa.Column('assignment_status', sa.String(), nullable=True),
        sa.Column('completion_status', sa.String(), nullable=True),
        sa.Column('completion_date', sa.DateTime(), nullable=True),
        sa.Column('delivery_memo', sa.Text(), nullable=True),
        sa.Column('external_response', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_delivery_assignments_id'), 'delivery_assignments', ['id'], unique=False)
    op.create_index(op.f('ix_delivery_assignments_agency_id'), 'delivery_assignments', ['agency_id'], unique=False)
    op.create_index(op.f('ix_delivery_assignments_invoice_number'), 'delivery_assignments', ['invoice_number'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('delivery_assignments')
    op.drop_table('postal_codes')
    op.drop_table('agencies')
    op.drop_table('return_trackings')
    op.drop_table('return_deliveries')
    op.drop_table('delivery_trackings')
    op.drop_table('deliveries')