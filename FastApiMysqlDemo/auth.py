from datetime import datetime, timedelta
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt import *
from passlib.context import CryptContext
from pydantic import BaseModel
from utils.mysql_utils import sql_helper
from fastapi import APIRouter
from pydantic import Field

login_router = APIRouter()

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 会话超时时间 默认1天

# 系统默认的登录用户
fake_users_db = {
    "pxxAdmin": {
        "username": "pxxAdmin",
        "hashed_password": "$2b$12$Y26vyX0FkZHBq3T57GzdwOd4WxJDoHV0PckspBfKbZ4LkDPOc1A4y",
        "disabled": False,
    }
}


class Token(BaseModel):
    user_name: str = Field(None, description="token 类型")
    access_token: str = Field(..., description="访问token密文，其他接口访问时在header上加参数（Authorization:密文） ")
    token_type: str = Field(..., description="token 类型")


class TokenData(BaseModel):
    username: str = None


class User(BaseModel):
    username: str
    disabled: bool = None


class UserInDB(User):
    hashed_password: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db, username: str):
    user_dict = get_user_from_db(username)
    if user_dict is not None:
        return UserInDB(**user_dict)


def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(*, data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except PyJWTError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@login_router.post("/login", response_model=Token, summary="登录接口")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    '''
    默认账号  密码  pxxAdmin   123456

    '''
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"user_name": user.username, "access_token": "Bearer " + str(access_token, encoding="utf8"),
            "token_type": "bearer2"}


def get_user_from_db(username):
    sql = "SELECT username,hashed_password, disabled FROM  sys_user where username = '%s' " % username
    user = sql_helper.fetch_one(sql)
    return user
