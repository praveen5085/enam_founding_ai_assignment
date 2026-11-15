# Public demo deployment

The root `Dockerfile` is the submission deployment. It builds the Next.js App Router frontend as a static export, then serves it alongside the real FastAPI API in a single Python container. There is no frontend API mock or browser-only substitute. A single external URL handles the page, JavaScript assets, `/api/*`, `/docs` and `/health`.

`NEXT_PUBLIC_API_URL=/` is embedded during the image build. The frontend removes the trailing slash, giving same-origin `/api/*` requests. Local development still defaults to `http://localhost:8000`. The ordinary Next.js server build and the original two-container compose setup remain available.

## Render

The root `render.yaml` declares one free Docker web service. The published repository is:

https://github.com/praveen5085/enam_founding_ai_assignment

To create it in your own authenticated Render account, use the repository's Blueprint:

https://dashboard.render.com/select-repo?type=blueprint&repo=https%3A%2F%2Fgithub.com%2Fpraveen5085%2Fenam_founding_ai_assignment

Review the free plan in the deployment preview, then create the Blueprint. No model key is required for the labeled synthetic demo. If desired, set `OPENAI_API_KEY` as a secret on the service's Environment page; do not add it to Git or to frontend variables.

Render supplies `PORT`, which the image's start command respects. `/health` is the readiness endpoint. `RENDER_EXTERNAL_URL` supplies the allowed CORS origin unless `ALLOWED_ORIGINS` is explicitly configured. Same-origin frontend calls do not require cross-origin permission. CORS is not authentication.

Render's free web services can sleep after 15 minutes without traffic. Expect a cold start when sharing the demo; open the link before the assessment. Provider/model availability is independent of hosting. All fallback states remain explicitly labeled. The app has no authentication or user data ingestion; network contacts and filings are fictional demonstration fixtures.

## Verify the actual deployed service

Do not treat a Blueprint URL or successful Git push as a deployed application. Wait for a successful Render deploy and use its returned `https://...onrender.com` URL. Then verify:

1. `/health` returns `{"status":"ok"}`.
2. `/` renders FINN and `_next` assets load.
3. `/api/feed?hours=168` returns ten filings in total.
4. `/api/network?q=Pharma%20or%20IT` returns profiles and explicit paths.
5. `/api/research/TCS` returns four quarters or a controlled error, with evidence mode visible.
6. The responsive app opens on a phone, and all tabs and controls work.

Record the real deployment URL and checks in `docs/validation.md` only after these checks. The public GitHub repository has been independently confirmed via GitHub's unauthenticated API (`private: false`, `visibility: public`).

Run the repeatable HTTP checks with `.\.venv\Scripts\python -m docs.verify_deployment https://your-service.onrender.com`. This checks real API responses and frontend script assets; it does not replace phone/browser testing.

References: [Blueprint specification](https://render.com/docs/blueprint-spec), [default environment variables](https://render.com/docs/environment-variables), [free-tier behavior](https://render.com/docs/free).
