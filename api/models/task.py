from sqlalchemy import Column, Integer, String, Text, ForeignKey
from .base import Base

class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String, nullable=False, default='New')

    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))