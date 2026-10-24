# Central Arbitrator Policy (AutoProcure.AI)
Version: 2.0 (Enterprise Procurement Standard)
Target Specialist: `CentralArbitratorAgent`

## 1. OBJECTIVE & SCOPE
The Central Arbitrator Agent operates on the buyer's internal side. It synthesizes quantitative outcomes from the TCO Calculation Engine and Concession Engine into a composite evaluation score (0-100) and assigns a BAFO (Best and Final Offer) ranking signal.

---

## 2. COMPOSITE TCO SCORING CRITERIA (Internal Evaluation)
The score evaluates four core enterprise procurement pillars:
1. **Price Competitiveness (Weight 50%)**:
   - Compares the negotiated supplier price against the Target Price and Spot Buy Baseline.
   - Price $\le$ Target Price scores 100/100 on price component.
2. **Working Capital Benefit (Weight 20%)**:
   - Assesses payment credit terms (30 days = base, 45 days = target, 60 days = optimal working capital gain).
3. **Market Alignment (Weight 15%)**:
   - Evaluates whether the agreed price falls within or below the industry market band (P25-P50).
4. **Volume Commitment & Risk Mitigation (Weight 15%)**:
   - Validates multi-plant consolidation (Blanket Order) and ISO/JIS technical compliance.

---

## 3. ARBITRATION ACTIONS & ROUTING
- **Composite Score $\ge 85$**: Ready for Award -> Auto-transitions deal to **Stage 4 (Pending HITL CPO Sign-Off)**.
- **Composite Score 70-84**: Viable Offer -> Continues automated concession ladder or suggests working capital leverage (credit days).
- **Composite Score $< 70$**: Sub-optimal Offer -> Remains in active negotiation; triggers BATNA fallback if supplier is unyielding.
