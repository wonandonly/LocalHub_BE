import os
from typing import Generator

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.deps import SessionLocal, engine
from app.models import Base, Comment, Post
from app.schemas import ChatRequest, ChatResponse, CommentCreate, CommentOut, PostCreate, PostDelete, PostOut, PostUpdate
from dotenv import load_dotenv

from openai import OpenAI

load_dotenv()
#print(os.getenv("OPENAI_API_KEY"))

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


@app.get("/api/posts", response_model=list[PostOut])
def list_posts(db: Session = Depends(get_db)) -> list[dict]:
    posts = db.query(Post).order_by(Post.id.desc()).all()
    return [
        {
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "view_count": post.view_count,
            "created_at": post.created_at,
            "comments": [{"id": c.id, "content": c.content, "created_at": c.created_at} for c in post.comments],
        }
        for post in posts
    ]


@app.post("/api/posts", response_model=PostOut, status_code=status.HTTP_201_CREATED)
def create_post(payload: PostCreate, db: Session = Depends(get_db)) -> dict:
    # 1. location 관련 로직을 모두 제거하고 바로 Post 객체를 생성합니다.
    post = Post(
        title=payload.title,
        content=payload.content,
        password=payload.password,
    )
    
    # 2. DB에 저장 및 커밋
    db.add(post)
    db.commit()
    db.refresh(post)
    
    # 3. 반환값 매핑 (기존과 동일)
    return {
        "id": post.id,
        "title": post.title,
        "content": post.content,
        "view_count": post.view_count,
        "created_at": post.created_at,
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
        "view_count": post.view_count,
        "created_at": post.created_at,
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
        "view_count": post.view_count,
        "created_at": post.created_at,
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

@app.post("/api/chat", response_model=ChatResponse)
def chat(payload: ChatRequest):

    message = payload.message.strip()

    reply = "죄송합니다. 답변을 생성하지 못했습니다."

    if os.getenv("OPENAI_API_KEY"):
        try:
            import openai

            client = openai.OpenAI(
                api_key=os.getenv("OPENAI_API_KEY")
            )

            response = client.responses.create(
                model="gpt-4o-mini",
                input=[
                    {
                        "role": "system",
                        "content": "당신은 공공데이터 기반 지역 정보 챗봇입니다. 짧고 친절하게 답변하세요."
                    },
                    {
                        "role": "user",
                        "content": message
                    }
                ]
            )

            if response.output_text:
                reply = response.output_text

        except Exception as e:
            reply = f"오류가 발생했습니다. ({e})"

    return {"reply": reply}
