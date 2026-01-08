# AI Agent Rules

**Project:** Adiyogi LangChain  
**Version:** 1.0

These rules are automatically loaded by Cursor. Follow them on every interaction.

---

## Mandatory Workflow

```
1. Read SPEC.md (ALWAYS)
2. Check relevant ADRs in docs/adr/
3. Create plan (get user approval)
4. Execute only after approval
5. Verify against CHECKLIST.md
6. Commit with proper message
```

---

## Before ANY Change

You MUST:

1. **Read `/SPEC.md`** - Contains requirements and prohibited patterns
2. **Check `/docs/adr/`** - Contains architectural decisions
3. **Create a plan** - Get user approval before executing
4. **Verify compliance** - Check against CHECKLIST.md before committing

---

## Prohibited Actions

### Code

```python
# ❌ NEVER DO THIS
localStorage.setItem()
sessionStorage.setItem()
API_KEY = "hardcoded"
load_dotenv()
from dotenv import load_dotenv
```

### Documentation

```markdown
# ❌ NEVER WRITE THIS
export GEMINI_API_KEY=xxx
echo "KEY=value" >> ~/.zshrc
Create .env file with...
```

### Without Approval

- Adding new packages/dependencies
- Changing architecture
- Modifying SPEC.md or ADRs
- Deploying to production

---

## Required Patterns

### API Keys

```python
# ✅ ALWAYS USE THIS
import os
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
```

### Local Development

```markdown
# ✅ ALWAYS SUGGEST THIS
Use SAM local with env.json:
sam local start-api --env-vars env.json
```

---

## Key Files to Reference

| File | Purpose | When to Read |
|------|---------|--------------|
| `SPEC.md` | Requirements | Every task |
| `docs/adr/*.md` | Decisions | Related changes |
| `CHECKLIST.md` | Verification | Before commit |
| `README.md` | Project overview | New features |

---

## Commit Message Format

```
type: description

[Body explaining what and why]

Refs: ADR-NNN (if applicable)
```

Types: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`

---

## When Unsure

1. Ask the user for clarification
2. Reference SPEC.md and ADRs
3. Propose options with pros/cons
4. Wait for approval before acting

---

## Compliance Check

Before completing any task, verify:

- [ ] SPEC.md requirements followed
- [ ] No prohibited patterns used
- [ ] ADR created for new decisions
- [ ] User approved the plan
- [ ] CHECKLIST.md items verified
