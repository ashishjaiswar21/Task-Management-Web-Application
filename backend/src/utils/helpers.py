from fastapi import HTTPException,status,Request,Depends

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from src.utils.settings import settings
from sqlalchemy.orm import Session
from src.user.models import UserModel
import jwt
from datetime import datetime,timedelta
from src.utils.db import get_db


def is_authenticated(request:Request,db:Session=Depends(get_db)):
    try:
        token = request.headers.get("Authorization")
        if not token:
            raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED,detail="you are unauthorised")
        
        token = token.split(" ")[-1]
        # print(token)
        
        data = jwt.decode(token,settings.SECRET_KEY,algorithms=[settings.ALGORITHM])
        user_id = data.get("_id")
        exp_time = data.get("exp")
        
        user = db.query(UserModel).filter(UserModel.id==user_id).first()
        if not user:
            raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED,detail="you are unauthorised ")
        
        return user
        # jo id aur exp time bhja tha encode ke time decode hone ke baad whi return hoga 
    except InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="you are unauthorised ")