from fastapi import APIRouter,Depends,status,Request
from sqlalchemy.orm import Session
from src.utils.db import get_db
from src.user.dtos import UserSchema,UserResponseSchema,LoginSchema
from src.user.models import UserModel
from src.user import controller

user_routes = APIRouter(prefix="/user")

@user_routes.post("/register",response_model=UserResponseSchema,status_code=status.HTTP_201_CREATED)
def register(body:UserSchema,db:Session = Depends(get_db)):
    return controller.register(body,db)

# login me kya kare data get kare ya post kar ? 
@user_routes.post("/login",status_code=status.HTTP_200_OK)
def login(body:LoginSchema,db:Session=Depends(get_db)):
    return controller.login_user(body,db)


# request bodey ke header me token hota hai 

# reuest contains ->It contains all the information sent by the client:
# headers
# cookies
# body
# query params
# authorization token
# request method
# request URL

@user_routes.get("/is_auth",response_model=UserResponseSchema,status_code=status.HTTP_200_OK)
def is_auth(request:Request,db:Session=Depends(get_db)):
    return controller.is_authenticated(request,db)
  





