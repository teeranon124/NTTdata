# Skill: Total Cost of Ownership (TCO) & Working Capital Optimization
Category: Corporate Financial Modeling
Skill ID: `skill_tco_finance`

## 1. THEORETICAL PRINCIPLE
Total Cost of Ownership (TCO) evaluates the holistic lifetime cost of an acquired asset rather than nominal invoice price alone. In enterprise supply chains, payment credit terms directly influence corporate working capital efficiency and liquidity.

## 2. MATHEMATICAL FORMULATION
1. **Working Capital Financing Value of Credit Term Extension**:
   $$\text{Benefit}_{\text{credit}} = P \times \left(\frac{\Delta \text{Days}}{365}\right) \times \text{WACC}$$
   where:
   - $\Delta \text{Days} = \text{Offered Credit Days} - \text{Baseline Days (30)}$
   - $\text{WACC} = 7.0\%$ (Enterprise Weighted Average Cost of Capital).
2. **Effective TCO Unit Price**:
   $$P_{\text{effective\_TCO}} = P_{\text{unit}} - \text{Benefit}_{\text{credit}}$$
3. **Net Enterprise Savings**:
   $$\text{Net Savings} = (P_{\text{budget}} - P_{\text{effective\_TCO}}) \times Q_{\text{annual}}$$

## 3. AGENT EXECUTION RULES
- Use this mathematical engine internally to evaluate vendor proposals.
- If the vendor cannot lower the nominal price, leverage credit extensions (45 to 60 days) to achieve equivalent net TCO targets.
- STRICT CONFIDENTIALITY: Never reveal WACC rates or TCO formulas to external suppliers.
