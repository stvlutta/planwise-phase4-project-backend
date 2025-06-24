"""Add password hash to users

Revision ID: e55f4ad7d449
Revises: 6437ca4377c0
Create Date: 2025-06-23 00:45:44.722482

# revision identifiers, used by Alembic.
revision = 'e55f4ad7d449'
down_revision = '6437ca4377c0'
branch_labels = None
depends_on = None

"""
from alembic import op
import sqlalchemy as sa 