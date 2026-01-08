# Pre-Commit Checklist

Verify ALL items before committing changes.

---

## Requirements Compliance

- [ ] Read `SPEC.md` before starting
- [ ] Checked relevant ADRs in `docs/adr/`
- [ ] No prohibited patterns introduced (see below)

---

## Prohibited Patterns Check

### Code - Verify NONE of these exist:

```python
# Search for these - they should NOT exist
localStorage.setItem
sessionStorage.setItem
load_dotenv
from dotenv import
API_KEY = "sk-
GEMINI_API_KEY = "AI
```

### Documentation - Verify NONE of these exist:

```markdown
# Search for these - they should NOT exist
export GEMINI_API_KEY=
export LANGCHAIN_API_KEY=
echo ".*KEY.*" >> ~/
Create .env file
```

---

## Required Patterns Check

### API Keys - Verify this pattern is used:

```python
# This pattern MUST be used for all keys
os.environ.get('KEY_NAME', '')
```

### Local Dev - Verify SAM is documented:

```markdown
# Documentation should reference SAM, not export
sam local start-api --env-vars env.json
```

---

## Code Quality

- [ ] Tests added for new functionality
- [ ] Existing tests pass
- [ ] No linter errors
- [ ] Type hints added (Python)
- [ ] TypeScript types correct

---

## Documentation

- [ ] README updated if needed
- [ ] ADR created for architectural decisions
- [ ] Code comments for complex logic
- [ ] API docs updated (if API changed)

---

## Package Ownership

- [ ] Changes only in packages I'm authorized to modify
- [ ] Cross-package changes approved by relevant team

---

## Commit

- [ ] Commit message follows format: `type: description`
- [ ] References ADR if applicable: `Refs: ADR-001`
- [ ] No sensitive data in commit

---

## Quick Grep Commands

Run these to verify compliance:

```bash
# Check for prohibited patterns
grep -r "localStorage\|sessionStorage" packages/
grep -r "load_dotenv\|from dotenv" packages/
grep -r "export GEMINI_API_KEY" .
grep -r "API_KEY = \"" packages/

# Should return no results
```
