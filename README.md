# Brief Ledger

A local workspace for freelancers: client notes → source-linked scope → human-priced draft estimate.

Built from scratch on October 15, 2026 for Hacktoberfest Week 2: **Side Hustle**.
The intended customer is an independent web designer or developer who repeatedly
turns informal client requests into estimates. This is a prototype; there are no
paying customers or measured business outcomes yet.

## Run locally

Requirements: **Python 3.11+**, [Ollama](https://ollama.com), and enough memory for
Qwen3 4B. There are **no Python or JavaScript packages to install**.

```sh
ollama pull qwen3:4b
python app.py
```

Keep Ollama running. Open **http://127.0.0.1:8765**. First-time setup downloads the
model; generation thereafter calls Ollama's loopback API. Inference can take a
few minutes on a CPU. The model request times out after five minutes.

On Windows, the Ollama desktop application normally starts its service. On a
system without a running service, run `ollama serve` in another terminal.

Optional environment variables: `OLLAMA_MODEL` (default `qwen3:4b`) and `PORT`
(default `8765`). Only Qwen3 4B is tested. The Ollama endpoint is fixed to
`127.0.0.1:11434` so changing the model does not change the inference destination.

## Use it

1. Enter a project name and paste the client's original notes, up to 6,000 characters.
2. Draft the scope. Review every task against its verbatim source quote. Edit task wording or remove incorrect items as needed.
3. Check explicit exclusions and edit suggested clarification questions. A matching quote proves the words occur in the source; it does **not** prove the model interpreted them correctly or found every request. Conflicting requests are particularly error-prone: a live test misclassified an unresolved payment request. Read the full notes before pricing.
4. Enter your own hours per item and hourly rate. Review the scope and open questions, then check the review box.
5. Calculate and download a text draft. Confirm unresolved questions with the client before agreeing on the work.

The sample brief is fictional. There is no email sending, payment collection,
invoice accounting, tax calculation, cloud sync, or client portal.

## How it works

```text
Browser → Python HTTP server → Ollama → Qwen3 4B
                          ↓
             Validate JSON and source quotes
                          ↓
           Human reviews scope, hours, and rate
                          ↓
          Decimal calculations → text download
```

Ollama receives a JSON schema. The server validates every returned item, limits
list lengths, rejects truncated or unreadable output, and requires each scope
and exclusion quote to occur in the submitted notes. Suggested questions are
clearly separate from assertions about the brief. The model supplies no rates or
hours. The server calculates each line with decimal arithmetic and half-up
rounding to two places, then sums the rounded lines. Browser-supplied totals
are ignored.

Client notes and drafts stay in tab/server/model memory; this app has no database,
analytics, external fonts, or cloud inference calls. It does not persist project
history. The downloaded draft is saved wherever your browser saves downloads.
Ollama is separate software; inspect its configuration and logging before using
confidential material. Reloading the tab loses the working draft.

The server binds only to loopback and rejects cross-origin JSON requests. It is
a local development application built with Python's `http.server`, not a public
production server. Do not expose it to the internet.

## Checks

```sh
python -m unittest -v
node --check web/app.js
```

Node is optional and used only for the JavaScript syntax check. Runtime does not
require Node, a package manager, or a build step. Tests cover source evidence,
review gates, stale scope, decimal totals and rounding, invalid numeric inputs,
model failure responses, origin checks, and static assets. See
`submission/verification.md` for real-model and browser evidence.

## Credits and license

Application code: **MIT**, see [LICENSE](LICENSE). Model weights are downloaded
separately and retain the [Qwen3 4B license](https://huggingface.co/Qwen/Qwen3-4B)
(Apache 2.0). Ollama is a separate runtime.

Two DEV posts informed the validation boundary: [Building an AI project estimator
with prices the model cannot invent](https://dev.to/vaynerov/building-an-ai-project-estimator-with-prices-the-model-cannot-invent-53o9)
and [Schema-Valid Isn't Correct: 4 Checks Before You Trust LLM Extraction](https://dev.to/michael_maurice/schema-valid-correct-4-checks-before-you-trust-llm-extraction-4n6f).
No source code was copied from them. Codex assisted with implementation,
verification, and the challenge write-up.
