# DealGuard Architecture

## End-to-end flow

```text
Buyer natural language
        │
        ▼
Groq GPT-OSS-120B
(intent extraction only)
        │
        ▼
Structured Buyer Mandate
        │
        ▼
Agent-readable Catalog
        │
        ▼
Deal Optimizer ───────────────┐
 │ products                   │
 │ add-on combinations        │
 │ bounded discounts          │
 └──────────────┬─────────────┘
                ▼
        Pricing Engine
        (deterministic)
                │
                ▼
         Policy Engine
 budget / margin / discount /
 inventory / order-value caps
                │
      ┌─────────┼─────────┐
      ▼         ▼         ▼
   BLOCK     AUTO OK   HUMAN GATE
      │                   │
      │              approve/reject
      │                   │
      └──────────┬────────┘
                 ▼
              Deal Proof
                 │
                 ▼
              Razorpay
        Order → Checkout → Verify
                 │
                 ▼
               Webhook
                 │
                 ▼
              Audit log
```

## Why expected merchant value?

Insisting on the maximum price can produce zero sales. DealGuard scores policy-compliant offers with:

```text
Expected Merchant Value = Merchant Profit × Estimated Acceptance Probability
```

The current acceptance probability is an explicitly labeled heuristic derived from price distance and preference satisfaction. It is **not represented as a trained production ML model**. The eval layer can later be used to train/calibrate it.

## Money action boundary

The browser cannot submit a payment amount. It submits only a `deal_id`. The backend looks up the persisted verified amount after checking:

- deal status == `APPROVED`
- approval status == `AUTO_APPROVED` or `APPROVED`
- deterministic Deal Proof exists

Only then does the Razorpay service create an Order.

## Protocol-aware bridge

### UAP / ACP side

DealGuard's merchant exposes machine-readable discovery/quote primitives:

- `GET /catalog`
- `GET /.well-known/dealguard.json`
- `POST /protocol/quote`

These normalize intent and offer objects so an external buyer agent does not need to scrape a human storefront.

### AP2 side

The Buyer Mandate carries a maximum spend; the Merchant Policy carries auto-approval and max-order limits. Deals beyond authority are escalated to a human gate. This demonstrates delegated authorization and auditability concepts without claiming formal AP2 compliance.

### x402 side

x402 is not used in the execution path. DealGuard's quote/verification layer is designed to sit above payment rails; the hackathon implementation deliberately executes through Razorpay Test Mode.

## LLM trust boundary

### LLM may

- interpret natural-language intent
- propose/communicate negotiation strategy
- explain deterministic outcomes

### LLM may not

- calculate trusted margin
- decide that a policy passed
- mutate merchant policy
- set the Razorpay amount
- bypass approval
- verify payment/webhook signatures

This is the core safety design.
