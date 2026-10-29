# Browser checks

Start FastAPI on 127.0.0.1:8000 and Vite on localhost:5173. The real-backend test expects the initial empty complaint database and no Gmail token (the default development setup); it performs a sync request and checks the real missing-authorization response. Do not run that test against an authorized/live inbox.

```sh
cd frontend
npx playwright install chromium
npm run test:e2e
```

For an already connected workspace, run only fixture-based checks:

```sh
npm run test:e2e -- --grep 'fixture-based|backend errors'
```

The populated-detail and backend-error tests intercept API responses with explicit fixtures. They verify UI behavior and escaping only, not live Google integrations. Each test runs at desktop and mobile sizes. No test sends emails or executes refunds.
