from pydantic import BaseModel
from typing import List, Optional


class User(BaseModel):
    name: str
    email: str
    password: str


class Blog(BaseModel):
    title: str
    body: str

    class Config:
        #orm_mode = True
        from_attributes = True

        
class ShowUser(BaseModel):
    name: str
    email: str
    blogs: List[Blog] = []

    class Config:
        #orm_mode = True
        from_attributes = True
        

class ShowBlog(BaseModel):
    title: str
    body: str

    class Config:
        #orm_mode = True
        from_attributes = True


class Login(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None