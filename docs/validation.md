# Validation record

Executed on Windows with Python 3.12.10 and Node 26.13.1.

- Backend: 14 regression tests passed, including same-origin static hosting and API-route precedence. Providers and active-key model calls are mocked in regression tests. Six dependency deprecation warnings remain (AnyIO/Starlette and PyMuPDF SWIG types).
- Frontend: `npm run typecheck` passed; optimized Next.js production build passed.
- Dependency audit: `npm audit` reports zero vulnerabilities after pinning the transitive PostCSS override to 8.5.33.
- Real Yahoo probe: all 15 configured portfolio symbols returned successful observations; no per-symbol errors in that probe. Availability is provider-dependent.
- Real TCS discovery probe: no approved primary documents discovered. The live research path is implemented but live extraction/synthesis was **not verified**. No real OpenAI call was made. Schema/provider failures and synthesis preservation were verified with mocks.
- Live deployment: https://finn-enam-praveen.onrender.com, deployed by Render from application commit `a694d57` and verified on 15 November 2026. The root Dockerfile builds the Next.js static export and serves the real FastAPI backend on the same origin. The separate two-container compose deployment has not been built locally.
- Hosted HTTP smoke: `/health`, frontend HTML, all six JavaScript assets, seven-day feed (ten filings), network query and four-quarter synthetic research passed using `python -m docs.verify_deployment https://finn-enam-praveen.onrender.com`.
- Hosted market probe: all fifteen symbols returned observations from the Render-hosted API.
- Hosted browser QA: headless Microsoft Edge via Playwright at a 390 × 844 touch/mobile viewport. Verified seven-day feed and two four-row results tables; four research quarter cards and synthetic/narrative-unavailable labels; automatic first-open Network load (twelve profiles); Pharma/IT search (six matches). No JavaScript errors or failed API responses. No horizontal overflow at 390px or 1440px. The mobile feed screenshot was visually inspected. This is browser emulation, not testing on a physical phone.
- GitHub's unauthenticated repository API confirms `private: false` and `visibility: public`; the initial GitHub Actions run passed on Ubuntu.

The synthetic demo contains four validated reporting quarters, source excerpts and deterministic comparisons without an API key. It explicitly reports that LLM narrative synthesis did not occur.
