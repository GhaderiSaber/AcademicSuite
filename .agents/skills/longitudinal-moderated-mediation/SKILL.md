---
name: longitudinal-moderated-mediation
description: >-
  Execute 3-wave longitudinal moderated mediation modeling, autoregressive baseline controls, and 5,000 bootstrap index estimation.
---

# `longitudinal-moderated-mediation` — Skill Specification

## Overview & Scope

This skill provides deterministic estimation for time-lagged longitudinal conditional process models. It tests whether the indirect effect of a predictor at Time 1 on an outcome at Time 3 via a mediator at Time 2 is moderated by a boundary condition at Time 1.

## Methodological Standards & Equations

Follows Cole & Maxwell (2003) and Preacher, Rucker, & Hayes (2007). Baseline autoregressive controls for M1 and Y1 are mandatory to purge prior equilibrium variance.

## Deterministic Execution Instructions

Run CLI engine: `python3 .agents/skills/longitudinal-moderated-mediation/scripts/run_longitudinal_modmed.py --data <path> --output <path.json>`

