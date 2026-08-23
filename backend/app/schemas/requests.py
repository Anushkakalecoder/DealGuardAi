from pydantic import BaseModel, Field


class StartDealRequest(BaseModel):
    message: str = Field(min_length=3, max_length=1000)


class CounterOfferRequest(BaseModel):
    amount: float = Field(gt=0)


class UnsafeDiscountRequest(BaseModel):
    requested_discount_pct: float = Field(gt=0, le=100)


class ApprovalRequest(BaseModel):
    decision: str


class VerifyPaymentRequest(BaseModel):
    razorpay_payment_id: str
    razorpay_order_id: str
    razorpay_signature: str


class PolicyUpdateRequest(BaseModel):
    minimum_margin_pct: float = Field(ge=0, le=100)
    maximum_discount_pct: float = Field(ge=0, le=100)
    auto_approval_limit: float = Field(gt=0)
    max_order_value: float = Field(gt=0)
    currency: str = "INR"


class EvaluationRequest(BaseModel):
    scenarios: int = Field(default=500, ge=50, le=5000)
    seed: int = 42
