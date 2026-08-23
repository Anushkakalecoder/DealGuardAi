from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

from app.core.config import settings
from app.core.database import Base, SessionLocal, engine
from app.data.seed import SEED_PRODUCTS
from app.models.entities import MerchantPolicy, Product
from app.api import analytics, approvals, catalog, deals, payments, policies, protocol, system, webhooks


def seed_database():
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        if not db.get(MerchantPolicy, 1):
            db.add(MerchantPolicy(id=1))
        count = db.scalar(select(Product.id).limit(1))
        if not count:
            for item in SEED_PRODUCTS:
                db.add(Product(**item))
        db.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    seed_database()
    yield


app = FastAPI(
    title="DealGuard AI",
    description="Verified negotiation and trust layer for agentic commerce",
    version="1.0.0",
    lifespan=lifespan,
)

origins = [settings.frontend_origin, "http://127.0.0.1:5173", "http://localhost:5173"]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

for router in [system.router, catalog.router, policies.router, deals.router, approvals.router, payments.router,
               webhooks.router, analytics.router, protocol.router]:
    app.include_router(router)


@app.get("/")
def root():
    return {"name": "DealGuard AI", "docs": "/docs", "manifest": "/.well-known/dealguard.json"}
