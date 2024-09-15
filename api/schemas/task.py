from typing import Optional
from pydantic import BaseModel, constr
from enum import Enum

class TaskStatusEnum(str, Enum):
    NEW = "NEW"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"


class TaskInSchema(BaseModel):
    title: constr(min_length=1, max_length=255)
    description: Optional[str] = None
    status: TaskStatusEnum

class TaskOutSchema(TaskInSchema):
    id: int
    user_id: int

    class Config:
        from_attributes = True
