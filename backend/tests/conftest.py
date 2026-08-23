import os
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_dealguard.db")
os.environ.setdefault("GROQ_API_KEY", "")

import pytest
from app.core.database import Base, SessionLocal, engine
from app.data.seed import SEED_PRODUCTS
from app.models.entities import MerchantPolicy, Product


@pytest.fixture(autouse=True)
def fresh_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        db.add(MerchantPolicy(id=1))
        for item in SEED_PRODUCTS:
            db.add(Product(**item))
        db.commit()
    yield
