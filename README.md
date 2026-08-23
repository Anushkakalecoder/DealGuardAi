# DealGuard AI

**Verified negotiation and trust layer for agentic commerce.**

DealGuard lets an AI buyer express a natural-language purchasing mandate, lets a merchant-side agent construct and negotiate a high-value offer, verifies every financial fact with deterministic code, requires human approval above merchant-defined limits, and executes approved transactions through **Razorpay Test Mode**.

> **Architecture rule:** LLM proposes and explains → deterministic code calculates and verifies → policy/human authorizes → Razorpay executes.

## Why this fits Razorpay Track 01

| Track requirement | DealGuard implementation |
|---|---|
| Grow merchant revenue | Deal optimizer + profitable cross-sell bundles + expected merchant value objective |
| AI buyer end-to-end | Natural-language buyer mandate → quote → negotiation → authorization → Razorpay checkout |
| Agent-readable catalog | `/catalog`, `/.well-known/dealguard.json`, `/protocol/quote` |
| Upsell/cross-sell | Compatible add-ons are searched as part of deal optimization |
| Explainable | AI explanation plus deterministic Deal Proof |
| Bounded | Min margin, max discount, inventory, budget and max-order policies |
| Gated | Human approval for transactions above the merchant auto-approval threshold |
| Audit trail | Every important decision/action persisted in `audit_events` |
| Failure handled gracefully | Unsafe discount is blocked and a compliant alternative is generated |
| Money execution | Razorpay Orders API + Checkout signature verification + webhook handling |

## Protocol story

DealGuard is **protocol-aware, not falsely advertised as protocol-certified**. The normalized `buyer_mandate`, `offer`, `deal_proof`, and `authorization` objects are designed for the same interoperability problem addressed by UAP/ACP/AP2. The approval/budget mandate is AP2-inspired. x402 is intentionally not used as the payment rail in this Razorpay build; the negotiation/quote layer is rail-agnostic.

See `ARCHITECTURE.md` for the mapping.

## Repository

```text
dealguard/
├── backend/                 FastAPI + SQLAlchemy + Groq + Razorpay
│   ├── app/api/             HTTP endpoints
│   ├── app/core/            config/database
│   ├── app/models/          persisted entities
│   ├── app/services/        AI, pricing, optimizer, policy, payments, evals
│   ├── tests/               deterministic engine tests
│   └── scripts/run_eval.py  standalone evaluation
├── frontend/                React + Vite UI
├── .github/workflows/ci.yml
└── docker-compose.yml
```

## 1. Backend setup (Windows PowerShell)

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Fill **only your local `backend/.env`**:

```env
GROQ_API_KEY=gsk_...
GROQ_MODEL=openai/gpt-oss-120b
RAZORPAY_KEY_ID=rzp_test_...
RAZORPAY_KEY_SECRET=...
RAZORPAY_WEBHOOK_SECRET=...
```

Run:

```powershell
python -m uvicorn app.main:app --reload
```

Open Swagger: `http://127.0.0.1:8000/docs`

## 2. Frontend setup

```powershell
cd frontend
Copy-Item .env.example .env
npm install
npm run dev
```

Open `http://localhost:5173`.

## 3. First demo

1. Start the backend and frontend.
2. In **Deal Arena**, submit the pre-filled buyer request.
3. Inspect the optimized offer, cross-sell, margin and Deal Proof.
4. Counter at ₹30,000 and show the merchant optimizer respond.
5. Click **Try unsafe action** with 30% discount. It will be blocked because the merchant max is 10%; DealGuard generates a safe alternative.
6. Approve the deal if the human gate is triggered.
7. Click **Pay with Razorpay** and complete a Test Mode payment.
8. Open **Audit Trail** and show the entire lifecycle.
9. Open **Evals** and run the 500-scenario controlled simulation.

## 4. Groq GPT-OSS-120B role

The model performs:

- natural-language → structured buyer mandate
- merchant-side communication/negotiation explanation
- explanation of already-verified offers

The model **does not** calculate margin, validate discounts, approve transactions, verify inventory, create payment amounts, or verify Razorpay signatures.

If `GROQ_API_KEY` is absent or the model call fails, DealGuard uses a deterministic fallback parser/message and logs `AI_FALLBACK_USED`. This keeps the demo recoverable without silently treating LLM output as financial truth.

## 5. Money safety

`POST /payments/order/{deal_id}` accepts **no amount from the browser**. The backend loads the persisted, approved Deal and creates the Razorpay order for that verified amount. This prevents client-side amount tampering.

## 6. Razorpay webhook

Configure a Razorpay Test Mode webhook pointing to:

```text
https://YOUR_BACKEND/webhooks/razorpay
```

Use the same webhook secret in Razorpay Dashboard and `RAZORPAY_WEBHOOK_SECRET`. Suggested events:

- `payment.captured`
- `payment.failed`
- `order.paid`

For local webhook testing, expose port 8000 through a tunnel such as ngrok/Cloudflare Tunnel.

## 7. Evaluation

From `backend`:

```powershell
python scripts/run_eval.py
```

or use `POST /analytics/evaluate`.

The evaluation is a **seeded synthetic simulation**, clearly labeled as such. It compares static catalog commerce to DealGuard and reports conversion, revenue, recovered deals and executed policy violations. Do not present these numbers as production results.

## 8. Tests

```powershell
cd backend
pytest -q
```

## 9. Deployment

Recommended:

- Frontend: **Vercel**, Root Directory `frontend`
- Backend + PostgreSQL: **Render** using the included deployment configuration as a starting point

Backend production environment variables:

```text
DATABASE_URL
FRONTEND_ORIGIN
GROQ_API_KEY
GROQ_MODEL=openai/gpt-oss-120b
RAZORPAY_KEY_ID
RAZORPAY_KEY_SECRET
RAZORPAY_WEBHOOK_SECRET
```

Frontend environment variable:

```text
VITE_API_BASE_URL=https://YOUR_BACKEND
```

Never commit `.env` files.

## Demo thesis

> **AI agents can already discover and pay. DealGuard makes the deal itself verifiable.**

> **Razorpay moves the money. DealGuard proves the autonomous deal is worth and allowed to exist.**
