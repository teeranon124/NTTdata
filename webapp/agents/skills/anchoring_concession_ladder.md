# Skill: Anchoring & Concession Ladder
Category: Behavioral Game Theory & Negotiation Psychology
Skill ID: `skill_anchoring_ladder`

## 1. THEORETICAL PRINCIPLE
The **Anchoring Effect** (Tversky & Kahneman) posits that initial figures presented in a commercial negotiation serve as cognitive anchors, disproportionately pulling counter-offers toward that reference point. In B2B procurement, opening with the true reservation target forfeits concession room.

## 2. MATHEMATICAL FORMULATION
1. **Anchor Price ($P_{\text{anchor}}$)**:
   $$P_{\text{anchor}} = \text{round}(P_{\text{target}} \times (1 - \delta_{\text{anchor}}), 2)$$
   where $\delta_{\text{anchor}} = 0.07$ (7% aggressive anchoring discount for 1-year Blanket Orders).
2. **Intermediate Step Concession ($P_{\text{step}}$)**:
   $$P_{\text{step}} = \text{round}\left(\frac{P_{\text{anchor}} + P_{\text{target}}}{2}, 2\right)$$
3. **Trade-off Condition**:
   Never concede on price without demanding a reciprocal concession (e.g., locking credit terms to 45-60 days or obtaining free DDP shipping).

## 3. AGENT EXECUTION RULES
- In Round 1, propose $P_{\text{anchor}}$ and 60 days credit.
- Never state "this is our anchor" or "this is a buffer". Use executive phrasing: "ฝ่ายจัดซื้อขอเรียนเสนอเปิดเงื่อนไขราคาจัดซื้อที่ ฿X".
- If the vendor moves closer to target, concede incrementally to $P_{\text{step}}$ while reducing credit term demand to 45 days.
