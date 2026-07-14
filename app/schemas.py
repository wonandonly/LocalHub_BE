from datetime import datetime

from pydantic import BaseModel, Field


class PostCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    content: str = Field(min_length=1)
    
    password: str = Field(min_length=1, max_length=50)


class PostUpdate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    content: str = Field(min_length=1)
    password: str = Field(min_length=1, max_length=50)


class PostDelete(BaseModel):
    password: str = Field(min_length=1, max_length=50)


class CommentCreate(BaseModel):
    content: str = Field(min_length=1)


class CommentOut(BaseModel):
    id: int
    content: str
    created_at: str


class PostOut(BaseModel):
    id: int
    title: str
    content: str
    
    view_count: int
    created_at: str
    comments: list[CommentOut] = Field(default_factory=list)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)


class ChatResponse(BaseModel):
    reply: str
