# Git Lifecycle Specification (Directive 8)

Universal version control and automation standards across AcademicSuite.

---

## 1. Lifecycle Contracts

- **Directive 8 (Mandatory Git Lifecycle Invariant)**: Turn conclusion requires a completely clean working tree. Never end a session leaving uncommitted modifications. [Enforcement: Turn completion gate]
- **Semantic Conventional Commits**: Commit messages must follow conventional semantic types:
  - `feat(<scope>)`: New capability, script, or model
  - `fix(<scope>)`: Bug fix, typography repair, or numerical alignment
  - `docs(<scope>)`: Documentation, SKILL.md, or manual updates
  - `refactor(<scope>)`: Code or rule restructuring
- **Automated Remote Push**: Pushing to `origin main` is required upon committing changes.
- **Data Protection**: Raw participant data (`01_raw_inputs/`) and transient files must respect `.gitignore`.

---

## 2. Standard Execution Sequence
```bash
git status
git add <target_files>
git commit -m "<type>(<scope>): <concise description>"
git push origin main
git status  # verify 'nothing to commit, working tree clean'
```
