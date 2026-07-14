from datetime import datetime

from pydantic import BaseModel, Field


class LocationCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)


class LocationOut(BaseModel):
    id: int
    name: str


class PostCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    content: str = Field(min_length=1)
    category: str = Field(min_length=1, max_length=20)
    password: str = Field(min_length=1, max_length=50)
    location_id: int


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
    created_at: datetime


class PostOut(BaseModel):
    id: int
    title: str
    content: str
    category: str
    view_count: int
    created_at: datetime
    location_id: int
    comments: list[CommentOut] = Field(default_factory=list)
