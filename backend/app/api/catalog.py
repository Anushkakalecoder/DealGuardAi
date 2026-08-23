from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.entities import Product

router = APIRouter(prefix="/catalog", tags=["Catalog"])


@router.get("")
def get_catalog(db: Session = Depends(get_db)):
    items = list(db.scalars(select(Product).order_by(Product.is_addon, Product.price.desc())).all())
    return [{
        "sku": p.sku, "name": p.name, "category": p.category, "price": p.price, "inventory": p.inventory,
        "tags": p.tags, "delivery_days": p.delivery_days, "is_addon": p.is_addon,
        "compatible_with": p.compatible_with,
    } for p in items]
