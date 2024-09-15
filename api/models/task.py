from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum
from .base import Base
import enum

class TaskStatusEnum(enum.Enum):
    NEW = "NEW"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"

class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(TaskStatusEnum), nullable=False, default=TaskStatusEnum.NEW)

    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
