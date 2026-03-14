from fastapi import HTTPException
from src.tasks.dtos import TaskSchema
from sqlalchemy.orm import Session
from src.tasks.models import TaskModel
from src.user.models import UserModel


# here we passing User:UserModel is loggedin user ,as only loggedin user can create,del,update,view/get

def create_task(body:TaskSchema,db:Session,user:UserModel):
    try:
        data= body.model_dump()
        new_task = TaskModel(title = data["title"],
                            desc=data["desc"],
                            is_completed=data["is_completed"],
                            user_id = user.id)
        db.add(new_task)
        db.commit()
        db.refresh(new_task)
        
        return new_task
    
    except Exception as e:
        db.rollback()
        raise HTTPException(500, f"Task creation failed: {str(e)}")


def get_task(db:Session,user:UserModel):
    tasks =db.query(TaskModel).filter(TaskModel.user_id==user.id).all()
    return tasks


def get_one_task(task_id:int,db:Session,user:UserModel):
    # get id use na ki filter ,filter for comparison 
    one_task = db.query(TaskModel).filter(TaskModel.id==task_id,
                                          TaskModel.user_id==user.id).first()
    if not one_task:
        raise HTTPException(404,detail="task id is not found")
    return one_task

    
def update_task(body:TaskSchema,task_id:int,db:Session,user:UserModel):
    try:
        one_task = db.query(TaskModel).filter(TaskModel.id==task_id,
                                            TaskModel.user_id==user.id).first()
        if not one_task:
            raise HTTPException(404,detail="task id is not found")
        
        # one_task.title = body.title
        # one_task.desc=body.desc
        # one_task.is_completed=body.is_completed
        
        body = body.model_dump()
        for field,value in body.items():
            setattr(one_task,field,value)
        
        db.add(one_task)
        db.commit()
        db.refresh(one_task)
        
        return one_task
    
    except Exception as e:
        db.rollback()
        raise HTTPException(500,str(e))
    
def delete_task(task_id:int,db:Session,user:UserModel):
    try:
        one_task = db.query(TaskModel).filter(TaskModel.id==task_id,
                                            TaskModel.user_id==user.id).first()
        if not one_task:
            raise HTTPException(404,detail="task id is not found")
        
        db.delete(one_task)
        db.commit()
        
        return None
    
    # Ya to pura operation success ho
    # Ya kuch bhi save na ho
    except Exception as e:
        db.rollback()
        raise HTTPException(500,str(e))
    
      
      