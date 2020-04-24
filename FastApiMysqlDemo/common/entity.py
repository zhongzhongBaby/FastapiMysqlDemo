from typing import List

from pydantic import BaseModel, Schema, Field


class FindRequestBase(BaseModel):
    limit: int = None
    page: int = None


class ResponseBase(BaseModel):
    code: int = 1000
    msg: str = "请求成功"
    data: dict = {}
