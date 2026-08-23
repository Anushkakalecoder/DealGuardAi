from datetime import datetime
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    sku: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(200))
    category: Mapped[str] = mapped_column(String(80), index=True)
    price: Mapped[float] = mapped_column(Float)
    cost: Mapped[float] = mapped_column(Float)
    inventory: Mapped[int] = mapped_column(Integer)
    tags: Mapped[list] = mapped_column(JSON, default=list)
    delivery_days: Mapped[int] = mapped_column(Integer, default=2)
    is_addon: Mapped[bool] = mapped_column(Boolean, default=False)
    compatible_with: Mapped[list] = mapped_column(JSON, default=list)


class MerchantPolicy(Base):
    __tablename__ = "merchant_policies"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    minimum_margin_pct: Mapped[float] = mapped_column(Float, default=18.0)
    maximum_discount_pct: Mapped[float] = mapped_column(Float, default=10.0)
    auto_approval_limit: Mapped[float] = mapped_column(Float, default=10000.0)
    max_order_value: Mapped[float] = mapped_column(Float, default=100000.0)
    currency: Mapped[str] = mapped_column(String(8), default="INR")


class Deal(Base):
    __tablename__ = "deals"
    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    status: Mapped[str] = mapped_column(String(40), index=True, default="OFFER")
    buyer_message: Mapped[str] = mapped_column(Text, default="")
    category: Mapped[str] = mapped_column(String(80))
    quantity: Mapped[int] = mapped_column(Integer)
    buyer_budget: Mapped[float] = mapped_column(Float)
    hard_constraints: Mapped[list] = mapped_column(JSON, default=list)
    soft_preferences: Mapped[list] = mapped_column(JSON, default=list)
    product_sku: Mapped[str] = mapped_column(String(64))
    addons: Mapped[list] = mapped_column(JSON, default=list)
    discount_pct: Mapped[float] = mapped_column(Float, default=0)
    gross_price: Mapped[float] = mapped_column(Float)
    final_price: Mapped[float] = mapped_column(Float)
    total_cost: Mapped[float] = mapped_column(Float)
    profit: Mapped[float] = mapped_column(Float)
    margin_pct: Mapped[float] = mapped_column(Float)
    acceptance_probability: Mapped[float] = mapped_column(Float, default=0.0)
    expected_merchant_value: Mapped[float] = mapped_column(Float, default=0.0)
    requires_approval: Mapped[bool] = mapped_column(Boolean, default=False)
    approval_status: Mapped[str] = mapped_column(String(30), default="NOT_REQUIRED")
    proof: Mapped[dict] = mapped_column(JSON, default=dict)
    ai_explanation: Mapped[str] = mapped_column(Text, default="")
    round_number: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AuditEvent(Base):
    __tablename__ = "audit_events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    deal_id: Mapped[str] = mapped_column(ForeignKey("deals.id"), index=True)
    event_type: Mapped[str] = mapped_column(String(80), index=True)
    actor: Mapped[str] = mapped_column(String(80))
    details: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class PaymentRecord(Base):
    __tablename__ = "payments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    deal_id: Mapped[str] = mapped_column(ForeignKey("deals.id"), unique=True, index=True)
    razorpay_order_id: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    razorpay_payment_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    amount: Mapped[float] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String(8), default="INR")
    status: Mapped[str] = mapped_column(String(40), default="ORDER_NOT_CREATED")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
