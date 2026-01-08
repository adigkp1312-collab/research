# Testing Package

**Team:** QA

End-to-end and integration tests for cross-package testing.

## Structure

```
testing/
├── e2e/              # End-to-end tests (Playwright)
├── integration/      # Cross-package integration tests
├── fixtures/         # Shared test data
└── utils/            # Test utilities
```

## E2E Tests

Full user flow testing with Playwright:

```bash
cd packages/testing
npm install
npx playwright test
```

## Integration Tests

Cross-package integration tests:

```bash
cd packages/testing
pytest integration/
```

## Fixtures

Shared test data and mock responses:
- `fixtures/mock-responses.json` - Sample API responses
- `fixtures/test-sessions.json` - Test session data

## Test Utilities

Shared helpers:
- `utils/test-helpers.py` - Python test utilities
- `utils/test-helpers.ts` - TypeScript test utilities
