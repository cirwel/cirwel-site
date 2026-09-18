# EDITORIAL.md — the contract for anyone who edits cirwel.org

Read this before changing a page. It applies to every writer: a Codex
session, a Claude session, or the operator. The site has been rewritten by
many sessions; the churn came from each one re-deriving what "effective"
means. This file is that definition, written once. Change the file when the
definition changes; do not work around it in a page.

## 1. The sentence

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
> multiple AI agents. Its federation kernel connects independent runtimes to
> one operator-controlled server over MCP or HTTP, where they share a durable
> record while keeping their own models, tools, and runtimes. Agent work
> should remain attributable, reviewable, and recoverable even when the
> process that started it is gone.

Headline (display only; the site's, not the README's):

> Many agents, one record.

Where each goes: the headline is the home hero and the share card; the
tagline is the page title, the JSON-LD description, the share card subline,
and the `og:image:alt`; the definition's first sentence is the hero subhead,
its third follows it, and its second (the one that names the federation
kernel) sits under the hero figure, where "federation" and "kernel" are both
defined. Placed apart from the sentence before it, its opening "Its" becomes
"The UNITARES"; no other word changes. To change any of
them, change the README first, then this file, then the pages, then
`claims.json`, then re-render the card with `node scripts/render-og.mjs`.

Brand order: the product leads and CIRWEL Research endorses it. UNITARES is
the subject of the home title and the hero eyebrow; CIRWEL Research is the
masthead and the publisher. The navigation lists the product pages first
(Architecture, whose page describes itself as the UNITARES architecture, and
Build, for "Build on UNITARES"), then Research, Paper, Source, Contact. Keep
labels short enough that the phone header stays at two rows. The legal
entity, CIRWEL Systems, stays in the colophon and the JSON-LD.

"Federation" is used in one plain sense on the product pages: independent
runtimes sharing one operator's server. Accountability between operators who
share no root of trust is a research question and lives on the research page
under that name. Do not let the two senses blur.

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
refuse"), verdict (say "policy action"), proprioception, EISV. The research
page may use its own terms because it names what it measures.

"Agent" means software on the product pages. Where people are meant too, say
"people and agents". The research page uses "principals" for the human-or-
software case.

## 4. The hedge budget

Every limit is stated once, on the page that owns it: the build page's §05
and the research page. Product pages state facts. Do not attach a disclaimer
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
page, one section rule per seam, no fact rendered twice (the deployment start
date lives in the receipts and on the seal; nowhere else). Labels are literal:
the theme control says AUTO / LIGHT / DARK, the 404 says "Not found", the
navigation names pages. The print metaphor lives in the drawing, not in the
controls.

The way into the product is a real call to action in the display face (`.cta`),
not a 13 px tracked label.

## 7. Corrections

A change to a figure, a status, or a claim gets an entry in
`src/data/corrections.json` and a `claims.json` update in the same pull
request. Copy edits do not. The corrections list renders on the research page.

## 8. Before you push

- `node scripts/render-og.mjs` if the hero or tagline changed.
- `python3 scripts/check-claims.py --self-test`, then the live check after
  deploy.
- Build locally and look at the home page at 390 px as well as 1440 px.
- One PR per topic; the PR body names which of the sections above it touches.
