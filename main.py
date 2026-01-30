from fastapi import FastAPI
from prometheus_client import make_asgi_app

from app.database import engine
from app.models import Base

app = FastAPI(title="Wiki Service")

# Prometheus metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# Health check (important for debugging)
@app.get("/")
def health():
    return {"status": "ok"}

# Create DB tables on startup
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

