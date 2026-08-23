# 2.5-minute Demo Script

## 0:00 — Problem

“AI agents can increasingly discover products and pay, but merchants still need to know whether an AI-negotiated transaction is economically safe and authorized before money moves.”

## 0:15 — Buyer mandate

Enter:

> I need 50 corporate gift boxes under ₹35,000, vegetarian, delivery by Friday. Premium packaging preferred.

Show that GPT-OSS-120B turns language into a buyer mandate and the system constructs an offer from the agent-readable catalog.

## 0:40 — Merchant growth

Show:

- selected product
- cross-sell add-on if chosen
- final price
- profit/margin
- expected merchant value

Explain: “The optimizer maximizes expected merchant value, not the buyer's cheapest price.”

## 1:00 — Deal Proof

Show deterministic checks:

- buyer budget
- minimum margin
- max discount
- inventory
- max order value

Say: “The LLM can propose; it cannot make these checks pass.”

## 1:20 — Required failure

Demand 30% discount.

Show:

> UNSAFE ACTION BLOCKED — merchant max 10%

Then show the automatically generated compliant alternative.

Say: “No Razorpay order was created for the blocked action.”

## 1:45 — Human gate + payment

Approve the high-value deal. Click Pay with Razorpay and complete Test Mode checkout.

## 2:05 — Audit

Open Audit Trail. Show buyer intent, offer optimization, proof, blocked action, safe repair, approval and Razorpay event.

## 2:20 — Evidence

Run the 500-scenario evaluation and show static-commerce vs DealGuard metrics.

Be explicit: “These are seeded synthetic evaluation results, not production claims.”

## Final line

“Razorpay moves the money. DealGuard proves the autonomous deal is worth and allowed to exist.”
