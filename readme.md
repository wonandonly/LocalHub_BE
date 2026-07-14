# LocalHub Backend

FastAPI + SQLite 기반 게시판 CRUD 백엔드 프로젝트입니다.

## 실행 방법

1. 의존성 설치
   ```bash
   pip install -r requirements.txt
   ```

2. 서버 실행
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

3. API 확인
   - Health: http://localhost:8000/health
   - Posts: http://localhost:8000/api/posts

## 주요 엔드포인트

- GET /health
- GET /api/posts
- POST /api/posts
- GET /api/posts/{post_id}
- PUT /api/posts/{post_id}
- DELETE /api/posts/{post_id}

## 테스트

```bash
pytest -q
```

## ERD
erDiagram
    POSTS {
        int id PK
        string title
        text content
        string password
        int view_count
        datetime created_at
    }

    COMMENTS {
        int id PK
        text content
        datetime created_at
        int post_id FK
    }

    POSTS ||--o{ COMMENTS : has
