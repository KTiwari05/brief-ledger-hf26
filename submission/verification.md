# Verification — October 15, 2026

## Automated and static checks

- `python -m unittest -v`: **12 passed** after the final application changes.
- `node --check web/app.js`: passed.
- `python -m py_compile app.py`: passed.
- `git diff --check`: passed before publication.
- No frontend compilation or package installation is needed to run the application.
- The HTTP tests require permission to open loopback sockets on this Windows host;
  the first sandboxed run was blocked by WinError 10013. The permitted rerun passed.

Tests cover fabricated source quotes for requested work and exclusions, invalid
scope, empty scope, human review, stale notes, invalid/negative/non-finite amounts,
per-line decimal rounding, browser totals being ignored, truncated/unreadable model
responses, cross-origin requests, model outage reporting, and asset routing.

## Real Qwen3 4B results

All briefs are fictional and were submitted to the running app's real Ollama path.
The application validation accepted only source quotes found in the supplied notes.

| Case | Result | Measured generation |
| --- | --- | --- |
| First bakery run, before prompt revision | Three pages extracted; mobile requirement missed; question repeated the client's request for an estimate | 59.41 s |
| Revised bakery run | Three pages plus mobile support, explicit online-ordering/payment exclusion, launch/newsletter questions | 86.81 s |
| Repeated revised bakery run | Same four tasks and exclusion; used for final quote workflow | 48.31 s |
| Photographer | Photo editing/JPEG delivery, RAW exclusion, image-dimension question; optional background removal was kept out of scope, but no follow-up question about it was suggested | 68.94 s |
| Contradiction plus embedded instruction | No invented invoice/price appeared, but unresolved payment conflict was incorrectly treated as a deliverable and payment exclusion; the blog exclusion was missed | 46.89 s |

The contradiction result is a **known semantic failure**, preserved in
`evidence/contradiction.json`. Verbatim evidence checks do not guarantee correct
interpretation or completeness. These checks do not establish prompt-injection
resistance for arbitrary input. Users must inspect the full notes, remove incorrect
items, and resolve questions with their client.

The app and Ollama had stopped between interrupted sessions. The app reported a
model-unavailable error during recovery; after both local processes were restored,
the real-model checks completed. The earlier outage evidence files were replaced
by their completed real-model runs, and the outage is recorded here.

## Browser workflow

Verified in the Codex in-app Chromium browser on Windows:

- Fictional sample filled the brief; a real model response produced the review UI.
- Hours entered manually: **4, 3, 2, 3**. Hourly rate entered manually: **INR 1,500**.
- The calculated total was **INR 18,000.00**.
- Clarification questions were manually edited in the UI before review.
- Download button saved a text file. Its UTF-8 content exactly matched the DOM's
  draft preview. A copy is `evidence/bakery-draft.txt`.
- Changing the hourly rate hid the old quote.
- Editing scope text cleared the review checkbox and hid the old quote.
- Removing the fourth scope item left three rows, retained the first row's entered
  four hours, cleared review, and kept the old quote hidden.
- At an explicit **375 × 812** phone viewport, the page's client width and scroll
  width were both **361 px** (the remaining width is the browser's scrollbar).
  There was no horizontal document overflow. Quote calculation also succeeded
  at this size. The viewport override was reset afterward.

The browser captures show real application state. The `bakery-browser.json`
evidence is from the earlier 86.81-second revised run; the final quote used the
48.31-second repeat of the same brief. No model output was mocked into the UI.

## Demo

`demo/brief-ledger-demo.mp4` is an approximately 45-second, 1280 × 800, 24 fps H.264
walkthrough assembled from six real browser screenshots with explanatory captions.
It is a screenshot walkthrough, not a continuous screen recording. Inference
waiting is omitted; measured timings above preserve the actual latency.

FFmpeg decoded the full exported MP4 without errors. The screenshots and captioned
frames were inspected for scope, review, total, and mobile layout accuracy.

Demo tooling uses the already-installed Pillow package plus `imageio-ffmpeg==0.6.0`
installed only into ignored `.tools/`. These are not application runtime dependencies.
To regenerate the video on Windows, install those demo-only tools and run
`python submission/make_demo.py`.

## Unverified boundaries

- No real customer, payment, willingness-to-pay study, or business outcome.
- No production hosting, public server deployment, other OS, or other model verified.
- No claim of complete extraction, factual accuracy, legal validity, or adversarial robustness.
- Nothing is automatically sent to a client. The exported document is a draft.
