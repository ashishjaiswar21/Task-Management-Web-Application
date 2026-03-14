from fastapi import FastAPI
from src.utils.db import Base,engine
from src.tasks.models import TaskModel
from src.tasks.router import task_routes
from src.user.router import user_routes

# alt+shift+v for view after frefresh in psotgresql

Base.metadata.create_all(engine)

app = FastAPI(title ="this is my Task App")
app.include_router(task_routes)
app.include_router(user_routes)

