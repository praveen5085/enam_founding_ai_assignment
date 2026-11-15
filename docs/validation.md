# Validation record

Executed on Windows with Python 3.12.10 and Node 26.13.1.

- Backend: 14 regression tests passed, including same-origin static hosting and API-route precedence. Providers and active-key model calls are mocked in regression tests. Six dependency deprecation warnings remain (AnyIO/Starlette and PyMuPDF SWIG types).
- Frontend: `npm run typecheck` passed; optimized Next.js production build passed.
- Dependency audit: `npm audit` reports zero vulnerabilities after pinning the transitive PostCSS override to 8.5.33.
- Real Yahoo probe: all 15 configured portfolio symbols returned successful observations; no per-symbol errors in that probe. Availability is provider-dependent.
- Real TCS discovery probe: no approved primary documents discovered. The live research path is implemented but live extraction/synthesis was **not verified**. No real OpenAI call was made. Schema/provider failures and synthesis preservation were verified with mocks.
- API HTTP smoke: health, seven-day feed, network query and synthetic research tested against a running Uvicorn server. Production frontend HTML checked over HTTP. This is not browser interaction or visual QA.
- Dockerfiles and compose configuration supplied; Docker image builds and hosted deployment not verified in this environment.
- Submission hosting preparation: the static Next.js export with same-origin API configuration builds successfully. GitHub's unauthenticated repository API confirms `private: false` and `visibility: public`; the initial GitHub Actions run passed on Ubuntu. Actual Render publication still requires an authenticated hosting connection and has not been claimed complete.

The synthetic demo contains four validated reporting quarters, source excerpts and deterministic comparisons without an API key. It explicitly reports that LLM narrative synthesis did not occur.
