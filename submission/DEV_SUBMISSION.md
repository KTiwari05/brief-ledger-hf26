*This is a submission for the [Hacktoberfest Open-Source AI Challenge Week 2: Side Hustle](https://dev.to/challenges/hacktoberfest-week2-2026-10-12).*

## What I Built

A client asks for a small website. Their message mixes pages, supplied assets,
"maybe later" features, and a launch date that means something different to
each person. Before pricing the project, a freelancer has to turn that message
into a clear conversation about the work.

I built **Brief Ledger**, a local workspace for that step. Paste the original
notes, draft a scope with Qwen3 4B, and read each task beside the exact words it
came from. Edit the tasks, remove incorrect items, and change the clarification
questions. Then enter your own hours and rate to download a draft estimate.

The customer I have in mind is an independent web designer or developer who
repeatedly prepares estimates from informal briefs. The business hypothesis is
a paid setup and support service for a local quoting workflow: keep client
notes on the freelancer's computer and reduce the repeated work of building a
scope document. The code is MIT licensed. There is no payment system or paying
customer in this prototype, and I have not validated willingness to pay.

## Demo

[Watch or download the video walkthrough (MP4)](https://raw.githubusercontent.com/KTiwari05/brief-ledger-hf26/main/submission/demo/brief-ledger-demo.mp4).

![Brief Ledger shows source-linked scope items beside the original client notes](https://raw.githubusercontent.com/KTiwari05/brief-ledger-hf26/main/submission/demo/03-scope.jpg)

The walkthrough uses a fictional bakery brief and a real local model reply.
It is assembled from browser screenshots, with generation waiting omitted.
The final browser run took **48.31 seconds** to generate the scope on this
computer. It found three pages plus the request for mobile support.

I entered 4, 3, 2, and 3 hours, then a rate of INR 1,500 per hour. The server
calculated INR 18,000.00. Those numbers are demonstration inputs, not a
recommended market price. The downloaded text matched the on-screen draft.

## Code

[Brief Ledger source on GitHub](https://github.com/KTiwari05/brief-ledger-hf26)

The repository includes setup instructions, tests, real-model evidence, browser
captures, and the demo. Run `ollama pull qwen3:4b`, keep Ollama running, then run
`python app.py` and open the printed local address. Application runtime needs
Python 3.11+ and Ollama, with no Python or JavaScript packages to install.

## How I Built It

The browser is plain HTML, CSS, and JavaScript. A small Python standard-library
server calls Ollama's local chat endpoint with a JSON schema. Qwen3 4B extracts
requested work, explicit exclusions, and questions the freelancer can ask.

```text
Client notes → local Qwen3 4B → JSON + source-quote validation
                                      ↓
                       Human reviews scope, hours, and rate
                                      ↓
                         Decimal calculation → text draft
```

Every task and exclusion must include a source quote found in the notes.
Truncated output and unreadable JSON are rejected. There is an important limit:
finding the quote does not establish that the model understood it or found
every requirement. The review screen makes that distinction visible.

Two DEV posts helped sharpen the boundary. [Edward Amirain's estimator
write-up](https://dev.to/vaynerov/building-an-ai-project-estimator-with-prices-the-model-cannot-invent-53o9)
keeps price calculations outside the model, while [Michael Maurice's extraction
checklist](https://dev.to/michael_maurice/schema-valid-correct-4-checks-before-you-trust-llm-extraction-4n6f)
explains why schema-valid data still needs evidence and ordinary business checks.
Brief Ledger was implemented independently; no source code was copied from them.

Here, the model returns no hours or rate. The freelancer enters both. The server
uses decimal arithmetic, rounds each line to two places, and sums the rounded
lines. It ignores totals supplied by the browser. Changing scope clears review;
changing pricing hides the old estimate until it is recalculated.

The first live bakery run exposed an omission: the model found the pages but
missed mobile support. It also repeated the client's request for an estimate
as a clarification question. I tightened the instructions and reran the same
brief. The revised runs included mobile support and launch/newsletter questions.

A more difficult test still failed semantically. Faced with conflicting
instructions about online payments, the model made resolving that conflict a
deliverable and also listed payments as excluded. It missed an explicit blog
exclusion. The evidence quotes were present in the notes, so substring checks
could not catch those mistakes. That output is preserved in the repository.
This is why the app lets a person remove items and edit questions before export.

Twelve automated tests passed. I also checked real replies for a photographer's
brief, the edited review flow, quote invalidation, the downloaded text, and a
375-pixel phone layout without horizontal overflow. The verification notes
record the exact checks and limits. These examples are not a benchmark of
general extraction accuracy or prompt-injection resistance.

## Why Does Open Innovation Matter?

The open-weight model does the central transformation from informal notes to
structured scope. Ollama runs it on the same computer. Once the software and
weights are downloaded, the inference path uses local endpoints and requires
no paid model account. This app has no database, analytics, or cloud inference.
It keeps the working draft in memory; exporting saves a text file.

For this workflow, control over where client notes are processed is useful.
The prompts and validation code can be inspected and changed, and the model
configuration is replaceable, although only Qwen3 4B has been tested here.
Qwen's weights are downloaded separately and retain their Apache 2.0 license.

Local inference also has a cost: waiting on the available hardware and reviewing
the output carefully. Open weights do not make an ambiguous request unambiguous.
The goal is a traceable starting point for the freelancer's judgment.

## My Agent Session

Codex implemented and tested this project and prepared this article under my
instruction to complete the challenge. This submission was published
autonomously with AI involvement disclosed. No public session transcript is
linked. The repository contains the verification evidence instead.

## Prize Categories

This entry is for the overall challenge. It uses Qwen and Ollama and does not
claim a partner prize category.
