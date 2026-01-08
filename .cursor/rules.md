# AI Agent Rules for Adiyogi LangChain

**MANDATORY**: Read this file and SPEC.md before making any changes.

---

## Workflow (Follow Every Time)

```
1. Read this file (.cursor/rules.md)
2. Read SPEC.md
3. Check relevant ADRs in docs/adr/
4. Create plan and get user approval
5. Execute approved plan only
6. Verify against CHECKLIST.md before commit
7. Commit with descriptive message
```

---

## Mandatory Checks Before Any Change

- [ ] Read SPEC.md
- [ ] Check if change conflicts with existing ADRs
- [ ] Verify no prohibited patterns are introduced
- [ ] Get explicit approval for architectural changes

---

## Prohibited Actions

### NEVER Do These Without Explicit Approval:
1. Add `export KEY=value` commands to documentation
2. Use localStorage or sessionStorage
3. Load .env files with `load_dotenv()`
4. Hardcode API keys or secrets
5. Create new packages without team assignment
6. Change environment variable source (must be Lambda)

### If You're About to Do Something Prohibited:
1. STOP
2. Ask user for clarification
3. Reference the relevant ADR
4. Get explicit approval

---

## Files to Reference

| File | When to Read |
|------|--------------|
| `SPEC.md` | Before ANY change |
| `CHECKLIST.md` | Before ANY commit |
| `docs/adr/*.md` | When making architectural decisions |
| `README.md` | When updating documentation |

---

## Key Decisions (Quick Reference)

| Decision | ADR | Rule |
|----------|-----|------|
| API Keys | ADR-001 | Lambda environment variables ONLY |
| Data Storage | - | No localStorage, use Supabase |
| Local Dev | ADR-001 | Use SAM with env.json |

---

## Before Committing

Run through CHECKLIST.md:
1. No prohibited patterns?
2. SPEC.md requirements met?
3. ADR created for new decisions?
4. Tests added?
5. Documentation updated?

---

## When Uncertain

1. Ask the user
2. Reference SPEC.md
3. Check existing ADRs
4. Do NOT assume or default to "developer convenience"

---

## Remember

> "Lambda environment variables ONLY. No exceptions without a new ADR."
