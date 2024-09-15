"""Add task status enum

Revision ID: 089699014cd4
Revises: c2c8ed2655ff
Create Date: 2024-09-15 01:10:50.595678

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
import enum

# Define Enum in Python
class TaskStatusEnum(enum.Enum):
    NEW = "NEW"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"

# revision identifiers, used by Alembic.
revision: str = '089699014cd4'
down_revision: Union[str, None] = 'c2c8ed2655ff'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Create Enum type in PostgreSQL if it doesn't exist
    task_status_enum = sa.Enum(TaskStatusEnum, name='taskstatus')
    task_status_enum.create(op.get_bind(), checkfirst=True)

    # Alter column to use the new Enum type with proper mapping
    op.execute("""
        ALTER TABLE tasks 
        ALTER COLUMN status 
        TYPE taskstatus 
        USING CASE 
            WHEN status = 'New' THEN 'NEW'::taskstatus
            WHEN status = 'In Progress' THEN 'IN_PROGRESS'::taskstatus
            WHEN status = 'Completed' THEN 'COMPLETED'::taskstatus
        END
    """)

def downgrade() -> None:
    # Revert the status column to use VARCHAR instead of Enum
    op.alter_column('tasks', 'status', type_=sa.VARCHAR(), existing_nullable=False)

    # Drop the Enum type if it exists
    op.execute('DROP TYPE IF EXISTS taskstatus')
