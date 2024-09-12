from typing import Optional
from pydantic import BaseModel, constr

class TaskInSchema(BaseModel):
    title: constr(min_length=1, max_length=255)
    description: Optional[str] = None
    status: constr(min_length=1, max_length=50)

class TaskOutSchema(TaskInSchema):
    id: int
    user_id: int

    class Config:
        from_attributes = True
