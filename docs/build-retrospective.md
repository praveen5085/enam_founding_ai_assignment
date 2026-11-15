# FINN build retrospective

This is a factual summary of the recorded AI-assisted process. It is not a rewritten conversation or a claim of unaided implementation. The [original user/assistant text export](ai-build-history/conversation.md) is preserved separately.

## Scope and execution

The applicant supplied a detailed specification for a mobile-first FINN prototype: Push, Pull and Network workflows, backend behavior, frontend requirements, regression cases, deployment documentation and a GitHub submission. Codex generated the implementation, installed dependencies, ran checks, committed and pushed the project. The applicant subsequently directed the agent to read the assignment PDFs, identify submission requirements and complete deployment.

The implementation focuses on a portfolio digest and market radar, quarterly guidance-versus-delivery research, and a fictional professional network. Synthetic filings and profiles make the product demonstrable without collecting personal network information. Yahoo observations are live; financial research evidence is either entirely live or entirely synthetic within a response.

## Decisions reflected in the implementation

- FastAPI owns external fetching, model credentials, Pydantic validation and Decimal comparisons. The Next.js frontend calls those APIs and cancels superseded requests.
- Market prices use one batched provider call in a thread. Completed IST sessions determine the trigger and ten-session volume baseline; failed symbols remain retryable.
- Extraction and synthesis are separate configurable model calls. `gpt-4.1-mini` is the extraction default; `gpt-4.1` is the narrative default. Missing or failed synthesis preserves validated numerical comparisons. No live OpenAI call was verified during this submission.
- Primary-source research uses an approved host registry, validates redirects and bounds download size, concurrency and time. Quotes and cited numbers are checked locally; guidance boundary calculations do not depend on the LLM doing arithmetic.
- Explicit graph edges supply connection paths. Name/employer/school/sector overlap contributes a search reason but does not create a relationship edge. Current and former employers contribute to rolling 24-hour reconnect prompts.
- The hosted demo uses a static Next.js export served by FastAPI from one Render service. This reduces deployment configuration and makes API calls same-origin. The ordinary two-process development setup remains available.

## What went wrong and what changed

The first dependency audit reported PostCSS advisories. A patched transitive override was added, and the subsequent npm audit reported no vulnerabilities. This result applies to the tested dependency set, not a complete application security audit.

An early production-start check exposed a mismatch between Next.js standalone output and the documented start command. The configuration was corrected before the final build. Deployment then moved to a single Python container with the exported frontend.

The repository was pushed before hosting was available. The conversation records several exchanges needed to distinguish signing into Render from connecting an app integration. Rather than treating a Git push as publication, the project gained a Render Blueprint; the applicant approved it in Render and supplied the resulting URL. The coding agent then verified the actual hosted service.

Live primary-document discovery did not return an approved set in the TCS probe. That remains unresolved. Research therefore showed labeled synthetic raw-document fixtures and deterministic parsing, with an explicit unavailable narrative state without an API key. Mocked active-key/schema failures and synthesis preservation verify failure behavior, not live model quality.

## What was verified

Fourteen backend regression tests passed. Frontend typechecking, production builds and the same-origin static export passed. GitHub Actions passed on Ubuntu. The repository was independently confirmed public. The hosted app served its HTML and all six JavaScript assets, returned ten seven-day filings, supported network search and returned four synthetic research quarters. The hosted market endpoint returned observations for all fifteen symbols.

Headless Edge/Playwright exercised the hosted app at a 390 × 844 touch/mobile viewport: two complete results tables, four research cards and fallback labels, first-open Network loading and a Pharma/IT search. There was no horizontal overflow at 390px or 1440px and no JavaScript or API error in that run. A mobile feed screenshot was visually inspected. This is emulation, not physical-phone testing. See the [validation record](validation.md) for the precise limits.

## Deliberate omissions and next work

The submission has no brokerage integration, automated trading, scheduled notification delivery or real contact ingestion. It stores no personal network records. Authentication, tenant isolation, consent/revocation, retention/deletion, durable jobs and production audit trails are proposed controls rather than implemented guarantees.

The next engineering priority is reliable live filing/transcript discovery and stronger semantic checks for guidance target periods, units and conversions, followed by a verified live extraction/synthesis run. Production hardening should then add authentication and per-investor access boundaries, explicit consent and retention policies, background refresh, exchange-session calendars, provider monitoring and broader device testing.
