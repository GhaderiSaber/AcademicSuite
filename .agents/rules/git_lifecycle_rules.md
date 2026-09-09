# Git Lifecycle Rules for AI Agents (Commit & Push Automation)

This rule governs how AI agents interact with the Git version control system in this repository (`GhaderiSaber/AcademicSuite`).

---

## 1. Mandatory End-of-Turn Automation

Whenever an agent finishes executing a user request, completing a task, making code modifications, or authoring documentation:
1. **Never Exit with a Dirty Working Tree**:
   Leaving modified, untracked, or uncommitted files behind is strictly prohibited.
2. **Execute Staging & Verification**:
   ```bash
   git status
   ```
   Stage all modified, added, and relevant skill/code/doc files:
   ```bash
   git add .agents/ AGENTS.md README.md ...
   ```
3. **Commit with Semantic Conventional Format**:
   Write a clear, concise commit message following standard types:
   - `feat(<scope>)`: New capability, script, or presentation path
   - `fix(<scope>)`: Bug fix, typography repair, or equation adjustment
   - `docs(<scope>)`: Updating AGENTS.md, SKILL.md, or guides
   - `refactor(<scope>)`: Code reorganization or performance improvement
   
   *Example*:
   ```bash
   git commit -m "feat(presentation): add tri-path selection (html, pptx, google_slides) and auto-sync"
   ```

4. **Push Immediately to Remote**:
   Push the committed changes to the GitHub remote repository:
   ```bash
   git push origin main
   ```
5. **Verify Clean Synchronization**:
   Confirm that `git status` reports:
   ```text
   On branch main
   Your branch is up to date with 'origin/main'.
   nothing to commit, working tree clean
   ```

---

## 2. Respect for Research Data & Gitignore

- Never stage raw participant SPSS files (`.sav`), student research drafts, or temporary large files that belong in `.gitignore`.
- Only commit agent code, skills, scripts, rules, documentation, and verified templates.
