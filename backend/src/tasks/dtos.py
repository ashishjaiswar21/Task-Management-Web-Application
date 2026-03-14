from pydantic import BaseModel


class TaskSchema(BaseModel):
    title:str
    desc:str
    is_completed:bool =False
    
class TaskResponseSchema(BaseModel):
    id:int
    title:str
    desc:str
    is_completed:bool =False
    user_id:int|None=None