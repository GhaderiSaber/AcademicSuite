# 06. Practical Blueprints & Templates

This document provides production-ready, copy-pasteable configuration blueprints and code templates for creating and orchestrating agents and subagents in Google Antigravity.

---

## 1. Declarative Subagent Definitions

### 1.1 Read-Only Security Auditor Subagent
Place at: `.agents/agents/security-auditor.md`

```markdown
---
name: security-auditor
description: Specialized security auditor. Audits codebase changes for OWASP Top 10 vulnerabilities, leaked credentials, and unsafe shell execution.
role: Application Security Auditor
model: pro
subagent: true
mainAgent: false
tools:
  - view_file
  - grep_search
  - find_by_name
skills:
  - security-scanner
---

# Security Auditor Persona & Guidelines

You are an adversarial Application Security Auditor.
Your mandate is to detect and flag vulnerabilities before changes are merged.

## Evaluation Checklist:
1. **Secret & Credential Leakage**: Check for API keys, bearer tokens, or database passwords in source code.
2. **Injection Vulnerabilities**: Inspect raw SQL queries, shell concatenations, and unsanitized HTML/eval executions.
3. **Least Privilege**: Verify that newly introduced modules do not request excessive permissions.
4. **Audit Reporting**: Output findings strictly in an APA/Security table:
   - Severity: CRITICAL | HIGH | MEDIUM | LOW
   - File Path & Line Numbers
   - Vulnerability Description
   - Recommended Patch
```

---

### 1.2 Isolated Component Builder Subagent
Place at: `.agents/agents/component-builder.md`

```markdown
---
name: component-builder
description: Frontend UI engineer. Implements responsive web components using React, TypeScript, and Tailwind CSS.
role: UI Component Builder
model: flash
subagent: true
mainAgent: false
tools:
  - view_file
  - replace_file_content
  - write_to_file
  - run_command
skills:
  - generative_ui
---

# Component Builder Instructions

You are a Senior Frontend Specialist.
When implementing components:
1. Adhere strictly to the project's design tokens and Tailwind configuration.
2. Ensure full TypeScript strict typing (zero `any` types).
3. Validate accessibility compliance (ARIA attributes, semantic HTML).
4. Run `npm test -- <component>` to ensure zero regressions before completing.
```

---

## 2. Dynamic Runtime Invocation Schemas

### 2.1 Concurrent Multi-Agent Dispatch (`invoke_subagent`)
```json
{
  "Subagents": [
    {
      "TypeName": "security-auditor",
      "Role": "Auth Module Auditor",
      "Prompt": "Perform a comprehensive security audit of src/auth/jwt_service.py. Pay particular attention to algorithm confusion and token expiration checks.",
      "Model": "pro",
      "Workspace": "inherit"
    },
    {
      "TypeName": "component-builder",
      "Role": "Login Modal Refactorer",
      "Prompt": "Refactor src/components/LoginModal.tsx to support OAuth2 redirect flows.",
      "Model": "flash",
      "Workspace": "branch"
    }
  ],
  "toolAction": "Dispatching subagents",
  "toolSummary": "Concurrent security audit and UI refactor"
}
```

### 2.2 Subagent Lifecycle Inspection (`manage_subagents`)
```json
{
  "Action": "list",
  "toolAction": "Listing subagents",
  "toolSummary": "Inspecting active subagent statuses"
}
```

### 2.3 Terminating Errored Subagents (`manage_subagents`)
```json
{
  "Action": "kill",
  "ConversationIds": ["subagent-conv-uuid-12345"],
  "toolAction": "Terminating subagent",
  "toolSummary": "Canceling unresponsive subagent execution"
}
```

---

## 3. Programmatic Python SDK Pipeline

The following script demonstrates a complete multi-tier agent hierarchy using `google-antigravity`:

```python
"""
multi_tier_pipeline.py
Demonstrates multi-tier subagent hierarchy and execution in Google Antigravity Python SDK.
"""

import asyncio
import sys
from google.antigravity import Agent, LocalAgentConfig, types

def create_pipeline_config() -> LocalAgentConfig:
    # Tier 2: Leaf Worker (Read-Only Codebase Explorer)
    code_explorer = types.SubagentConfig(
        name="explorer",
        description="Searches codebase for symbol definitions, call hierarchies, and schemas.",
        system_instructions="You are a read-only codebase explorer. Extract precise file paths and lines.",
        capabilities=types.SubagentCapabilities(
            enabled_tools=[
                types.BuiltinTools.VIEW_FILE,
                types.BuiltinTools.GREP_SEARCH,
                types.BuiltinTools.FIND_BY_NAME,
            ],
            agent_behavior=types.AgentBehavior.AUTONOMOUS,
        ),
    )

    # Tier 1: Intermediate Subagent (Refactoring Specialist)
    refactoring_lead = types.SubagentConfig(
        name="refactoring_lead",
        description="Plans and coordinates code refactoring across multiple files.",
        system_instructions="You are a Principal Software Engineer overseeing code modernization.",
        capabilities=types.SubagentCapabilities(
            enabled_tools=[
                types.BuiltinTools.VIEW_FILE,
                types.BuiltinTools.WRITE_TO_FILE,
                types.BuiltinTools.REPLACE_FILE_CONTENT,
                types.BuiltinTools.START_SUBAGENT,
            ],
            allowed_subagents=["explorer"],
            agent_behavior=types.AgentBehavior.AUTONOMOUS,
        ),
    )

    # Tier 0: Primary Lead Orchestrator
    return LocalAgentConfig(
        model="gemini-3.8-pro",
        system_instructions="You are the Executive Engineering Orchestrator coordinating software evolution.",
        subagents=[refactoring_lead, code_explorer],
        capabilities=types.CapabilitiesConfig(
            enable_subagents=True,
            max_subagent_depth=2,
            allowed_subagents=["refactoring_lead"],
        ),
        budget_config=types.BudgetConfig(
            max_model_calls=40,
            max_tool_calls=100,
            max_total_tokens=500_000,
        ),
    )

async def main():
    config = create_pipeline_config()
    print("Launching Antigravity Multi-Tier Agent Pipeline...")
    
    async with Agent(config=config) as agent:
        response = await agent.chat(
            "Audit the database connection pool in src/db/pool.py and propose an async-compatible upgrade."
        )
        
        # Stream response in real time
        async for token in response:
            sys.stdout.write(token)
            sys.stdout.flush()
        print("\n\nPipeline execution finished successfully.")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 4. Deterministic Quality Gate Script (`Stop` Hook)

Place at: `.agents/verification/stop_gate.py`

```python
#!/usr/bin/env python3
"""
stop_gate.py
Mechanical Stop hook verifying test results and git working tree cleanliness.
"""

import json
import subprocess
import sys

def main():
    # 1. Check for uncommitted git changes
    git_status = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True,
        text=True
    ).stdout.strip()
    
    if git_status:
        # Block agent completion and force it to commit or clean up
        decision = {
            "decision": "continue",
            "message": "Git working tree is dirty. Stage and commit your modifications before concluding."
        }
        print(json.dumps(decision))
        return

    # 2. Allow turn completion
    print(json.dumps({"decision": "allow"}))

if __name__ == "__main__":
    main()
```
