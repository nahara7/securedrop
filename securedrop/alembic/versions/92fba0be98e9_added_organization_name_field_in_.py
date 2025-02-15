"""Added organization_name field in instance_config table

Revision ID: 92fba0be98e9
Revises: 48a75abc0121
Create Date: 2020-11-15 19:36:20.351993

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '92fba0be98e9'
down_revision = '48a75abc0121'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('instance_config', schema=None) as batch_op:
        batch_op.add_column(sa.Column('organization_name', sa.String(length=255), nullable=True))

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('instance_config', schema=None) as batch_op:
        batch_op.drop_column('organization_name')

    # ### end Alembic commands ###
