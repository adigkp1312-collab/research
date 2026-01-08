# Pre-Commit Checklist

**MANDATORY**: Verify ALL items before every commit.

---

## 1. Specification Compliance

- [ ] Read SPEC.md before making changes
- [ ] No prohibited patterns introduced
- [ ] API keys only from Lambda environment variables
- [ ] No localStorage/sessionStorage usage
- [ ] No hardcoded secrets

---

## 2. Documentation Alignment

- [ ] No `export KEY=value` commands in README
- [ ] Lambda Console/CLI instructions for key setup
- [ ] Documentation matches SPEC.md requirements

---

## 3. Architecture Decisions

- [ ] New architectural decisions have ADR
- [ ] ADR approved before implementation
- [ ] docs/adr/README.md index updated

---

## 4. Code Quality

- [ ] Tests added for new functionality
- [ ] Existing tests pass
- [ ] No linter errors
- [ ] Type checking passes (if applicable)

---

## 5. Team Ownership

- [ ] Changes in correct package per SPEC.md
- [ ] Team ownership respected
- [ ] Cross-team changes discussed

---

## 6. Security

- [ ] No API keys in source code
- [ ] No secrets in commit
- [ ] .gitignore includes sensitive files
- [ ] env.json not committed

---

## Quick Verification Commands

```bash
# Check for prohibited patterns
grep -r "localStorage" packages/ --include="*.ts" --include="*.tsx"
grep -r "export GEMINI_API_KEY" .
grep -r "load_dotenv" packages/ --include="*.py"

# Run tests
./scripts/test-all.sh

# Check git status
git diff --cached --name-only
```

---

## If Any Item Fails

1. STOP - Do not commit
2. Fix the issue
3. Re-verify checklist
4. Then commit

---

## Commit Message Format

```
type: Short description

- Detail 1
- Detail 2

Refs: ADR-NNN (if applicable)
```

Types: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`
