To: assessment@enam.com

Subject: IIT Delhi – Founding AI Engineer - 2027

Dear ENAM team,

Please find my submission, FINN: a mobile-first investment intelligence prototype connecting portfolio signals, financial research and professional context.

Live prototype: https://finn-enam-praveen.onrender.com

Public repository: https://github.com/praveen5085/enam_founding_ai_assignment

AI build history and retrospective: https://github.com/praveen5085/enam_founding_ai_assignment/tree/main/docs/ai-build-history

FINN provides three working workflows: a windowed portfolio digest with configurable end-of-day market alerts; four-quarter guidance-versus-delivery research with supporting excerpts; and a searchable synthetic professional network with explicit relationship paths and reconnect prompts. The CFO announcement embeds relevant network context directly in the feed.

The architecture uses FastAPI for fetching, validation and model calls, with a Next.js/TypeScript frontend. The deployed app serves the exported frontend and API from one Render service. Market data is fetched in a batch, with successful-only caching and IST session filtering. Research separates primary-document discovery, structured extraction and narrative synthesis. The model defaults are gpt-4.1-mini for extraction and gpt-4.1 for synthesis; Python validates cited evidence and uses Decimal for guidance comparisons. No autonomous outreach or trading takes place.

I used Codex for implementation and automated verification. The linked history preserves the original user/assistant messages, including deployment troubleshooting, with its export scope stated explicitly. A separate retrospective explains the decisions, corrections and remaining gaps.

Fourteen backend tests, frontend type/build checks and hosted HTTP checks passed. The live market endpoint returned observations for all fifteen symbols. Hosted browser checks exercised all three tabs at a phone-sized viewport. Filings, biographies and network profiles are fictional and labeled. Live primary-document discovery did not succeed in the verification run, so the demonstrated research uses a labeled synthetic fallback; live OpenAI extraction and synthesis are not claimed as verified.

The prototype collects no real contact data. Authentication, tenant isolation, consent, retention controls and scheduled push delivery are deliberately outside the implemented scope. My next priorities would be reliable live primary-source ingestion, stronger guidance/unit validation, followed by per-investor access controls and background refresh. The README distinguishes implemented safeguards from proposed production controls. The free hosting service may need a short cold start.

Thank you for reviewing my submission. I would welcome the opportunity to discuss the product and engineering choices.

Best regards,
Praveen Panwar
