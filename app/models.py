from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime, timezone, timedelta

# Define the KST timezone
KST = timezone(timedelta(hours=9))

Base = declarative_base()


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    password = Column(String(50), nullable=False, default="")
    view_count = Column(Integer, nullable=False, default=0)
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(KST).replace(tzinfo=None),
        nullable=False
    )

    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(KST).replace(tzinfo=None),
        nullable=False
    )
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)

    post = relationship("Post", back_populates="comments")
