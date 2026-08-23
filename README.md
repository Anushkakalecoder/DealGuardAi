# DealGuard AI

> **The negotiation and trust layer for agentic commerce.**  
> **AI negotiates. Code verifies. Razorpay executes.**

DealGuard AI is a protocol-aware commerce layer that allows an AI buyer to negotiate with a merchant, construct a commercially viable deal, verify every money-related decision with deterministic code, enforce merchant-defined limits, and execute the final approved transaction through **Razorpay Test Mode**.

It is built for a future where AI agents do not just discover products — they **negotiate, authorize, and transact**.

---

## 🚀 The Problem

AI agents can increasingly discover products and initiate purchases, but there is still a missing trust layer between **“I want to buy this”** and **“this transaction should actually happen.”**

A merchant still needs to know:

- Is the deal profitable?
- Does the discount violate policy?
- Is there enough inventory?
- Is the transaction inside delegated authority?
- Should a human approve it?
- Can an abandoning buyer be recovered safely?
- Can every money action be explained later?

A pure LLM is not enough for this because financial actions must be **bounded, deterministic, explainable and auditable**.

DealGuard AI solves that problem.

---

## 💡 What DealGuard AI Does

A buyer can submit a request such as:

> “I need 50 corporate gift boxes under ₹35,000, vegetarian, delivery by Friday. Premium packaging preferred.”

DealGuard then:

1. Converts the request into a structured **Buyer Mandate**.
2. Reads an agent-readable merchant catalog and merchant policy.
3. Searches product, bundle, cross-sell and bounded discount combinations.
4. Scores offers using **Expected Merchant Value**.
5. Calculates final price, cost, profit and margin deterministically.
6. Verifies budget, margin, discount, inventory and order-value constraints.
7. Produces a deterministic **Deal Proof**.
8. Blocks unsafe money actions.
9. Generates a compliant alternative when possible.
10. Requires human approval above merchant-defined authority.
11. Creates a Razorpay order only from the persisted verified amount.
12. Verifies payment and webhook events.
13. Stores the full lifecycle in an audit trail.

> **Architecture rule:** LLM proposes and explains → deterministic code calculates and verifies → policy/human authorizes → Razorpay executes.

> **The LLM can propose a financial action, but it can never authorize one.**

---

# 🏗️ Architecture

```text
Buyer / AI Agent
      |
      v
Natural-language purchasing mandate
      |
      v
Groq GPT-OSS-120B
(intent extraction + communication)
      |
      v
Structured Buyer Mandate
      |
      +-------------------------------+
      |                               |
      v                               v
Agent-readable Catalog         Merchant Policy
products / price / stock       min margin
compatible add-ons             max discount
                               auto-approval limit
                               max order value
      |                               |
      +---------------+---------------+
                      |
                      v
                Deal Optimizer
          products + add-ons + discount
                      |
                      v
        Expected Merchant Value scorer
      Profit × Estimated Acceptance Probability
                      |
                      v
             Deterministic Pricing Engine
      gross / discount / final / cost / profit / margin
                      |
                      v
                 Policy Engine
      budget / margin / discount / inventory / order cap
             /              |               \
            v               v                v
        BLOCKED        AUTO-APPROVED     HUMAN GATE
            |                               |
            v                               v
     Safe alternative                 approve / reject
            \______________________________/
                          |
                          v
                      Deal Proof
           checks + verdict + proof hash
                          |
                          v
                       Razorpay
              Order -> Checkout -> Verify
                          |
                          v
                       Webhook
                          |
                          v
                      Audit Trail
```

---

## 🧠 LLM Trust Boundary

### The LLM may

- parse natural-language intent
- understand preferences and flexible constraints
- communicate negotiation strategy
- explain already-verified outcomes

### The LLM may not

- calculate trusted margin
- decide whether merchant policy passed
- change merchant limits
- set the Razorpay amount
- bypass approval
- verify payment signatures
- verify webhook signatures

The AI handles ambiguity. Deterministic code handles financial truth.

---

## 💰 Revenue Growth Logic

DealGuard does not simply maximize price or discount.

It scores policy-compliant offers using:

```text
Expected Merchant Value
    = Merchant Profit × Estimated Acceptance Probability
```

A very high price can have strong margin but low conversion probability.  
A very low price may convert but destroy merchant economics.

DealGuard searches for the best compliant trade-off and can include compatible cross-sells or add-ons.

> The current acceptance probability is a transparent heuristic for the prototype, not a production-trained ML model.

---

## 🛡️ Deal Proof

Before payment, DealGuard generates deterministic evidence of the decision.

Example:

```text
Buyer budget            PASS
Minimum margin          PASS
Maximum discount        PASS
Inventory               PASS
Maximum order value     PASS
Human approval          REQUIRED
```

The proof records the values used, checks executed, verdict and proof hash.

This answers:

> **Why was this AI-generated transaction allowed?**

---

## 🚨 Graceful Failure

The hackathon requires a failure to be handled gracefully.

Example:

```text
Requested discount: 30%
Merchant maximum:   10%
```

DealGuard returns:

```text
UNSAFE_ACTION_BLOCKED
money_action_executed = false
```

It then searches inside merchant boundaries and generates a safe alternative rather than simply terminating the journey.

This demonstrates **bounded autonomy**.

---

## 🤝 Agentic Negotiation

A DealGuard transaction is not a static checkout.

```text
Buyer Agent
     |
     | counteroffer
     v
Merchant-side DealGuard Agent
     |
     | pricing + policy verification
     v
Accept / safe counter / reject
```

Every proposed money action passes through deterministic verification before it can progress.

---

# 🤖 Agent-Readable Commerce

DealGuard exposes machine-readable merchant primitives:

```http
GET /catalog
GET /.well-known/dealguard.json
POST /protocol/quote
```

The architecture normalizes concepts such as:

```text
Buyer Mandate
Offer
Deal Proof
Authorization
Payment
```

This is aligned with the interoperability problem being addressed by emerging agentic-commerce protocols such as **UAP, ACP and AP2**.

DealGuard is **protocol-aware**, not presented as formally certified by those standards.

The negotiation/verification layer is payment-rail agnostic; this hackathon implementation executes money through **Razorpay Test Mode**.

---

# 🏆 Why DealGuard Fits Razorpay Track 01 — AI Growth & Agentic Commerce

Track 01 asks builders to **grow merchant revenue and make merchants sellable to AI buyers**.

DealGuard addresses both objectives.

| Track requirement | DealGuard AI |
|---|---|
| Grow merchant revenue | Optimizes offers using merchant profit and estimated acceptance probability |
| Agentic commerce | Buyer mandate → negotiation → verification → authorization → Razorpay payment |
| Conversational checkout | Natural-language buyer intent |
| Agent-readable catalog | `/catalog`, discovery manifest and `/protocol/quote` |
| Upsell / cross-sell | Optimizer evaluates compatible profitable add-ons |
| AI buyer end-to-end | An AI buyer can move from intent to executable payment |
| Explainable money actions | AI explanation + deterministic Deal Proof |
| Bounded | Budget, margin, discount, inventory and order-value constraints |
| Gated | Human approval beyond delegated authority |
| Audit trail | Important financial decisions are persisted |
| Graceful failure | Unsafe discount is blocked and repaired |
| Razorpay integration | Orders API, Checkout, signature verification and webhook handling |
| Evidence of value | Seeded synthetic comparison against static commerce |

## Why this is strongly relatable to Track 01

A normal AI shopping assistant mainly helps the **buyer**.

DealGuard also protects and grows the **merchant**.

Agentic commerce creates a new merchant-side question:

> **If autonomous buyers negotiate aggressively, who protects the merchant's economics?**

DealGuard is that negotiation and trust layer.

It lets a merchant become transactable by AI buyers without giving an LLM unrestricted authority over pricing or payments.

---

# 🔄 End-to-End Demo

### 1. Buyer mandate

```text
I need 50 corporate gift boxes under ₹35,000,
vegetarian, delivery by Friday.
Premium packaging preferred.
```

### 2. Intent extraction

The AI converts it to structured constraints.

### 3. Offer optimization

DealGuard searches products, add-ons and bounded discounts.

### 4. Deterministic verification

Pricing and policy engines verify the offer.

### 5. Negotiation

The buyer can counteroffer and DealGuard decides whether to accept, counter or reject within policy.

### 6. Failure demo

The buyer asks for a 30% discount while the merchant allows only 10%.

DealGuard blocks the action and produces a safe alternative.

### 7. Approval

High-value transactions require explicit merchant approval.

### 8. Razorpay execution

Only the persisted verified amount is used to create the Razorpay order.

### 9. Payment verification

Checkout signature verification and webhooks update payment state.

### 10. Audit

The full lifecycle is visible in the Audit Trail.

---

# 📊 Evaluation

DealGuard contains a seeded synthetic evaluation comparing:

```text
Static Commerce
       vs
DealGuard Negotiated Commerce
```

Metrics include:

- conversion rate
- revenue
- recovered deals
- executed policy violations

The demo evaluation uses synthetic scenarios and is intentionally presented as **prototype evidence, not production performance**.

---

# 🧰 Tech Stack

**Frontend**
- React
- Vite
- JavaScript
- Razorpay Checkout

**Backend**
- FastAPI
- Python
- SQLAlchemy
- PostgreSQL / Supabase
- Pydantic

**AI**
- Groq
- `openai/gpt-oss-120b`

**Payments**
- Razorpay Orders API
- Razorpay Checkout
- Payment signature verification
- Razorpay webhooks

**Infrastructure**
- Vercel — frontend
- Render — backend
- Supabase PostgreSQL — persistence
- GitHub Actions — CI

---

# 📁 Repository Structure

```text
DealGuardAi/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   └── services/
│   ├── scripts/run_eval.py
│   └── tests/
├── frontend/
│   └── src/
├── .github/workflows/ci.yml
├── ARCHITECTURE.md
├── DEMO_SCRIPT.md
├── PROJECT_EXPLANATION.md
└── README.md
```

---

# 🔌 Core API

```http
GET  /health
GET  /config/public

GET  /catalog

GET  /merchant/policy
PUT  /merchant/policy

POST /deals/start
GET  /deals/{deal_id}
POST /deals/{deal_id}/counter
POST /deals/{deal_id}/demo-unsafe-discount
GET  /deals/{deal_id}/audit

POST /approvals/{deal_id}

POST /payments/order/{deal_id}
POST /payments/verify
POST /webhooks/razorpay

GET  /.well-known/dealguard.json
POST /protocol/quote

GET  /analytics
POST /analytics/evaluate
```

---

# ⚙️ Local Setup

## Backend

```bash
cd backend
python -m venv .venv
pip install -r requirements.txt
```

Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

Create `backend/.env`:

```env
APP_ENV=development
DATABASE_URL=sqlite:///./dealguard.db
FRONTEND_ORIGIN=http://localhost:5173

GROQ_API_KEY=your_key
GROQ_MODEL=openai/gpt-oss-120b
GROQ_REASONING_EFFORT=medium

RAZORPAY_KEY_ID=your_test_key_id
RAZORPAY_KEY_SECRET=your_test_secret
RAZORPAY_WEBHOOK_SECRET=your_webhook_secret
```

Run:

```bash
uvicorn app.main:app --reload
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

## Frontend

```bash
cd frontend
npm install
npm run dev
```

Create `frontend/.env`:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

---

# 🧪 Tests

```bash
cd backend
pytest -q
```

---

# 📈 Evaluation

```bash
cd backend
python scripts/run_eval.py
```

or call:

```http
POST /analytics/evaluate
```

---

# 🔒 Payment Safety

The browser does not submit the trusted payment amount.

```text
deal_id
   |
   v
Persisted Deal
   |
   v
Verified amount + approval + Deal Proof
   |
   v
Razorpay Order
```

This prevents client-side amount tampering.

---

# 🧾 Representative Audit Events

```text
BUYER_INTENT_PARSED
OFFER_OPTIMIZED
DEAL_PROOF_GENERATED
AI_EXPLANATION_GENERATED
BUYER_COUNTEROFFER
AI_NEGOTIATION_MESSAGE
UNSAFE_ACTION_BLOCKED
SAFE_ALTERNATIVE_GENERATED
HUMAN_APPROVED
RAZORPAY_ORDER_CREATED
PAYMENT_VERIFIED
```

---

# 🌐 Deployment

**Frontend — Vercel**

```text
https://dealguardainew.vercel.app
```

**Backend — Render**

```text
https://dealguardai.onrender.com
```

**Razorpay Webhook**

```text
https://dealguardai.onrender.com/webhooks/razorpay
```

---

# 🎯 Demo Thesis

> **AI agents can already discover products and pay. DealGuard makes sure the deal itself is economically valid, authorized and explainable before the money moves.**

> **Razorpay moves the money. DealGuard makes sure the deal should exist.**

---

# 🔮 Future Scope

- external autonomous buyer-agent integration
- calibrated acceptance probability using real merchant data
- personalized negotiation policies
- multi-merchant agent routing
- inventory reservation during negotiation
- richer delegated purchasing mandates
- formal adapters for emerging agentic-commerce protocols
- merchant negotiation analytics

---

# ⚠️ Prototype Notes

- Razorpay runs in **Test Mode**.
- Evaluation uses a **seeded synthetic simulation** and is not a production claim.
- Protocol support is **protocol-aware / inspired**, not official certification.
- AI-generated outputs are never treated as trusted financial truth.

---

## Built for Razorpay Track 01 — AI Growth & Agentic Commerce

**DealGuard AI turns a merchant from a passive catalog into an agent-ready business that can negotiate, protect margin, recover buyers, authorize safely and transact through Razorpay.**
