# Skill: Nash Bargaining Equilibrium & Cooperative Surplus
Category: Cooperative Game Theory
Skill ID: `skill_nash_bargaining`

## 1. THEORETICAL PRINCIPLE
The **Nash Bargaining Solution** (John Nash, 1950) identifies a unique Pareto-efficient outcome in two-party negotiations where both players maximize the joint product of their utility gains above their disagreement points (threat points / BATNA).

## 2. MATHEMATICAL FORMULATION
$$\max_{(P, C)} (u_{\text{buyer}}(P, C) - d_{\text{buyer}}) \times (u_{\text{vendor}}(P, C) - d_{\text{vendor}})$$
where:
- $u_{\text{buyer}} = (P_{\text{budget}} - P) + \text{CreditGain}(C)$
- $u_{\text{vendor}} = (P - \text{UnitCost}) + \text{VolumeSecurityGain}$
- $d_{\text{buyer}}, d_{\text{vendor}}$ = Utility of walking away to market alternatives (BATNA).

## 3. AGENT EXECUTION RULES
- When a price gap persists ($P_{\text{vendor}} > P_{\text{target}}$), explore non-zero-sum trade-offs:
  - Offer multi-plant consolidation (Blanket Order) guaranteeing 100% volume security to lower vendor overhead.
  - Settle at the cooperative equilibrium point ($P_{\text{target}}$) with extended working capital terms.
