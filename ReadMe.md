# FastApi+mysql 快速搭建web后端接口框架

## 项目地址：
https://github.com/zhongzhongBaby/FastapiMysqlDemo

## 项目描述：
最近从java转来学习FastApi，想要快速搭建一个FastApi+mysql的后端接口框架，但是网上没有找到demo，所以自己简单写了一个，做了一些简单的封装，希望对和我一样的新学者有所帮助。<br>

## 功能涵盖：
1.使用数据源访问mysql<br>
2.实现中文api文档<br>
3.请求参数数据验证<br>
4.使用jwt实现Token登录验证<br>
5.不同环境（生产、测试），配置环境参数<br>


### 1.数据源访问工具类

```
import pymysql
from DBUtils.PooledDB import PooledDB


class MySQLHelper(object):
    def __init__(self, host, port, dbuser, password, database):
        self.pool = PooledDB(
            creator=pymysql,  # 使用链接数据库的模块
            maxconnections=6,  # 连接池允许的最大连接数，0和None表示不限制连接数
            mincached=2,  # 初始化时，链接池中至少创建的空闲的链接，0表示不创建
            maxcached=5,  # 链接池中最多闲置的链接，0和None不限制
            maxshared=3,
            # 链接池中最多共享的链接数量，0和None表示全部共享。PS: 无用，因为pymysql和MySQLdb等模块的 threadsafety都为1，所有值无论设置为多少，_maxcached永远为0，所以永远是所有链接都共享。
            blocking=True,  # 连接池中如果没有可用连接后，是否阻塞等待。True，等待；False，不等待然后报错
            maxusage=None,  # 一个链接最多被重复使用的次数，None表示无限制
            setsession=[],  # 开始会话前执行的命令列表。如：["set datestyle to ...", "set time zone ..."]
            ping=0,
            # ping MySQL服务端，检查是否服务可用。# 如：0 = None = never, 1 = default = whenever it is requested, 2 = when a cursor is created, 4 = when a query is executed, 7 = always
            host=host,
            port=int(port),
            user=dbuser,
            password=password,
            database=database,
            charset='utf8'
        )

    def create_conn_cursor(self):
        conn = self.pool.connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        return conn, cursor

    def fetch_one(self, sql):
        conn, cursor = self.create_conn_cursor()
        cursor.execute(sql)
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result

    def fetch_all(self, sql, args):
        conn, cursor = self.create_conn_cursor()
        cursor.execute(sql, args)
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return result

    def fetch_all2(self, sql):
        conn, cursor = self.create_conn_cursor()
        cursor.execute(sql)
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return result

    def insert_one(self, sql, args):
        conn, cursor = self.create_conn_cursor()
        res = cursor.execute(sql, args)
        conn.commit()
        print(res)
        conn.close()
        return res

    def update(self, sql, args):
        conn, cursor = self.create_conn_cursor()
        res = cursor.execute(sql, args)
        conn.commit()
        print(res)
        conn.close()
        return res


sql_helper = MySQLHelper("127.0.0.1", 3306, "root", "123456", "demo")


```



### 2.api文档实现效果
![image](1.png)




### 3.请求参数数据验证

```
//使用pydantic.Field方法数据验证
class FindCourseListRequest(FindRequestBase):
    course_id: str = Field(None, title="课程id", max_length=300)
    name: str = Field(None, title="名称", max_length=300)
    subject: str = Field(..., title="科目", max_length=300) 
```
以上是对参数的基本校验，如：参数类型，是否必传，参数长度等。
如果需要进行更多自定义的校验可以使用pydantic.@validator。



### 4.使用jwt实现Token登录验证

```
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

# 系统默认的登录用户,如果不去数据库进行验证用户信息，可在这儿配置
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


# 从数据库获取用户信息
def get_user_from_db(username):
    sql = "SELECT username,hashed_password, disabled FROM  sys_user where username = '%s' " % username
    user = sql_helper.fetch_one(sql)
    return user

```

访问login接口，登录成功，可以**返回token密文**

```
{
    "user_name": "Admin",
    "access_token": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJBZG1pbiIsImV4cCI6MTU4NzgwNTcxMH0.qwahQ22GaMGOpoE_xHr_Dg-i8VjO1bwEl2uJSz1ry6U",
    "token_type": "bearer2"
}
```

之后在**访问其他需要登录验证的接口**的时候，只需要在接口请求header上添加token密文参数

```
Authorization ：Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJBZG1pbiIsImV4cCI6MTU4NzgwNTcxMH0.qwahQ22GaMGOpoE_xHr_Dg-i8VjO1bwEl2uJSz1ry6U
```

**设置接口登录验证**只需要在接口方法上添加参数：<br>
current_user: User = Depends(get_current_active_user)

```
async def find_course_selective(current_user: User = Depends(get_current_active_user),
                                request: FindCourseListRequest = Body(None, title="课程筛选条件")):

```


### 5.不同环境（生产、测试），配置环境参数

新建几个环境参数文件：prod.env,test.env

```
from pydantic import BaseSettings
from functools import lru_cache


@lru_cache()
def get_settings():
    return Settings(_env_file='prod.env')


class Settings(BaseSettings):
    app_name: str = "FastApiMysqlDemo"
    admin_email: str = "844383583@qq.com"
    database: dict = {
        "url": "127.0.0.1",
        "port": 3306,
        "user": "root",
        "password": "12346",
        "database_name": "demo"
    }

    class Config:
        env_file = "prod.env"

```

**@lru_cache()目的**：因为环境参数要从文件中读取，这样存于内存可以避免IO次数。
**使用：**
```
import config
database = config.get_settings().database

sql_helper = MySQLHelper(database["url"], database["port"],
                         database["user"], database["password"], database["database_name"])

```


## 项目启动

```
- 项目启动

        uvicorn main:app --reload
        # 指定端口和主机
        uvicorn main:app --reload  --port 8000 --host 192.168.1.24
```














