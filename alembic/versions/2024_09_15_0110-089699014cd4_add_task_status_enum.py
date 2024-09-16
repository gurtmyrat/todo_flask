from alembic import op
import sqlalchemy as sa
import enum

# Define Enum in Python
class TaskStatusEnum(enum.Enum):
    NEW = "NEW"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"

# Revision identifiers, used by Alembic.
revision = '089699014cd4'
down_revision = 'c2c8ed2655ff'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create Enum type in PostgreSQL if it doesn't exist
    task_status_enum = sa.Enum(TaskStatusEnum, name='taskstatus')
    task_status_enum.create(op.get_bind(), checkfirst=True)

    # Alter column to use the new Enum type with proper mapping
    op.execute("""
        ALTER TABLE tasks 
        ALTER COLUMN status 
        TYPE taskstatus 
        USING status::taskstatus
    """)

def downgrade() -> None:
    # Revert the status column to use VARCHAR instead of Enum
    op.alter_column('tasks', 'status', type_=sa.VARCHAR(), existing_nullable=False)

    # Drop the Enum type if it exists
    op.execute('DROP TYPE IF EXISTS taskstatus')
