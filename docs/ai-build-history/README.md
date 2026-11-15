# FINN AI build history

This folder provides the actual user/assistant conversation used to build and deploy this submission, plus a separately labeled retrospective. It is not an edited replacement for the dialogue and does not claim that the applicant independently wrote the AI-generated implementation.

- [Original conversation — readable text export](conversation.md)
- [Original conversation — machine-readable messages](conversation.json)
- [Export scope, snapshot time, checksum and tool invocation index](export-manifest.json)
- [Build retrospective — a summary, not a transcript](../build-retrospective.md)
- [Validation results and limitations](../validation.md)

The exported dialogue retains original wording, including troubleshooting, uncertainty and requests to change the presentation of the history. It is a time-bounded snapshot from the local Codex session, not an account-wide ChatGPT export. System/developer instructions, internal reasoning, environment context and raw tool inputs/outputs are excluded. The manifest documents those categories. Other ChatGPT conversations, if any, are not accessible through this export and are not represented here.

The repository's [export script](../export_build_history.py) reproduces the transformation when provided the selected local session JSONL. The machine-readable file's checksum detects changes to this snapshot; it is not an independent signature from the chat provider.

## Evidence in the repository

| Commit | Result |
| --- | --- |
| [`d500898`](https://github.com/praveen5085/enam_founding_ai_assignment/commit/d500898) | FINN application, initial regression suite, frontend, lockfiles, documentation and CI |
| [`a694d57`](https://github.com/praveen5085/enam_founding_ai_assignment/commit/a694d57) | Single-origin Render deployment, static frontend export and hosting tests |
| [`9c841bd`](https://github.com/praveen5085/enam_founding_ai_assignment/commit/9c841bd) | Verified deployed links, hosted HTTP/mobile-viewport checks and submission documentation |

Live application: https://finn-enam-praveen.onrender.com

The coding agent performed the implementation and automated checks. The applicant supplied the specification, requested the assignment comparison and deployment, completed Render account interactions and supplied the live URL. No claim is made that the applicant manually authored all generated code or personally executed every check.
