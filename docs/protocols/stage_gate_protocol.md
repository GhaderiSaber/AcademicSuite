# Interactive Stage-Gate Protocol (Directive 11)

## Purpose
The **Interactive Stage-Gate Protocol** enforces human-in-the-loop governance and prevents runaway autonomous execution across multi-stage dissertation pipelines.

## Standard Operational Procedure
At the conclusion of each micro-stage, section drafting phase, or hypothesis analysis:
1. **Stage Completion Report**: The agent must output an explicit report stating:
   - **What Was Done**: Subagents invoked, deterministic scripts executed, exact numbers verified, and physical disk artifacts generated.
   - **What Will Be Done Next**: Target next stage, assigned subagent, input prerequisites, and expected deliverables.
2. **Mandatory Confirmation Pause**:
   - The agent **MUST STOP and await user confirmation** before advancing.
   - Autonomous execution across multiple stages in a single turn without explicit user approval is strictly prohibited.
