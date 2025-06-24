"""Initial migration with User, Task, Project, and ProjectCollaborator models

Revision ID: 6437ca4377c0
Revises: 
Create Date: 2025-06-23 00:19:44.607360

# revision identifiers, used by Alembic.
revision = '6437ca4377c0'
down_revision = None
branch_labels = None
depends_on = None

"""
from alembic import op
import sqlalchemy as sa
