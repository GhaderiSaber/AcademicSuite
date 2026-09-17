# Psychometric Scoring & Reverse-Coding Guidelines

## 1. Reverse-Coding Formula
For items scaled from $\text{Min}$ to $\text{Max}$:
$$X_{\text{rev}} = (\text{Max} + \text{Min}) - X$$
Example (1 to 5 Likert): $X_{\text{rev}} = (5 + 1) - X = 6 - X$.
Example (0 to 4 Likert): $X_{\text{rev}} = (4 + 0) - X = 4 - X$.

## 2. Scale Aggregation Standards
- Continuous composite score: Sum of item responses if missingness is zero.
- Mean score: Mean of items, retaining scale metric ($1-5$).
- Item completeness check: Disallow score computation if more than 1 item is missing in a subscale.
