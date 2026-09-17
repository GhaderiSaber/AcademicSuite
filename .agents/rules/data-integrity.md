# Data Integrity Rules (Directives 2, 9, 10)

1. **Directive 2 (Deterministic Calculation)**:
   - Zero mental math or hallucinated numbers, $p$-values, or test statistics.
   - Calculations must execute through deterministic scripts in `.agents/skills/*/scripts/` or `tools/python/`.
2. **Directive 9 (Realistic Decimal Noise)**:
   - Never generate synthetic whole-integer means. Inject bounded empirical noise: $\mu_{\text{empirical}} = \mu_{\text{target}} + \delta, \delta \sim \text{Uniform}(\pm 0.08, \pm 0.25)$.
3. **Directive 10 (Multi-Signal Anomaly Index - MSAI)**:
   - Never accuse data fabrication on a single threshold. Evaluate MSAI combining effect size, variance deflation, group overlap, and scale reliability.
