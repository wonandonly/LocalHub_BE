from typing import Generator

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.deps import SessionLocal, engine
from app.models import Base, Comment, Location, Post
from app.schemas import CommentCreate, CommentOut, LocationCreate, LocationOut, PostCreate, PostDelete, PostOut, PostUpdate

# Import models so SQLAlchemy can create the tables on startup.
import app.models  # noqa: F401

app = FastAPI(title="LocalHub Board API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/locations", response_model=LocationOut, status_code=status.HTTP_201_CREATED)
def create_location(payload: LocationCreate, db: Session = Depends(get_db)) -> dict:
    location = db.query(Location).filter(Location.name == payload.name).first()
    if location is None:
        location = Location(name=payload.name)
        db.add(location)
        db.commit()
        db.refresh(location)
    return {"id": location.id, "name": location.name}


@app.get("/api/posts", response_model=list[PostOut])
def list_posts(db: Session = Depends(get_db)) -> list[dict]:
    posts = db.query(Post).order_by(Post.id.desc()).all()
    return [
        {
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "category": post.category,
            "view_count": post.view_count,
            "created_at": post.created_at,
            "location_id": post.location_id,
            "comments": [{"id": c.id, "content": c.content, "created_at": c.created_at} for c in post.comments],
        }
        for post in posts
    ]


@app.post("/api/posts", response_model=PostOut, status_code=status.HTTP_201_CREATED)
def create_post(payload: PostCreate, db: Session = Depends(get_db)) -> dict:
    location_id = payload.location_id
    if payload.location_id is None:
        location = db.query(Location).filter(Location.name == "서울").first()
        if location is None:
            location = Location(name="서울")
            db.add(location)
            db.commit()
            db.refresh(location)
        location_id = location.id

    location = db.query(Location).filter(Location.id == location_id).first()
    if location is None:
        raise HTTPException(status_code=404, detail="location not found")

    post = Post(
        title=payload.title,
        content=payload.content,
        category=payload.category,
        password=payload.password,
        location_id=location_id,
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    return {
        "id": post.id,
        "title": post.title,
        "content": post.content,
        "category": post.category,
        "view_count": post.view_count,
        "created_at": post.created_at,
        "location_id": post.location_id,
        "comments": [],
    }


@app.get("/api/posts/{post_id}", response_model=PostOut)
def get_post(post_id: int, db: Session = Depends(get_db)) -> dict:
    post = db.query(Post).filter(Post.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail="post not found")

    post.view_count += 1
    db.commit()
    db.refresh(post)
    return {
        "id": post.id,
        "title": post.title,
        "content": post.content,
        "category": post.category,
        "view_count": post.view_count,
        "created_at": post.created_at,
        "location_id": post.location_id,
        "comments": [{"id": c.id, "content": c.content, "created_at": c.created_at} for c in post.comments],
    }


@app.put("/api/posts/{post_id}", response_model=PostOut)
def update_post(post_id: int, payload: PostUpdate, db: Session = Depends(get_db)) -> dict:
    post = db.query(Post).filter(Post.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail="post not found")
    if post.password != payload.password:
        raise HTTPException(status_code=403, detail="invalid password")

    post.title = payload.title
    post.content = payload.content
    db.commit()
    db.refresh(post)
    return {
        "id": post.id,
        "title": post.title,
        "content": post.content,
        "category": post.category,
        "view_count": post.view_count,
        "created_at": post.created_at,
        "location_id": post.location_id,
        "comments": [{"id": c.id, "content": c.content, "created_at": c.created_at} for c in post.comments],
    }


@app.delete("/api/posts/{post_id}")
def delete_post(post_id: int, payload: PostDelete, db: Session = Depends(get_db)) -> dict:
    post = db.query(Post).filter(Post.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail="post not found")
    if post.password != payload.password:
        raise HTTPException(status_code=403, detail="invalid password")

    db.delete(post)
    db.commit()
    return {"deleted": True, "id": post_id}


@app.post("/api/posts/{post_id}/comments", response_model=CommentOut, status_code=status.HTTP_201_CREATED)
def create_comment(post_id: int, payload: CommentCreate, db: Session = Depends(get_db)) -> dict:
    post = db.query(Post).filter(Post.id == post_id).first()
    if post is None:
        raise HTTPException(status_code=404, detail="post not found")

    comment = Comment(content=payload.content, post_id=post_id)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return {"id": comment.id, "content": comment.content, "created_at": comment.created_at}
