from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timedelta
from jose import JWTError, jwt
from core.config import SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES, TEST_USERNAME, TEST_PASSWORD
from core.response import success, error
from db.models import LoginRequest

router = APIRouter()

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return encoded_jwt

async def get_current_user(token: str = Depends()):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return username
    except JWTError:
        raise credentials_exception

@router.post("/login")
def login(request: LoginRequest):
    if request.username == TEST_USERNAME and request.password == TEST_PASSWORD:
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": request.username}, expires_delta=access_token_expires
        )
        return success({"token": access_token}, "登录成功")
    else:
        return error(401, "用户名或密码错误")