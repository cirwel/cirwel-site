# cirwelsystems.com — homepage redesign

**Status:** Design approved, awaiting implementation plan
**Date:** 2026-04-26
**Owner:** Kenny Wang
**Repo:** `CIRWEL/cirwel-site` (replaces in place — keeps Cloudflare Pages binding)

## Problem

The current cirwelsystems.com is a React/Vite Replit-exported app with a cyberpunk/glitch aesthetic anchored on a "thermodynamic governance" narrative. Both the aesthetic and the framing are mismatched to the founder's current audience (deep-tech-explicit funders, ML researchers, secondarily VCs). The local source has also drifted into a partially-broken state — builds, but renders inconsistently — leaving the live site stuck on an old deployment.

The minimum viable fix is not a copy refresh; the visual system itself is fighting the positioning. Replace the stack and the design.

## Decisions

| Question | Decision |
|---|---|
| Single-site or two-site? | **Single-site** for now. cirwel.org will redirect to cirwelsystems.com. Two-audience split (3b — `.org` for research, `.com` for commercial) deferred until single-site is clean. |
| Site structure | **Hybrid C** — single-page Home with anchor sections, plus dedicated subpages later for `/paper`, `/patents`, eventual `/blog`. |
| Tech stack | **Astro + Tailwind**. Replaces React/Vite/framer-motion in place. |
| Aesthetic direction | Editorial-publication × engineering-instrument-panel. Distinctive without copying Anthropic, Nous, Distill, or arXiv. Driven by a single characterful serif (Fraunces) for almost all reading copy plus restrained mono (JetBrains Mono) for data. |
| Narrative spine | **Telemetry-first** — runtime self-state telemetry as the missing layer between pre-deployment evaluation and post-incident forensics. Heterogeneity (class-conditional calibration) is the credibility leg; provenance (signed audit trail) is the defensibility leg. |
| Contact | `founder@cirwel.org`. Email itself does not exist yet — see Prerequisites. |
| Location in footer | **Omitted.** Founder may relocate; future-proof by not pinning. |
| Embodied edge service mention (Lumen surface area) | **Single passing reference** in §03 ("In production"). Not centered, not named. |
| Hero italic treatment | Keep — Fraunces italic on `fleets.` is the one expressive moment. |

## Audience (in priority order, broad not tribal)

1. Deep-tech-explicit funders — NSF, CO ONE, Anthropic Fellow, Eric Schmidt's foundation, federal grants
2. ML researchers from labs like Anthropic and Nous Research
3. VCs evaluating market opportunity
4. Casual visitors arriving via paper or social

The site must read as legitimate to all four without picking a tribal aesthetic.

## Visual system

| Token | Value | Role |
|---|---|---|
| `cream` | `#F5F1E8` | Background |
| `ink` | `#1A1612` | Primary text |
| `oxblood` | `#7A1F1F` | Accent — labels, links, section markers |
| `ochre` | `#B8862F` | Secondary accent — sparingly used |
| `stone` | `#5C544A` | Muted text, metadata |
| `sepia` | `#C9C0AE` | Hairline rules |

- **Display + body type:** Fraunces (variable: `opsz`, `wght`, `SOFT`, `WONK` axes). One typeface for nearly everything.
- **Mono type:** JetBrains Mono. Restricted to DOIs, ORCIDs, repo paths, verdict tokens, footer records.
- **Layout:** 12-column grid. Section markers in left rail (oxblood small caps, mono); content in right 9 columns. Max-width container, no full-bleed visuals.
- **Motion:** One staggered page-load reveal (5 elements, 0–660ms); underline-grow on hover. Nothing else.
- **Texture:** Faint SVG noise overlay (~4% opacity, multiply blend) for paper feel.

No gradients. No glow. No glass-morphism. No translucency. No purple/pink. No buyer-persona feature cards.

## Section structure (Home)

| # | Section | Purpose |
|---|---|---|
| Nav | Wordmark + minimal links (Thesis, Paper, Patents, Plugin, Contact) | Identity + routing |
| Hero | Display headline + editorial lede paragraph | Establish thesis in first 5s |
| Receipts | DOI · ORCID · patents · tests · production date · code link | Proof above scroll |
| §01 The thesis | 3-paragraph essay block expanding the missing-layer argument | Develop position |
| §02 Three pillars | Class-conditional calibration / drift detection / auditable provenance | Concrete differentiation |
| §03 In production | Dogfooding paragraph (governing CIRWEL's own dev fleet) | Solo-founder credibility |
| §04 Engage | Three doors: Read paper / Run plugin / Write founder | Three audiences, three paths |
| Footer | Records (ORCID, DOI), copyright, identity line | Institutional close |

## Receipts surfaced above scroll

- Paper: *UNITARES: Information-Theoretic Governance of Heterogeneous Agent Fleets*, Wang 2026
- DOI: 10.5281/zenodo.19647159 (concept — auto-resolves to latest)
- Author: Kenny Wang, Independent Researcher, ORCID 0009-0006-7544-2374
- Patents: 9+ provisional, filed
- Tests: 6,200+ at 77% coverage
- Production: continuous since November 2025
- Code: github.com/CIRWEL/unitares-governance-plugin

## Constraints — copy and content

- Do **not** expose EISV variable names (E, I, S, V) or ODE dynamics anywhere on the homepage. Reference "four-dimensional self-state vector" without enumerating axes.
- Do **not** name or center Lumen / anima (the embodied Pi side). Permitted: a single passing reference to "an embodied edge service" inside a heterogeneity-list in §03.
- Verdict tokens (`proceed`, `guide`, `pause`, `reject`) are public-facing API surface and may appear in `<code>` styling in the thesis section.
- UNITARES is the internal product name — referenced by name in the thesis and pillars sections; not the headliner.
- CIRWEL Systems is the public brand; first-person institutional voice ("CIRWEL Systems builds…").

## Aesthetic justifications vs the "don'ts"

| Constraint | How honored |
|---|---|
| No glass / gradients / glow | Solid cream background, hairline rules, single accent. Zero translucency. |
| No buyer-persona feature cards | Pillars are technical capabilities, not buyer benefits. |
| Not Anthropic-clone | Cream + characterful serif + oxblood vs Anthropic's off-white + geometric sans + orange. |
| Not Nous-clone | Light + serif-everywhere + zero generative widgets vs Nous's dark + mono-everywhere + SEED/OUTPUT motifs. |
| Not Distill-clone | No interactive figures. |
| Not arXiv-clone | Designed publication system, not academic PDF. |
| Not "50-person enterprise" | No team grid, no logo wall, no demo CTA. First-person institutional voice. |
| Substance forward | DOI, ORCID, patent count, test count, production date all visible above one scroll. |

The differentiating move: committing to Fraunces — a characterful variable serif — for both display and body. Almost no AI/tech site does this. Reads as "publication" not "pitch deck"; the WONK + SOFT axes give just enough quirk at display sizes to feel handcrafted rather than templated. This is the one thing a visitor will remember.

## Prerequisites (must resolve before launch — not blocking spec approval)

1. **Email at `founder@cirwel.org`** — domain has no DNS records currently and no email routing. Recommended path: Cloudflare Email Routing (free, ~5 min setup, MX records auto-managed, forwards to existing inbox like `hikewa@gmail.com`). Without this, the contact link is broken.
2. **`cirwel.org` DNS** — currently dark. Needs a record to enable email forwarding (above) and to support the planned `cirwel.org` → `cirwelsystems.com` 301 redirect (Cloudflare Redirect Rule or Page Rule).
3. **Cloudflare Pages binding** — current production deploy already targets the `cirwel-site` Cloudflare Pages project. After the Astro replacement, `wrangler pages deploy dist` (or whatever Astro outputs) should drop into the same project; no DNS changes required.

## Out of scope

- `/paper`, `/patents`, `/blog` subpages. Routes are referenced in nav but will 404 until built. Separate spec/plan.
- The two-audience split (`.org` for research / `.com` for commercial). Deferred until single-site is clean.
- Visual identity / logo refresh. The current wordmark "CIRWEL Systems" set in Fraunces is sufficient.
- Migration of any content from the existing React app (the existing modal-heavy components, the Patents portfolio page, the IP portfolio, the Industries page, etc.). The redesign is a clean rewrite, not a port.

## Acceptance criteria

- Lighthouse performance ≥ 95 on desktop, ≥ 90 mobile
- Web fonts loaded with `font-display: swap`; first contentful paint ≤ 1.5s on cable
- Page passes basic a11y (axe-core no critical violations)
- All copy on the page matches the receipts above (no hallucinated metrics)
- Live at cirwelsystems.com via the existing Cloudflare Pages project
- `cirwel.org` redirects to cirwelsystems.com (Cloudflare-side rule)
- `founder@cirwel.org` contact link resolves to a real inbox (Cloudflare Email Routing or equivalent)
- No EISV variable names, no ODE references, no Lumen-as-product framing on the homepage

## Implementation phases (high-level — to be detailed by writing-plans)

1. **Repo prep** — branch off `master`, archive React/Vite source under `legacy/` (don't delete), strip top-level scaffolding
2. **Astro scaffold** — `npm create astro@latest`, integrate Tailwind, drop in the design system files (`tailwind.config.mjs`, `src/styles/global.css`, `src/layouts/BaseLayout.astro`)
3. **Homepage build** — `src/pages/index.astro` with all sections from this spec, real copy
4. **Local verification** — `npm run dev`, visual review at multiple viewports, Lighthouse local
5. **Prerequisites** — Cloudflare Email Routing for `founder@cirwel.org`; cirwel.org DNS + redirect rule
6. **Deploy** — Cloudflare Pages, same `cirwel-site` project; verify cirwelsystems.com renders new homepage
7. **Subpages** — separate spec/plan; not part of this milestone
