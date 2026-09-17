# Master Agent Behavioral Contracts Directory (Phase 4)

In accordance with **Phase 4 (Design Agent Contracts)** of the Academic Suite Architecture, every agent is governed by a formal 12-section behavioral contract. Contracts enforce strict operational boundaries, tool restrictions, and handoff protocols.

## Contract Schema (12 Non-Negotiable Sections)
1. `MISSION`: Fundamental role and epistemic responsibility.
2. `RESPONSIBILITIES`: Permitted actions and explicit mandates.
3. `NON-RESPONSIBILITIES`: Scope exclusions preventing role creep.
4. `INPUTS`: Machine-verifiable artifacts consumed.
5. `OUTPUTS`: Machine-verifiable artifacts produced (triads or JSON).
6. `ALLOWED TOOLS`: Whitelisted tools and deterministic CLI scripts.
7. `REQUIRED SKILLS`: Bundled skills invoked for domain capabilities.
8. `FORBIDDEN ACTIONS`: Explicit negative constraints (e.g. zero hallucinated numbers, zero raw data mutation).
9. `HANDOFF FORMAT`: Standard handoff envelope structure.
10. `VALIDATION REQUIREMENTS`: Upstream and downstream validation gates.
11. `COMPLETION CRITERIA`: Conditions required before signaling task completion.
12. `FAILURE CONDITIONS`: Specific triggers for reporting failure to the recovery engine.

## Agent Contracts Index (22 Roles)

### Core Primary Agents (Phase 3 Taxonomy)
- [academic-orchestrator](../../.agents/agents/academic-orchestrator/contract.md): Task decomposition, delegation, state coordination.
- [research-agent](../../.agents/agents/research-agent/contract.md): Literature harvesting, research questions & design.
- [data-agent](../../.agents/agents/data-agent/contract.md): Data ingestion, Little's MCAR & screening.
- [statistics-agent](../../.agents/agents/statistics-agent/contract.md): Statistical modeling, R/Python calculation & tables.
- [writing-agent](../../.agents/agents/writing-agent/contract.md): 5-part epistemic chapter prose & APA 7 presentation.
- [validation-agent](../../.agents/agents/validation-agent/contract.md): Adversarial quality gatekeeper & Viva Voce defense simulation.

### Specialized Domain Agents
- [academic-writer](../../.agents/agents/academic-writer/contract.md): Master chapter drafter and Persian academic prose specialist.
- [data-curator](../../.agents/agents/data-curator/contract.md): Deep missingness and Mahalanobis D2 outlier specialist.
- [digital-saber](../../.agents/agents/digital-saber/contract.md): Cognitive Twin of Saber Ghaderi & project principal.
- [evidence-auditor](../../.agents/agents/evidence-auditor/contract.md): In-text citation reconciliation & Irandoc audit.
- [final-judge](../../.agents/agents/final-judge/contract.md): Dissertation defense committee simulator.
- [intervention-designer](../../.agents/agents/intervention-designer/contract.md): Clinical manual & psychological intervention protocol architect.
- [journal-strategist](../../.agents/agents/journal-strategist/contract.md): WoS/Scopus target journal extraction & manuscript packaging.
- [literature-expert](../../.agents/agents/literature-expert/contract.md): Multi-database literature harvesting & science mapping.
- [longitudinal-modmed-expert](../../.agents/agents/longitudinal-modmed-expert/contract.md): 3-wave longitudinal moderated mediation specialist.
- [meta-analyst](../../.agents/agents/meta-analyst/contract.md): PRISMA 2020 systematic review & Cochrane RoB 2 meta-analyst.
- [methodology-expert](../../.agents/agents/methodology-expert/contract.md): Research design & G*Power sampling auditor.
- [psychometric-expert](../../.agents/agents/psychometric-expert/contract.md): CVR/CVI, CTT, IRT, EFA & CFA construct validator.
- [qualitative-analyst](../../.agents/agents/qualitative-analyst/contract.md): Reflexive Thematic Analysis & Grounded Theory specialist.
- [results-auditor](../../.agents/agents/results-auditor/contract.md): APA 7 numerical precision & OpenXML OMML math auditor.
- [statistical-auditor](../../.agents/agents/statistical-auditor/contract.md): Adversarial degrees-of-freedom & MSAI scoring auditor.
- [statistical-expert](../../.agents/agents/statistical-expert/contract.md): Statistical hypothesis testing planner & execution architect.
