# EDITORIAL.md — the contract for anyone who edits cirwel.org

Read this before changing a page. It applies to every writer: a Codex
session, a Claude session, or the operator. The site has been rewritten by
many sessions; the churn came from each one re-deriving what "effective"
means. This file is that definition, written once. Change the file when the
definition changes; do not work around it in a page.

## 1. The sentence

The home page is written for a first-time reader who reads about thirty
words and has no reason yet to trust it. Above the fold it says what the
product is and why it matters in plain words, and shows checkable facts rather
than adjectives. Every plain line must still be true of the deployed system:
no "automatically", no "all of it", nothing the server docs do not support.
The precise definition is one scroll away, not the first thing read.

The one-sentence definition of UNITARES is owned by the server README
(`cirwel/unitares`, `README.md`). Every surface copies it verbatim, and
`src/data/claims.json` pins it against the README so a rewrite that changes it
fails the daily check.

Tagline (the README's own heading):

> Accountability infrastructure for long-running AI agents.

Definition (the README's three definition sentences, in two short paragraphs
beginning "UNITARES is self-hosted"; the problem paragraph above them is
README-only):

> UNITARES is self-hosted accountability infrastructure for operators running
> multiple AI agents. Its single-operator federation kernel connects
> independent runtimes to one operator-controlled server over MCP or HTTP,
> where they share a durable record while keeping their own models, tools, and
> runtimes. Across Claude Code, Codex, Hermes Agent, and custom MCP or REST
> clients, agent work remains attributable, reviewable, and recoverable even
> when the process that started it is gone.

Headline (display only; the site's, not the README's):

> Many agents, one record.

Plain lead (the site's, not the README's; the home hero's two lines under the
headline):

> Your AI agents share one record of what they did, what they claimed, who
> challenged it, and how it turned out.
>
> Logs show each run. The record keeps the thread between them, so whoever
> picks up next can find where the last one left off.

Where each goes: the headline is the home hero and the share card; the plain
lead follows the headline on the home page; the tagline is the page title,
the JSON-LD description, the share card subline, and the `og:image:alt`; the
definition's three sentences sit together, in order, in the home page's "In
precise terms" block, where "federation" and "kernel" are both defined. In
that block the second sentence's opening "Its" becomes "The UNITARES"; no
other word changes. To change any of
them, change the README first, then this file, then the pages, then
`claims.json`, then re-render the card with `node scripts/render-og.mjs`.

Brand order: the product leads and CIRWEL Research endorses it. UNITARES is
the subject of the home title and the hero eyebrow; CIRWEL Research is the
masthead and the publisher. The navigation lists the product pages first
(Architecture, whose page describes itself as the UNITARES architecture, and
Build, for "Build on UNITARES"), then Research, Paper, Source, Contact. Keep
labels short enough that the phone header stays at two rows. The trade
name, CIRWEL Systems, stays in the colophon and the JSON-LD.

"Federation" is used in one plain sense on the product pages: independent
runtimes sharing one operator's server. That is why the definition says
"single-operator federation kernel", and the qualifier stays wherever the
product pages name the kernel. Accountability between operators who share no
root of trust is the other sense. When a product page mentions it, the page
says "cross-operator" or "multi-principal", as the server repository does. It
is a research question, answered in the papers the research page lists. Do
not let the two senses blur.

## 2. The spine

The only permitted "what it does" structure on the home and ecosystem pages
is the five questions from the server's `docs/PRODUCT_DEFINITION.md`:

1. Who said it?
2. What supports it?
3. Who challenged it?
4. What happened?
5. What can a successor recover?

Each gets one deployed mechanism and, if needed, one boundary. Do not
reintroduce the noun list ("identity, evidence, memory, runtime state, and
coordination"); it appeared nine times with a different membership each time.

## 3. Vocabulary

Allowed on the front door without definition: agent, operator, runtime,
record, evidence, review, outcome, handoff, restart, process, check-in.

Must be defined in the sentence that introduces them: lineage, provenance,
attestation, lease, harness, kernel, userland.

Kept off the product pages (home, ecosystem, build): resident (say
"long-running agent"), governed surface (say "a write the server can
refuse"), verdict (say "policy action"), proprioception, EISV.

"Agent" means software on the product pages. Where people are meant too, say
"people and agents". The research page uses "principals" for the human-or-
software case.

## 4. No hedge budget

The storefront states what is true, confidently, and lets the reader judge
(operator rule, 2026-09-19, reaffirmed 2026-10-21). No page prefaces a claim
with what has not been tested, who has not adopted it, or which single
deployment it came from, and no page implies adoption. Honest scoping lives in
the server repository: the evidence ledger (`docs/EVIDENCE_AND_LIMITS.md`) and
the scope and threat model (`docs/SCOPE_AND_THREAT_MODEL.md`). The build page
links to both; no page restates them, and the build page's §05 says where
UNITARES sits beside evals and guardrails rather than listing limits.

Three kinds of qualifier stay, because they are facts rather than apologies:

- a caveat that defines a number: its n, its slice, that it is
  observational, or the deployment it was measured on;
- a denominator;
- the single-operator disclosure, which the operator chose to promote: the
  "In use" receipts row on the home and architecture pages. It is stated in
  those rows and nowhere else.

No page shows live counts of the deployment's own traffic (events, sessions,
findings). On a single-operator deployment every one of them is
self-generated, so a count reads as adoption to anyone who does not stop to
ask what generated it, and the "In use" row already states the fact a count
was standing in for: the system has run since November 2025 as CIRWEL's own
record. Counts, with their denominators and dates, belong to the server's
production snapshot and evidence ledger.

Research results and their status are not restated anywhere on the site. They
move with the data, and a hand-kept copy drifts faster than any check can
follow. The research page lists the papers and the data, and links to the server's evidence ledger
(`cirwel/unitares`, `docs/EVIDENCE_AND_LIMITS.md`), which is versioned with the
code and is the one place current status lives. Do not copy a figure or a
status from the ledger or a paper onto a page; link to it.

Process rules (pre-registration, no re-runs, keeping withdrawn results, the
claims check) are how the repositories and the agents that edit them are kept
honest. They live in the repositories, not on the public pages: listed on a
page, they read as the researcher's confession rather than the system's
discipline. Do not attach a disclaimer
to a sentence that states a mechanism; "X, not Y" and "X rather than Y" at
most once per section. The honesty stays; the tic goes.

## 5. Voice

Product pages are impersonal. The research page is signed "I", on purpose.
Never "this site", "this page", or "our code"; never editorialize about other
products. A page does not talk about itself.

## 6. The register

The engraved register stays: cream and oxblood by day, bistre and verdigris by
night, Bodoni Moda display over EB Garamond text with JetBrains Mono for data,
hairlines and no cards. Tokens live in `tailwind.config.mjs` and
`src/styles/global.css`; `cirwel.github.io` mirrors them and checks the mirror.

Ornament must be load-bearing. Per page: one figure plate at most on the home
page (a real record from the deployment, claim to outcome, when one is
published in `src/data/example-record.json`; never an invented one), one section rule per seam, no fact rendered twice (the deployment start
date lives in the receipts; nowhere else). Labels are literal:
the theme control says AUTO / LIGHT / DARK, the 404 says "Not found", the
navigation names pages. The print metaphor lives in the drawing, not in the
controls.

The way into the product is a real call to action in the display face (`.cta`),
not a 13 px tracked label.

## 7. Corrections

A change to a figure, a status, or a claim gets an entry in
`src/data/corrections.json` and a `claims.json` update in the same pull
request. Copy edits do not. The list lives in the repository; no page
renders it.

## 8. Before you push

- `node scripts/render-og.mjs` if the hero or tagline changed.
- `python3 scripts/check-claims.py --self-test`, then the live check after
  deploy.
- Build locally and look at the home page at 390 px as well as 1440 px.
- One PR per topic; the PR body names which of the sections above it touches.
