# FINN

[Live application](https://finn-enam-praveen.onrender.com) · [Public GitHub repository](https://github.com/praveen5085/enam_founding_ai_assignment)

A mobile-first investment intelligence workbench for the ENAM Founding AI Engineer challenge. Feed joins prioritized filings and configurable market signals. Research compares guidance with reported delivery using primary documents. Network adds explicit relationship paths and contextual search.

## Run on Windows PowerShell

Requires Python 3.11+ (tested with 3.12), Node 22+ (tested with 26), and Git. From this repository:

```powershell
Set-Location C:\Users\prave\Downloads\enam_founding_ai_assignment
python -m venv .venv
.\.venv\Scripts\python -m pip install -r backend/requirements.lock
Copy-Item backend/.env.example backend/.env
Copy-Item frontend/.env.example frontend/.env.local
.\.venv\Scripts\python -m uvicorn backend.main:app --reload --port 8000
```

In a second PowerShell window:

```powershell
Set-Location C:\Users\prave\Downloads\enam_founding_ai_assignment\frontend
npm ci
npm run dev
```

Open http://localhost:3000. API documentation: http://localhost:8000/docs. No environment activation or PowerShell execution-policy changes are needed. No OpenAI key is required for the synthetic research demo. Discovery can take up to 25 seconds before fallback. Configure `OPENAI_API_KEY` only in `backend/.env` for model calls; never use a `NEXT_PUBLIC_` variable for secrets.

## Architecture and data contracts

`frontend/app` is a Next.js App Router client with Tailwind and custom dark responsive styles. All three tabs call FastAPI. Aborted superseded fetches prevent stale responses from replacing current filters. Network automatically loads once first opened. Research requests begin when its tab opens. Source excerpts, routine filings and biographies expand inline.

`backend/main.py` validates endpoint parameters and exposes:

| Endpoint | Pipeline |
| --- | --- |
| `/api/eod?vol_threshold=2&price_threshold=3` | One batched `yf.download` in `asyncio.to_thread`, 15 diverse symbols, IST completed-session filtering, preceding ten-session volume baseline and close-to-close change. Independent strictly-greater volume and absolute-price alerts. Successful observations cached for five minutes; failures retried. Each observation includes trigger date, baseline dates and provider alias. |
| `/api/feed?hours=24` | Ten synthetic filings distributed across 1–150 hours; select 24, 72 or 168 hours. Material categories precede low-priority unclassified items, routine ballot/meeting notices are separate. TCS and Asian Paints have four-row result cards computed from explicit current, prior-quarter and year-ago snapshots. Nonpositive bases yield null percentages. |
| `/api/network?q=Pharma%20or%20IT` | Twelve fictional professionals; weighted name, employer, former-employer, school, sector and role matching. Explicit first/second-degree edges; overlap never creates an edge. Identity candidates are labeled. Rolling UTC 24-hour reconnect events match current and former employers. |
| `/api/research/TCS?demo_fallback=true` | Syntax-valid NSE tickers accepted. Screener is a discovery index only. Approved original documents are fetched concurrently, extracted and validated; Decimal computes beats, misses and boundary deltas. An entire live-evidence attempt succeeds or a completely separate synthetic set is used. `false` returns controlled 503 for unavailable or noncomparable evidence. |

Aliases currently map ULTRATECH → ULTRACEMCO, ZOMATO → ETERNAL and TATAMOTORS → TMPV. These are explicit provider mappings, not claims that reorganized entities have identical economic history. Review mappings for corporate actions before production use. Price changes use unadjusted closes. The session filter assumes normal 15:30 IST closes; exchange holiday/special-session calendars are not implemented. A failed market call shows errors, never fabricated prices.

## Evidence and model routing

1. Bounded HTTPS discovery and original fetching: four concurrent downloads, 25-second request timeout, four redirects, 4 MiB per document, eight candidate documents. Every redirect is revalidated against exact approved hosts. PDF text uses PyMuPDF; HTML uses BeautifulSoup. TCS, Infosys, Asian Paints and Reliance company hosts are explicitly registered; exchange-hosted originals can serve any accepted ticker. Extend the reviewed registry for additional issuer hosts. No user-supplied URLs are fetched.
2. `EXTRACTION_MODEL` defaults to `gpt-4.1-mini`. Pydantic validates structured quarter/metric records, and Python checks normalized supporting quotes, source IDs, cited actuals and guidance bounds. Current and previous guidance citations must be distinct sources. Quarter labels need not appear literally inside the numerical quote. Comma formatting, case and whitespace are normalized; there is no percentage whitelist. Financial metadata from Screener or Yahoo never enters the research prompt.
3. Decimal compares each actual against explicit absolute guidance boundaries in INR crore. A missing individual bound yields “not comparable” when neither boundary exists. A missing comparable set fails the live attempt. Fiscal quarter indices enforce unique chronological quarters and preceding-quarter guidance attribution, accepting both Q2 FY2025 and FY2025 Q2 labels. Percentage-only revenue-growth or margin guidance is deliberately left unconverted rather than compared to absolute financial values without a supported conversion. Full semantic proof of source-quarter attribution and unit conversion remains a production validation gap.
4. `SYNTHESIS_MODEL` defaults to `gpt-4.1` and receives validated comparisons to produce promises-versus-delivery, recurring-divergence and tone-shift narrative. Failure preserves numbers and explicitly marks narrative unavailable.
5. Synthetic raw documents contain a documented repeated grammar: `Revenue actual INR crore 1020. Next quarter Revenue guidance INR crore 1035 to 1045.` EBITDA and PAT follow the same grammar. Five source documents support four reporting quarters and preceding guidance. Extraction is attempted with a key; otherwise a local regex parser handles this known grammar. No key means no LLM synthesis, stated in the response and UI. Synthetic financials never mix with live financials.

With a key, CFO enrichment extracts source-validated biographical facts; provider/schema/grounding failure uses a conservative deterministic summary and preserves the original filing. A summary composed from multiple grounded facts need not be a contiguous source substring. All people, biographies and announcements are synthetic and labeled; the CFO profile is fictional even when a real company name supplies context.

## Configuration and deployment

For a single public application URL, use the root `Dockerfile` and `render.yaml`: the static Next.js export and FastAPI API share one host. See [deployment instructions](docs/deployment.md). A real hosting-account connection is required to create the service; a configuration file or Git push alone is not a deployed application.

`backend/.env.example` documents `OPENAI_API_KEY`, extraction/synthesis models and `ALLOWED_ORIGINS`. `frontend/.env.example` documents `NEXT_PUBLIC_API_URL`. Origins are read using `os.getenv("ALLOWED_ORIGINS", "*").split(",")`; use comma-separated exact origins without spaces. CORS is not authentication.

For deployment set `ALLOWED_ORIGINS=https://your-frontend.example` and build the frontend with `NEXT_PUBLIC_API_URL=https://your-api.example`. This public variable is embedded at build time. Never put keys in frontend build args. Terminate TLS at your platform ingress. Configure backend command `uvicorn backend.main:app --host 0.0.0.0 --port 8000` and health path `/health`. Deploy the frontend with `npm ci`, `npm run build`, `npm start`.

Docker deployment configuration is provided:

```powershell
docker compose up --build
```

The frontend browser uses localhost:8000 in the local compose setup; production must supply the externally accessible API origin. Docker packaging is provided but requires a Docker engine to validate locally. No hosted deployment is implied by a GitHub push.

## Validation

```powershell
.\.venv\Scripts\python -m pytest -q
Set-Location frontend
npm run typecheck
npm run build
npm audit
```

The regression suite mocks providers and active-key model failures; these are not claims of verified live OpenAI or exchange integrations. It covers provider/schema failures, normalized evidence/reversed label formats, noncontiguous biography summaries, result cards, UTC reconnects crossing IST midnight, former employers, batched market retry, fallback/live-only behavior, Decimal handling and narrative-failure preservation. Optional real-provider probes: `.\.venv\Scripts\python -m docs.smoke` from the root. See `docs/validation.md` for execution results.

Both dependency lockfiles are committed: npm's `package-lock.json`, and fully pinned Python `requirements.lock` generated from the tested environment. The Python lock was resolved on Windows/Python 3.12 and is not a cross-platform hash lock. Direct dependency intent is retained in `requirements.txt`. PostCSS is overridden to a patched version.

## Privacy, limits and production work

Implemented: synthetic-only network, explicit graph relationships, no address-book ingestion, no persistent user storage, backend-only model key, document host/redirect/size/time limits, typed inputs, successful-only market cache and citation/numeric checks. Documents sent to OpenAI contain public issuer evidence; review provider terms before real use.

Proposed production controls, **not implemented**: authentication, authorization, tenant isolation, consent and revocation, retention/deletion policies, encryption at rest, audit trails, rate limiting, abuse controls and user-specific portfolio storage. This is a single-process demonstration, unsuitable for public multi-user exposure without those controls. Additional work includes durable jobs, provider contracts/retries, exchange calendars, SSRF DNS/IP hardening, robust document chronology/unit verification, exhaustive semantic citation validation, observability and scalable caching. No real professional relationship is asserted and no outreach is sent. Alerts are on-demand dashboard observations; scheduled push notifications, trading, broker integration and personal financial advice are deliberately omitted.
