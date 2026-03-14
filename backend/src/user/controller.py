from fastapi import HTTPException,status,Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from src.utils.settings import settings

from sqlalchemy.orm import Session
from src.user.dtos import UserSchema,UserResponseSchema
from src.user.models import UserModel
from src.user.dtos import LoginSchema
import jwt
from datetime import datetime,timedelta

password_hash = PasswordHash.recommended()

def get_password_hash(password):
    return password_hash.hash(password)

def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)

def register(body:UserSchema,db:Session):
    try:
        is_user = db.query(UserModel).filter(UserModel.username==body.username).first()
        if is_user:
            raise HTTPException(400,detail="Username already exist ")
        
        is_user = db.query(UserModel).filter(UserModel.email==body.email).first()
        if is_user:
            raise HTTPException(400,detail="Email Address already exist ")
        
        hash_password= get_password_hash(body.password)
        
        new_user = UserModel(
            name=body.name,
            username = body.username,
            hash_password = hash_password,
            email = body.email,
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return new_user
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"User registration failed: {str(e)}"
        )

def login_user(body:LoginSchema,db:Session):
    try:
        user = db.query(UserModel).filter(UserModel.username==body.username).first()
        if not user:
            raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED,detail="Invalid credentials ")
        
        if not verify_password(body.password,user.hash_password):
            raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED,detail="Invalid credentials ")
        
        exp_time = datetime.now()+timedelta(minutes=settings.EXP_TIME)
        # print(exp_time)
        # token is created by encoding ,id,exp,seckey,algo
        token = jwt.encode({"_id":user.id,"exp":exp_time.timestamp()},
                        settings.SECRET_KEY,
                        settings.ALGORITHM
                        )
            
        return {
            "Token":token
        }
    except Exception as e:
        raise HTTPException(500,str(e))
    
# token send 
def is_authenticated(request:Request,db:Session):
    try:
        token = request.headers.get("authorization")
        if not token:
            raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED,detail="you are unauthorised")
        
        token = token.split(" ")[-1]
        # print(token)
        
        data = jwt.decode(token,settings.SECRET_KEY,settings.ALGORITHM)
        user_id = data.get("_id")
        exp_time = data.get("exp")
        
        user = db.query(UserModel).filter(UserModel.id==user_id).first()
        if not user:
            raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED,detail="you are unauthorised ")
        
        return user
        # jo id aur exp time bhja tha encode ke time decode hone ke baad whi return hoga 
    except InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="you are unauthorised ")