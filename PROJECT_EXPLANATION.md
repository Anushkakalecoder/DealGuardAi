# Project Explanation — Learn This Before Judging

## One sentence

DealGuard is a protocol-aware AI merchant layer where an AI buyer can state what it wants, a merchant agent can construct and negotiate a profitable offer, deterministic code verifies every financial constraint, a human approves high-value actions, and Razorpay executes the resulting test-mode payment.

## Component responsibilities

- **GPT-OSS-120B**: understands language and communicates strategy.
- **Catalog**: makes merchant inventory machine-readable to AI buyers.
- **Deal Optimizer**: searches products, add-ons and legal discount choices.
- **Pricing Engine**: calculates revenue, cost, profit and margin.
- **Policy Engine**: enforces budget, min margin, max discount, stock and max-order limits.
- **Deal Proof**: stores why a deal passed, failed or requires approval.
- **Approval Gate**: prevents high-value autonomous money actions without merchant consent.
- **Razorpay**: creates and executes the approved payment order.
- **Webhook/Signature Verification**: verifies payment authenticity and updates the state.
- **Audit Trail**: records every consequential step.
- **Evaluation Suite**: compares DealGuard with static pricing on seeded synthetic buyers.

## Interview answer: “Why not let the LLM do everything?”

Financial correctness should not depend on probabilistic text generation. The LLM handles ambiguity; deterministic services handle money. If the LLM hallucinates a 30% discount, the policy engine blocks it because the merchant's configured maximum is 10%.

## Interview answer: “How do you maximize merchant revenue while allowing negotiation?”

A high price that the buyer rejects produces zero profit. DealGuard searches policy-compliant alternatives and maximizes expected merchant value: `profit × estimated acceptance probability`. This balances margin preservation with conversion probability.

## Interview answer: “What happens if Razorpay fails?”

The provider exception is logged as `PAYMENT_PROVIDER_FAILURE`; no deal is falsely marked paid. A failed-payment webhook leaves the deal available for retry and records the failure/recovery path.
