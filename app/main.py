from fastapi import FastAPI, Depends
from prometheus_client import make_asgi_app, Counter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import engine, get_db
from app.models import Base, User, Post

app = FastAPI(title="Wiki Service")

# ----------------------------
# Prometheus metrics
# ----------------------------
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

users_created = Counter(
    "users_created_total",
    "Total number of users created"
)

posts_created = Counter(
    "posts_created_total",
    "Total number of posts created"
)

# ----------------------------
# Health check
# ----------------------------
@app.get("/")
def health():
    return {"status": "ok"}

# ----------------------------
# Create DB tables on startup
# ----------------------------
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# ----------------------------
# Users APIs
# ----------------------------
@app.post("/users")
async def create_user(
    username: str,
    db: AsyncSession = Depends(get_db)
):
    user = User(username=username)
    db.add(user)
    await db.commit()
    await db.refresh(user)

    users_created.inc()
    return user


@app.get("/users")
async def list_users(
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User))
    return result.scalars().all()

# ----------------------------
# Posts APIs
# ----------------------------
@app.post("/posts")
async def create_post(
    title: str,
    content: str,
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    post = Post(
        title=title,
        content=content,
        owner_id=user_id
    )
    db.add(post)
    await db.commit()
    await db.refresh(post)

    posts_created.inc()
    return post


@app.get("/posts")
async def list_posts(
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Post))
    return result.scalars().all()

