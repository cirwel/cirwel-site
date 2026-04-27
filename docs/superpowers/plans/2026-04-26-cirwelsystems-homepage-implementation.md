# cirwelsystems.com Homepage Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the existing React/Vite cirwelsystems.com with an Astro+Tailwind static site implementing the editorial-publication design from the spec, deployed in-place via the existing Cloudflare Pages project.

**Architecture:** Astro 4.x static site. Single layout, single page (Home). Tailwind for styling. Fraunces + JetBrains Mono via Google Fonts. Build output to `dist/` for Cloudflare Pages compatibility. Existing React/Vite source archived to `legacy/react-vite/` rather than deleted, to preserve history.

**Tech Stack:** Astro 4.x, Tailwind CSS 3.x, TypeScript (strict), Google Fonts (Fraunces variable + JetBrains Mono), Cloudflare Pages, Cloudflare Email Routing, Cloudflare Redirect Rules.

**Spec:** `docs/superpowers/specs/2026-04-26-cirwelsystems-homepage-design.md` (commit `8d70dd3`)

---

## Working environment

All code-change tasks are run inside a git worktree at `/Users/cirwel/projects/cirwel-site-redesign` on branch `redesign-astro`. The original `/Users/cirwel/projects/cirwel-site/` worktree on `master` is left undisturbed (it has uncommitted React/Vite WIP that must not be touched).

Bash cwd does NOT persist across calls in worktrees. Every git command must include `git -C /Users/cirwel/projects/cirwel-site-redesign` or `cd` inline. Every npm command must `cd` inline.

## File structure

After this plan, the worktree will contain:

```
cirwel-site-redesign/
├── .gitignore                                 (new — Astro-standard)
├── astro.config.mjs                           (new)
├── tailwind.config.mjs                        (new)
├── tsconfig.json                              (new — Astro-standard strict)
├── package.json                               (replaced)
├── package-lock.json                          (regenerated)
├── public/
│   ├── favicon.png                            (preserved from existing)
│   └── robots.txt                             (preserved from existing)
├── src/
│   ├── layouts/
│   │   └── BaseLayout.astro                   (new)
│   ├── pages/
│   │   └── index.astro                        (new — homepage)
│   └── styles/
│       └── global.css                         (new)
├── legacy/
│   └── react-vite/                            (archive of pre-redesign source)
│       ├── index.html
│       ├── vite.config.js
│       ├── package.json
│       ├── package-lock.json
│       ├── src/
│       └── public/
└── docs/superpowers/
    ├── specs/2026-04-26-cirwelsystems-homepage-design.md  (existing)
    └── plans/2026-04-26-cirwelsystems-homepage-implementation.md  (this file)
```

Cloudflare-side changes (Email Routing, DNS for cirwel.org, redirect rule) are made via the Cloudflare dashboard and verified from the command line. They do not produce git commits.

---

## Task 1: Create the worktree

**Files:** none (worktree creation only)

- [ ] **Step 1: Verify the source repo and current state**

```bash
git -C /Users/cirwel/projects/cirwel-site rev-parse --abbrev-ref HEAD
git -C /Users/cirwel/projects/cirwel-site log -1 --oneline
```

Expected output:
- branch: `master`
- last commit: `8d70dd3 spec: cirwelsystems.com homepage redesign (Astro, telemetry-first, Fraunces)`

- [ ] **Step 2: Confirm no existing `redesign-astro` branch or worktree**

```bash
git -C /Users/cirwel/projects/cirwel-site worktree list
git -C /Users/cirwel/projects/cirwel-site branch --list redesign-astro
```

Expected: only the `master` worktree listed; no `redesign-astro` branch. If either exists, stop and ask the user before proceeding.

- [ ] **Step 3: Create the worktree on a new branch**

```bash
git -C /Users/cirwel/projects/cirwel-site worktree add -b redesign-astro /Users/cirwel/projects/cirwel-site-redesign master
```

- [ ] **Step 4: Verify the worktree is clean**

```bash
git -C /Users/cirwel/projects/cirwel-site-redesign status --short
```

Expected: empty output (no modified, no untracked). The uncommitted WIP from the master worktree must NOT have followed.

- [ ] **Step 5: Verify the worktree contains the spec**

```bash
ls /Users/cirwel/projects/cirwel-site-redesign/docs/superpowers/specs/
```

Expected: `2026-04-26-cirwelsystems-homepage-design.md` is present.

No commit yet — Task 1 is environment setup only.

---

## Task 2: Archive existing React/Vite scaffolding

**Files:**
- Move: `index.html` → `legacy/react-vite/index.html`
- Move: any other tracked top-level Vite files (the master HEAD only had `index.html` tracked at the top level; package.json, src/, etc. were untracked WIP).

- [ ] **Step 1: List currently-tracked files in the worktree**

```bash
git -C /Users/cirwel/projects/cirwel-site-redesign ls-files | head -30
```

Note the output. Expected non-doc files at top level: `index.html`, possibly assets under `assets/`.

- [ ] **Step 2: Create the legacy directory**

```bash
mkdir -p /Users/cirwel/projects/cirwel-site-redesign/legacy/react-vite
```

- [ ] **Step 3: Move every tracked top-level non-doc file into `legacy/react-vite/`**

For each tracked file in the previous output that is NOT under `docs/`, run a git mv. Concretely, at minimum:

```bash
cd /Users/cirwel/projects/cirwel-site-redesign && git mv index.html legacy/react-vite/index.html
```

If `assets/` is tracked, move the whole tree:

```bash
cd /Users/cirwel/projects/cirwel-site-redesign && git mv assets legacy/react-vite/assets
```

Adjust the list to match the actual `git ls-files` output from Step 1.

- [ ] **Step 4: Verify the move**

```bash
git -C /Users/cirwel/projects/cirwel-site-redesign status --short
git -C /Users/cirwel/projects/cirwel-site-redesign ls-files | grep -E '^(index\.html|assets/)' | head -5
```

Expected: status shows the renames staged; the grep returns no top-level matches (everything moved).

- [ ] **Step 5: Commit**

```bash
git -C /Users/cirwel/projects/cirwel-site-redesign commit -m "chore: archive React/Vite source under legacy/react-vite"
```

Verify commit succeeded:

```bash
git -C /Users/cirwel/projects/cirwel-site-redesign log -1 --oneline
```

---

## Task 3: Create `package.json` for Astro

**Files:**
- Create: `package.json`

- [ ] **Step 1: Write the file**

Path: `/Users/cirwel/projects/cirwel-site-redesign/package.json`

```json
{
  "name": "cirwel-site",
  "version": "2.0.0",
  "type": "module",
  "private": true,
  "description": "cirwelsystems.com — runtime governance for heterogeneous AI-agent fleets",
  "repository": {
    "type": "git",
    "url": "git+https://github.com/CIRWEL/cirwel-site.git"
  },
  "scripts": {
    "dev": "astro dev",
    "build": "astro build",
    "preview": "astro preview",
    "check": "astro check"
  },
  "dependencies": {
    "@astrojs/check": "^0.9.4",
    "@astrojs/tailwind": "^5.1.5",
    "astro": "^4.16.18",
    "tailwindcss": "^3.4.17",
    "typescript": "^5.7.3"
  }
}
```

- [ ] **Step 2: Verify the file is valid JSON**

```bash
python3 -c "import json; json.load(open('/Users/cirwel/projects/cirwel-site-redesign/package.json'))" && echo OK
```

Expected: `OK`. If anything else, fix the JSON before continuing.

- [ ] **Step 3: Commit (will be combined with the other config files in Task 7's commit)**

No commit yet.

---

## Task 4: Create `astro.config.mjs`

**Files:**
- Create: `astro.config.mjs`

- [ ] **Step 1: Write the file**

Path: `/Users/cirwel/projects/cirwel-site-redesign/astro.config.mjs`

```js
import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';

export default defineConfig({
  site: 'https://cirwelsystems.com',
  integrations: [
    tailwind({
      applyBaseStyles: false,
    }),
  ],
  build: {
    inlineStylesheets: 'auto',
  },
});
```

`applyBaseStyles: false` is intentional — we manage `@tailwind base` manually inside `src/styles/global.css` so that custom font/grain/typography rules can sit alongside the Tailwind layers.

No commit yet.

---

## Task 5: Create `tailwind.config.mjs`

**Files:**
- Create: `tailwind.config.mjs`

- [ ] **Step 1: Write the file**

Path: `/Users/cirwel/projects/cirwel-site-redesign/tailwind.config.mjs`

```js
/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
  theme: {
    extend: {
      colors: {
        cream:   '#F5F1E8',
        ink:     '#1A1612',
        oxblood: '#7A1F1F',
        ochre:   '#B8862F',
        stone:   '#5C544A',
        sepia:   '#C9C0AE',
      },
      fontFamily: {
        serif: ['Fraunces', 'ui-serif', 'Georgia', 'serif'],
        mono:  ['"JetBrains Mono"', 'ui-monospace', 'monospace'],
      },
      maxWidth: {
        prose: '40rem',
      },
    },
  },
  plugins: [],
};
```

No commit yet.

---

## Task 6: Create `tsconfig.json`

**Files:**
- Create: `tsconfig.json`

- [ ] **Step 1: Write the file**

Path: `/Users/cirwel/projects/cirwel-site-redesign/tsconfig.json`

```json
{
  "extends": "astro/tsconfigs/strict",
  "include": [".astro/types.d.ts", "**/*"],
  "exclude": ["dist", "legacy"]
}
```

No commit yet.

---

## Task 7: Create `.gitignore` and commit Astro scaffolding

**Files:**
- Create: `.gitignore`
- Stage: `package.json`, `astro.config.mjs`, `tailwind.config.mjs`, `tsconfig.json`, `.gitignore`

- [ ] **Step 1: Write `.gitignore`**

Path: `/Users/cirwel/projects/cirwel-site-redesign/.gitignore`

```
# build output
dist/
.astro/

# dependencies
node_modules/

# logs
npm-debug.log*
yarn-debug.log*
yarn-error.log*
pnpm-debug.log*

# environment
.env
.env.production
.env.local
.env.*.local

# macOS
.DS_Store

# editor
.vscode/
.idea/
*.swp
```

- [ ] **Step 2: Stage and commit the scaffolding**

```bash
cd /Users/cirwel/projects/cirwel-site-redesign && git add .gitignore package.json astro.config.mjs tailwind.config.mjs tsconfig.json && git commit -m "chore: scaffold Astro+Tailwind project (config + .gitignore)"
```

- [ ] **Step 3: Verify the commit**

```bash
git -C /Users/cirwel/projects/cirwel-site-redesign log -1 --stat
```

Expected: 5 files added, no `package-lock.json` yet (that's Task 8), no `node_modules` (gitignored).

---

## Task 8: Install dependencies

**Files:** none (creates `node_modules/` and `package-lock.json`)

- [ ] **Step 1: Run `npm install`**

```bash
cd /Users/cirwel/projects/cirwel-site-redesign && npm install
```

Expected: completes in 30-90 seconds. Possible warnings about peer deps are fine; ERRORS are not. If it errors, stop and ask.

- [ ] **Step 2: Verify Astro is callable**

```bash
cd /Users/cirwel/projects/cirwel-site-redesign && npx astro --version
```

Expected: prints `4.x.x`.

- [ ] **Step 3: Stage and commit `package-lock.json`**

```bash
cd /Users/cirwel/projects/cirwel-site-redesign && git add package-lock.json && git commit -m "chore: pin dependencies via package-lock"
```

---

## Task 9: Verify Astro dev server boots cleanly (smoke test)

**Files:** none (read-only verification)

This is a smoke test, not a commit. We need at least ONE Astro page to exist for `dev` to actually serve something — so create a minimal stub now and replace it in later tasks.

- [ ] **Step 1: Create a placeholder `src/pages/index.astro`**

Path: `/Users/cirwel/projects/cirwel-site-redesign/src/pages/index.astro`

```astro
---
// Placeholder — replaced in Task 12
---
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <title>scaffold check</title>
  </head>
  <body>scaffold ok</body>
</html>
```

(Create the `src/pages/` directory first: `mkdir -p /Users/cirwel/projects/cirwel-site-redesign/src/pages`)

- [ ] **Step 2: Run `npm run dev` in the background**

```bash
cd /Users/cirwel/projects/cirwel-site-redesign && npm run dev
```

Run this with `run_in_background: true`. Wait for the "Local: http://localhost:4321/" line in the output (use Monitor or BashOutput to check).

- [ ] **Step 3: Curl the running dev server**

```bash
curl -sf http://localhost:4321/ | head -5
```

Expected: returns HTML containing `scaffold ok`. If 404 or connection refused, the dev server failed to boot — read the background output to diagnose.

- [ ] **Step 4: Stop the dev server**

Use KillShell on the background bash id.

- [ ] **Step 5: Do not commit the placeholder index.astro**

It will be overwritten in Task 12. Leave it untracked for now (or git status will show it as untracked — that is fine).

---

## Task 10: Create `src/styles/global.css`

**Files:**
- Create: `src/styles/global.css`

- [ ] **Step 1: Create the styles directory**

```bash
mkdir -p /Users/cirwel/projects/cirwel-site-redesign/src/styles
```

- [ ] **Step 2: Write the file**

Path: `/Users/cirwel/projects/cirwel-site-redesign/src/styles/global.css`

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  --grain-opacity: 0.04;
}

html {
  font-feature-settings: 'kern', 'liga', 'onum', 'pnum';
  font-size: 17px;
  text-rendering: geometricPrecision;
  -webkit-font-smoothing: antialiased;
}

/* Paper grain overlay */
body::before {
  content: '';
  position: fixed;
  inset: 0;
  pointer-events: none;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='3' stitchTiles='stitch'/%3E%3CfeColorMatrix values='0 0 0 0 0.10 0 0 0 0 0.08 0 0 0 0 0.04 0 0 0 0.5 0'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
  opacity: var(--grain-opacity);
  z-index: 1000;
  mix-blend-mode: multiply;
}

.display {
  font-variation-settings: 'opsz' 144, 'SOFT' 100, 'WONK' 1;
  letter-spacing: -0.035em;
  line-height: 0.96;
}

.label {
  font-family: 'JetBrains Mono', ui-monospace, monospace;
  font-size: 0.72rem;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  font-weight: 500;
}

.hairline {
  height: 1px;
  background: theme('colors.sepia');
  border: 0;
}

a {
  color: inherit;
  text-decoration-line: underline;
  text-decoration-color: rgba(122, 31, 31, 0.3);
  text-decoration-thickness: 1px;
  text-underline-offset: 0.22em;
  transition: text-decoration-color 0.2s ease;
}
a:hover {
  text-decoration-color: rgba(122, 31, 31, 1);
}

@media (prefers-reduced-motion: no-preference) {
  .reveal {
    opacity: 0;
    transform: translateY(10px);
    animation: fade-up 0.9s cubic-bezier(0.2, 0.7, 0.2, 1) forwards;
  }
  .reveal-1 { animation-delay: 0.05s; }
  .reveal-2 { animation-delay: 0.18s; }
  .reveal-3 { animation-delay: 0.34s; }
  .reveal-4 { animation-delay: 0.52s; }
  .reveal-5 { animation-delay: 0.70s; }
}
@keyframes fade-up {
  to { opacity: 1; transform: translateY(0); }
}
```

No commit yet — committed alongside layout in Task 11's final step.

---

## Task 11: Create `src/layouts/BaseLayout.astro`

**Files:**
- Create: `src/layouts/BaseLayout.astro`

- [ ] **Step 1: Create the layouts directory**

```bash
mkdir -p /Users/cirwel/projects/cirwel-site-redesign/src/layouts
```

- [ ] **Step 2: Write the file**

Path: `/Users/cirwel/projects/cirwel-site-redesign/src/layouts/BaseLayout.astro`

```astro
---
import '../styles/global.css';
interface Props { title: string; description: string; }
const { title, description } = Astro.props;
const canonical = new URL(Astro.url.pathname, Astro.site ?? 'https://cirwelsystems.com');
---
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="description" content={description} />
    <link rel="canonical" href={canonical} />
    <meta property="og:title" content={title} />
    <meta property="og:description" content={description} />
    <meta property="og:type" content="website" />
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link
      href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght,SOFT,WONK@0,9..144,300..900,0..100,0..1;1,9..144,300..900,0..100,0..1&family=JetBrains+Mono:wght@400;500&display=swap"
      rel="stylesheet"
    />
    <title>{title}</title>
  </head>
  <body class="font-serif text-ink bg-cream">
    <slot />
  </body>
</html>
```

- [ ] **Step 3: Stage and commit the design system**

```bash
cd /Users/cirwel/projects/cirwel-site-redesign && git add src/styles/global.css src/layouts/BaseLayout.astro && git commit -m "feat(design): add base layout, global styles, paper-grain overlay"
```

---

## Task 12: Create the homepage `src/pages/index.astro`

**Files:**
- Replace: `src/pages/index.astro` (currently the Task 9 placeholder)

- [ ] **Step 1: Overwrite the file with the production homepage**

Path: `/Users/cirwel/projects/cirwel-site-redesign/src/pages/index.astro`

```astro
---
import BaseLayout from '../layouts/BaseLayout.astro';
---
<BaseLayout
  title="CIRWEL Systems — Runtime governance for heterogeneous AI-agent fleets"
  description="Continuous self-state telemetry, class-conditional calibration, and signed provenance for AI agents you didn't build yourself. Reference implementation of UNITARES (Wang 2026, DOI 10.5281/zenodo.19647159)."
>
  <header class="px-6 lg:px-12 pt-8 pb-4 max-w-screen-xl mx-auto flex items-center justify-between">
    <a href="/" class="no-underline">
      <span class="display text-xl font-medium tracking-tight">CIRWEL Systems</span>
    </a>
    <nav class="hidden md:flex items-center gap-7 label text-stone">
      <a href="#thesis"  class="no-underline hover:text-oxblood transition-colors">Thesis</a>
      <a href="/paper"   class="no-underline hover:text-oxblood transition-colors">Paper</a>
      <a href="/patents" class="no-underline hover:text-oxblood transition-colors">Patents</a>
      <a href="https://github.com/CIRWEL/unitares-governance-plugin" class="no-underline hover:text-oxblood transition-colors">Plugin</a>
      <a href="#contact" class="no-underline hover:text-oxblood transition-colors">Contact</a>
    </nav>
  </header>

  <main class="px-6 lg:px-12 max-w-screen-xl mx-auto">

    <!-- HERO -->
    <section class="pt-16 pb-20 lg:pt-28 lg:pb-28 grid grid-cols-12 gap-6">
      <div class="col-span-12 lg:col-span-9">
        <p class="label text-oxblood mb-8 reveal reveal-1">— A research preface, with running code</p>
        <h1 class="display text-5xl md:text-7xl lg:text-8xl mb-10 reveal reveal-2">
          Runtime governance<br/>
          for heterogeneous<br/>
          AI-agent <span class="italic">fleets.</span>
        </h1>
        <p class="text-lg md:text-xl leading-relaxed text-stone max-w-prose reveal reveal-3">
          Most AI safety reasons about agents in two windows: pre-deployment evaluation
          and post-incident forensics. Between them — <em>while agents are actually
          running</em> — there is a measurement gap. Continuous, class-calibrated
          self-state telemetry, with signed provenance behind every intervention,
          fills it.
        </p>
      </div>
    </section>

    <hr class="hairline mb-2"/>

    <!-- RECEIPTS -->
    <section class="py-10 grid grid-cols-12 gap-6 reveal reveal-4">
      <div class="col-span-12 lg:col-span-3 mb-4 lg:mb-0">
        <p class="label text-oxblood">— The receipts</p>
      </div>
      <dl class="col-span-12 lg:col-span-9 grid grid-cols-12 gap-y-5 gap-x-6">

        <dt class="col-span-4 md:col-span-3 label text-stone pt-1">Paper</dt>
        <dd class="col-span-8 md:col-span-9">
          <a href="https://github.com/CIRWEL/unitares-paper-v6" class="font-medium">
            UNITARES: Information-Theoretic Governance of Heterogeneous Agent Fleets
          </a><span class="text-stone"> · Wang, 2026</span>
        </dd>

        <dt class="col-span-4 md:col-span-3 label text-stone pt-1">DOI</dt>
        <dd class="col-span-8 md:col-span-9 font-mono text-sm">
          <a href="https://doi.org/10.5281/zenodo.19647159">10.5281/zenodo.19647159</a>
          <span class="text-stone">  (concept · resolves to latest)</span>
        </dd>

        <dt class="col-span-4 md:col-span-3 label text-stone pt-1">Author</dt>
        <dd class="col-span-8 md:col-span-9">
          Kenny Wang <span class="text-stone">· Independent Researcher · ORCID</span>
          <a href="https://orcid.org/0009-0006-7544-2374" class="font-mono text-sm">0009-0006-7544-2374</a>
        </dd>

        <dt class="col-span-4 md:col-span-3 label text-stone pt-1">Patents</dt>
        <dd class="col-span-8 md:col-span-9">
          9<span class="text-stone">+</span> provisional, filed
        </dd>

        <dt class="col-span-4 md:col-span-3 label text-stone pt-1">Tests</dt>
        <dd class="col-span-8 md:col-span-9">
          6,200<span class="text-stone">+ at</span> 77<span class="text-stone">% coverage</span>
        </dd>

        <dt class="col-span-4 md:col-span-3 label text-stone pt-1">Production</dt>
        <dd class="col-span-8 md:col-span-9">
          Continuous since <span class="font-medium">November 2025</span>
        </dd>

        <dt class="col-span-4 md:col-span-3 label text-stone pt-1">Code</dt>
        <dd class="col-span-8 md:col-span-9 font-mono text-sm">
          <a href="https://github.com/CIRWEL/unitares-governance-plugin">github.com/CIRWEL/unitares-governance-plugin</a>
        </dd>
      </dl>
    </section>

    <hr class="hairline mt-2 mb-20"/>

    <!-- §01 THE THESIS -->
    <section id="thesis" class="py-16 lg:py-24 grid grid-cols-12 gap-6">
      <div class="col-span-12 lg:col-span-3 mb-6 lg:mb-0">
        <p class="label text-oxblood">§01 — The thesis</p>
      </div>
      <div class="col-span-12 lg:col-span-9">
        <h2 class="display text-3xl md:text-5xl mb-8 leading-tight max-w-prose">
          Runtime self-state is the missing layer.
        </h2>
        <div class="space-y-6 text-lg leading-relaxed text-ink max-w-prose">
          <p>
            The discipline of AI safety has built two strong instruments and one large gap.
            <em>Pre-deployment evaluation</em> tells you whether a model behaves on a
            benchmark. <em>Post-incident forensics</em> tells you what went wrong after
            it didn't. In between — across the hours, days, and weeks an agent is
            actually running — we have largely been guessing.
          </p>
          <p>
            CIRWEL Systems builds the runtime layer that closes the gap. Each agent
            carries a continuous, four-dimensional self-state vector. The vector is
            calibrated against a baseline specific to the agent's <em>class</em>,
            because a long-running coding assistant does not behave like an ephemeral
            parser, and neither behaves like an embodied service. Drift is detected
            against the right reference, not an averaged one. Every governance verdict
            — <span class="font-mono text-base">proceed</span>,
            <span class="font-mono text-base">guide</span>,
            <span class="font-mono text-base">pause</span>,
            <span class="font-mono text-base">reject</span> — carries a signed lineage
            back to the observation that produced it.
          </p>
          <p>
            The framework is described in
            <a href="https://github.com/CIRWEL/unitares-paper-v6">a paper</a>,
            covered by nine provisional patents, and has been governing CIRWEL's own
            development fleet without interruption since November 2025.
          </p>
        </div>
      </div>
    </section>

    <hr class="hairline"/>

    <!-- §02 THREE PILLARS -->
    <section id="pillars" class="py-16 lg:py-24 grid grid-cols-12 gap-6">
      <div class="col-span-12 lg:col-span-3 mb-6 lg:mb-0">
        <p class="label text-oxblood">§02 — Three pillars</p>
      </div>
      <div class="col-span-12 lg:col-span-9 grid md:grid-cols-3 gap-10 lg:gap-12">

        <article>
          <p class="label text-stone mb-4">i</p>
          <h3 class="display text-2xl mb-4 leading-tight">Class-conditional calibration</h3>
          <p class="text-stone leading-relaxed">
            A coding agent and a research agent are not held to the same statistics.
            UNITARES learns separate baselines per agent class from production
            telemetry, so drift in one class is not masked by noise from another.
          </p>
        </article>

        <article>
          <p class="label text-stone mb-4">ii</p>
          <h3 class="display text-2xl mb-4 leading-tight">Drift detection at runtime</h3>
          <p class="text-stone leading-relaxed">
            Continuous state observation catches behavioral drift while it is
            happening, not in the post-incident review. Verdicts arrive early enough
            to intervene, late enough to be evidence-based.
          </p>
        </article>

        <article>
          <p class="label text-stone mb-4">iii</p>
          <h3 class="display text-2xl mb-4 leading-tight">Auditable provenance</h3>
          <p class="text-stone leading-relaxed">
            Every intervention carries a signed lineage back to the observation that
            triggered it. Regulators, underwriters, and the next-shift human can
            replay the chain — not just read a verdict.
          </p>
        </article>

      </div>
    </section>

    <hr class="hairline"/>

    <!-- §03 IN PRODUCTION -->
    <section class="py-16 lg:py-24 grid grid-cols-12 gap-6">
      <div class="col-span-12 lg:col-span-3 mb-6 lg:mb-0">
        <p class="label text-oxblood">§03 — In production</p>
      </div>
      <div class="col-span-12 lg:col-span-9">
        <h2 class="display text-3xl md:text-5xl mb-8 leading-tight max-w-prose">
          Governing its own development.
        </h2>
        <div class="space-y-6 text-lg leading-relaxed text-stone max-w-prose">
          <p>
            The system you read about on this page also wrote, tested, and shipped a
            meaningful fraction of itself. CIRWEL's development fleet — a heterogeneous
            mix of long-running resident agents, short-lived coding sessions, an
            embodied edge service, and a Discord bridge — has been governed
            continuously by UNITARES since November 2025.
          </p>
          <p>
            Living under one's own framework is the cheapest credibility a research
            operator can offer. We treat it as the floor, not the ceiling.
          </p>
        </div>
      </div>
    </section>

    <hr class="hairline"/>

    <!-- §04 ENGAGE -->
    <section id="contact" class="py-16 lg:py-24 grid grid-cols-12 gap-6">
      <div class="col-span-12 lg:col-span-3 mb-6 lg:mb-0">
        <p class="label text-oxblood">§04 — Engage</p>
      </div>
      <div class="col-span-12 lg:col-span-9">
        <h2 class="display text-3xl md:text-5xl mb-10 leading-tight">
          Three ways in.
        </h2>
        <ul class="space-y-7 text-lg max-w-prose">
          <li class="grid grid-cols-12 gap-4 items-baseline">
            <span class="col-span-12 md:col-span-2 label text-stone">Read</span>
            <span class="col-span-12 md:col-span-10">
              The paper:
              <a href="https://github.com/CIRWEL/unitares-paper-v6" class="font-medium">UNITARES (Wang, 2026)</a>.
              CC-BY 4.0, citable via the DOI above.
            </span>
          </li>
          <li class="grid grid-cols-12 gap-4 items-baseline">
            <span class="col-span-12 md:col-span-2 label text-stone">Run</span>
            <span class="col-span-12 md:col-span-10">
              The open-source plugin:
              <a href="https://github.com/CIRWEL/unitares-governance-plugin" class="font-mono text-base">CIRWEL/unitares-governance-plugin</a>.
              Drops into Claude Code or Codex; emits real verdicts against a local server.
            </span>
          </li>
          <li class="grid grid-cols-12 gap-4 items-baseline">
            <span class="col-span-12 md:col-span-2 label text-stone">Write</span>
            <span class="col-span-12 md:col-span-10">
              Direct to the founder:
              <a href="mailto:founder@cirwel.org" class="font-mono text-base">founder@cirwel.org</a>.
              Funders, researchers, and integrators all welcome.
            </span>
          </li>
        </ul>
      </div>
    </section>

    <hr class="hairline"/>

  </main>

  <footer class="px-6 lg:px-12 max-w-screen-xl mx-auto py-12 grid grid-cols-12 gap-6 text-sm text-stone">
    <div class="col-span-12 md:col-span-4">
      <p class="display text-base font-medium text-ink mb-2">CIRWEL Systems</p>
      <p>Independent research operator.</p>
    </div>
    <div class="col-span-12 md:col-span-4">
      <p class="label mb-3 text-ink">Records</p>
      <p>
        ORCID <a href="https://orcid.org/0009-0006-7544-2374" class="font-mono">0009-0006-7544-2374</a><br/>
        DOI <a href="https://doi.org/10.5281/zenodo.19647159" class="font-mono">10.5281/zenodo.19647159</a>
      </p>
    </div>
    <div class="col-span-12 md:col-span-4 md:text-right">
      <p class="label mb-3 text-ink">© 2026</p>
      <p>All rights reserved unless noted.<br/>Plugin and paper carry their own licenses.</p>
    </div>
  </footer>
</BaseLayout>
```

- [ ] **Step 2: Stage and commit**

```bash
cd /Users/cirwel/projects/cirwel-site-redesign && git add src/pages/index.astro && git commit -m "feat(home): build telemetry-first homepage with receipts panel"
```

---

## Task 13: Dev-mode smoke test of the real homepage

**Files:** none (verification)

- [ ] **Step 1: Run `npm run dev` in the background**

```bash
cd /Users/cirwel/projects/cirwel-site-redesign && npm run dev
```

Use `run_in_background: true`. Wait for the "Local: http://localhost:4321/" line.

- [ ] **Step 2: Curl and grep for spec-required strings**

```bash
curl -sf http://localhost:4321/ | grep -oE '(Runtime governance|10\.5281/zenodo\.19647159|0009-0006-7544-2374|9\+ provisional|6,200|November 2025|founder@cirwel\.org|CIRWEL/unitares-governance-plugin)' | sort -u
```

Expected: returns ALL of these strings:
- `Runtime governance`
- `10.5281/zenodo.19647159`
- `0009-0006-7544-2374`
- `9+ provisional` (or just `9+ provisional`)
- `6,200`
- `November 2025`
- `founder@cirwel.org`
- `CIRWEL/unitares-governance-plugin`

If any are missing, the receipts panel did not render correctly. Fix before committing.

- [ ] **Step 3: Verify forbidden strings are absent**

```bash
curl -sf http://localhost:4321/ | grep -iE '(thermodynamic|EISV|ODE dynamics|lumen|tamagotchi)' && echo "FOUND FORBIDDEN" || echo "clean"
```

Expected: `clean`. If any match, that text leaked back in.

- [ ] **Step 4: Stop the dev server**

Use KillShell on the background bash id.

No commit needed (verification only).

---

## Task 14: Production build verification

**Files:** none (creates `dist/`, which is gitignored)

- [ ] **Step 1: Run the production build**

```bash
cd /Users/cirwel/projects/cirwel-site-redesign && npm run build
```

Expected: completes without errors. Last line should report build duration. Output goes to `dist/`.

- [ ] **Step 2: Verify `dist/index.html` exists and contains the receipts**

```bash
test -f /Users/cirwel/projects/cirwel-site-redesign/dist/index.html && grep -q "10.5281/zenodo.19647159" /Users/cirwel/projects/cirwel-site-redesign/dist/index.html && echo "OK"
```

Expected: `OK`. Anything else means the build silently dropped content.

- [ ] **Step 3: Check `dist/` size sanity**

```bash
du -sh /Users/cirwel/projects/cirwel-site-redesign/dist/
ls /Users/cirwel/projects/cirwel-site-redesign/dist/
```

Expected: `dist/` is a small directory (single-digit MB), contains `index.html` and an `_astro/` directory with hashed CSS. Should NOT contain stray React/Vite artifacts.

No commit (`dist/` is gitignored).

---

## Task 15: Local Lighthouse + axe-core check

**Files:** none (verification)

- [ ] **Step 1: Run Astro preview server in the background**

```bash
cd /Users/cirwel/projects/cirwel-site-redesign && npm run preview
```

Use `run_in_background: true`. Wait for the "Local: http://localhost:4321/" line. (Astro preview uses the production build from `dist/`.)

- [ ] **Step 2: Run Lighthouse via npx**

```bash
npx --yes lighthouse http://localhost:4321/ --quiet --chrome-flags="--headless" --only-categories=performance,accessibility,best-practices,seo --output=json --output-path=/tmp/lh-cirwel.json
```

If `npx lighthouse` is unavailable, install once with `npm install -g lighthouse` and retry.

- [ ] **Step 3: Read the scores**

```bash
python3 -c "import json; d=json.load(open('/tmp/lh-cirwel.json')); [print(k, round(v['score']*100)) for k,v in d['categories'].items()]"
```

Expected scores (from spec acceptance criteria):
- `performance` ≥ 95
- `accessibility` ≥ 95
- `best-practices` ≥ 90
- `seo` ≥ 90

If `performance` < 95 on desktop, the most likely culprits are: (a) Google Fonts blocking — check `<link rel="preconnect">` is in `BaseLayout.astro`; (b) the SVG grain image — though it's data-URI so should not be a network cost. Investigate before continuing.

- [ ] **Step 4: Run axe-core via npx**

```bash
npx --yes @axe-core/cli http://localhost:4321/ --exit
```

Expected: no critical violations. Warnings (color contrast on the `text-stone` body, possibly) are acceptable; investigate but do not necessarily fix.

If `text-stone` (`#5C544A` on `#F5F1E8`) flags contrast, verify with a contrast checker. The pair has WCAG AA contrast ratio of ~6.7:1 for normal text, well above the 4.5:1 requirement, so any axe complaint is likely a false positive against the cream background detection.

- [ ] **Step 5: Stop the preview server**

Use KillShell on the background bash id.

No commit (verification only).

---

## Task 16: Cloudflare — Email Routing for `founder@cirwel.org`

**Files:** none (Cloudflare dashboard + DNS verification only)

This task is performed by the user in the Cloudflare dashboard. Provide guidance and verify via CLI.

- [ ] **Step 1: Confirm cirwel.org is on the user's Cloudflare account**

```bash
dig cirwel.org NS +short
```

Expected: returns Cloudflare nameservers (e.g. `*.ns.cloudflare.com`). If not, stop — domain is not on Cloudflare.

- [ ] **Step 2: Direct the user to enable Cloudflare Email Routing**

Tell the user:

> In the Cloudflare dashboard, go to: **cirwel.org → Email → Email Routing**. Click **Get started**. Cloudflare will offer to add MX and TXT records automatically — accept. Then under **Routes**, add a custom address: `founder@cirwel.org` → forwards to `hikewa@gmail.com`. You will receive a verification email at `hikewa@gmail.com` — click the link.

- [ ] **Step 3: Verify MX records are live**

After the user confirms they've completed Step 2, run:

```bash
dig cirwel.org MX +short
```

Expected: returns three MX records pointing to `*.mx.cloudflare.net` (route1, route2, route3).

- [ ] **Step 4: Send a test email**

Tell the user:

> Send a test email from any account to `founder@cirwel.org`. Confirm it arrives at `hikewa@gmail.com` (it may go to spam initially — mark as not-spam if so).

Wait for the user's confirmation. If it does not arrive, check Cloudflare Email Routing's **Activity log** in the dashboard.

No git commit (dashboard config).

---

## Task 17: Cloudflare — `cirwel.org` → `cirwelsystems.com` redirect

**Files:** none (Cloudflare dashboard)

- [ ] **Step 1: Direct the user to add an A or AAAA placeholder record**

Cloudflare Redirect Rules require the hostname to resolve. Tell the user:

> In the Cloudflare dashboard, go to: **cirwel.org → DNS → Records**. Add an A record: name `@` (or `cirwel.org`), IPv4 address `192.0.2.1` (TEST-NET-1, will not resolve to anything but satisfies Cloudflare's requirement that the hostname exist), proxy status: **Proxied** (orange cloud). Repeat for `www` if needed.

- [ ] **Step 2: Direct the user to add the redirect rule**

> Go to: **cirwel.org → Rules → Redirect Rules → Create rule**.
> Name: "Redirect cirwel.org to cirwelsystems.com"
> When incoming requests match: Custom filter expression
>   `(http.host eq "cirwel.org") or (http.host eq "www.cirwel.org")`
> Then: Static redirect
>   Type: 301 (Permanent)
>   URL: `https://cirwelsystems.com${http.request.uri.path}`
>   Preserve query string: ON
> Deploy.

- [ ] **Step 3: Verify the redirect works**

```bash
curl -sI https://cirwel.org/ | head -5
curl -sI https://cirwel.org/some/path?q=1 | head -5
```

Expected: both return `HTTP/2 301` with `location:` header pointing to `https://cirwelsystems.com/` (and `/some/path?q=1` for the second). If 522 or other errors, the A record / proxy is misconfigured.

No git commit.

---

## Task 18: Cloudflare Pages — verify build settings

**Files:** none (Cloudflare dashboard verification only)

- [ ] **Step 1: Direct the user to open the existing Pages project**

> Cloudflare dashboard → **Workers & Pages → cirwel-site → Settings → Build & deployments**.

Verify these settings:
- **Build command:** `npm run build`
- **Build output directory:** `dist`
- **Root directory:** `/` (project root)
- **Production branch:** `master`
- **Node version:** 20 or higher (Astro 4 requires Node 18.17+)

If the build command was previously `vite build` — change it to `npm run build` (the Astro `package.json` defines `build` as `astro build`).

- [ ] **Step 2: Verify the GitHub integration is connected**

> Same screen → **Source** section. Confirm GitHub repo is `CIRWEL/cirwel-site` and branch `master` triggers production deploys.

If not connected, the project deploys via direct upload (`wrangler pages deploy`) — note this for Task 19 deploy method.

No git commit.

---

## Task 19: Merge to master and trigger deploy

**Files:** none (git operations)

- [ ] **Step 1: Verify the master worktree's WIP is still untouched**

```bash
git -C /Users/cirwel/projects/cirwel-site status --short
```

Expected: same WIP that was there at plan start (modified `index.html`, deleted assets, untracked `package.json`, `src/`, etc.). The master WIP must NOT have been modified by this plan.

- [ ] **Step 2: From the master worktree, stash the WIP onto a backup branch**

```bash
cd /Users/cirwel/projects/cirwel-site && git stash push --include-untracked --message "pre-redesign WIP backup"
git -C /Users/cirwel/projects/cirwel-site stash branch backup/pre-astro-rewrite-wip
```

This converts the stash into a branch with all WIP committed. The branch is local-only and not pushed. If anything was important in the WIP, it lives there.

After `stash branch`, the worktree is on the backup branch. Switch back to master:

```bash
git -C /Users/cirwel/projects/cirwel-site checkout master
```

Verify clean:

```bash
git -C /Users/cirwel/projects/cirwel-site status --short
```

Expected: empty.

- [ ] **Step 3: Merge `redesign-astro` into `master` (fast-forward)**

```bash
git -C /Users/cirwel/projects/cirwel-site merge --ff-only redesign-astro
```

If the merge is not fast-forward (someone else committed to master since the worktree was created), stop and ask the user how to handle. For a solo-founder repo this should always be ff.

- [ ] **Step 4: Push to origin**

```bash
git -C /Users/cirwel/projects/cirwel-site push origin master
```

If the Cloudflare Pages project is wired to GitHub (Task 18, Step 2), this triggers an automatic deploy. If not, run:

```bash
cd /Users/cirwel/projects/cirwel-site && npm install && npm run build && npx wrangler pages deploy dist --project-name=cirwel-site --branch=main
```

(If wrangler asks for auth, the user runs `npx wrangler login` once.)

- [ ] **Step 5: Watch the deploy**

Tell the user:

> In the Cloudflare dashboard, go to **cirwel-site → Deployments**. Watch the latest deploy go from "Building" → "Success". This typically takes 60-120s.

If the deploy fails, read the build log in the dashboard. Common failure: Node version mismatch — the project needs Node 20+, but Cloudflare Pages may default to Node 18. Set `NODE_VERSION=20` as an environment variable in Pages settings.

No additional git commit (the deploy itself is not a commit).

---

## Task 20: Production verification

**Files:** none (verification only)

- [ ] **Step 1: Verify cirwelsystems.com serves the new homepage**

```bash
curl -sf https://cirwelsystems.com/ | grep -oE '(Runtime governance|10\.5281/zenodo\.19647159|founder@cirwel\.org)' | sort -u
```

Expected: all three strings present. If old "thermodynamic" content is still served, Cloudflare's edge cache may need purging — direct the user to **Caching → Configuration → Purge Everything** in the Cloudflare dashboard.

- [ ] **Step 2: Verify forbidden content is gone from production**

```bash
curl -sf https://cirwelsystems.com/ | grep -iE '(thermodynamic|EISV|ODE dynamics|lumen)' && echo "FOUND FORBIDDEN — purge cache and re-check" || echo "clean"
```

Expected: `clean`.

- [ ] **Step 3: Verify cirwel.org redirects**

```bash
curl -sIL https://cirwel.org/ 2>&1 | grep -E '(HTTP|location)' | head -8
```

Expected: HTTP/2 301 to `https://cirwelsystems.com/`, then HTTP/2 200 from cirwelsystems.com.

- [ ] **Step 4: Production Lighthouse**

```bash
npx --yes lighthouse https://cirwelsystems.com/ --quiet --chrome-flags="--headless" --only-categories=performance,accessibility,best-practices,seo --output=json --output-path=/tmp/lh-prod.json
python3 -c "import json; d=json.load(open('/tmp/lh-prod.json')); [print(k, round(v['score']*100)) for k,v in d['categories'].items()]"
```

Expected: same thresholds as Task 15. Production may score slightly lower than local due to network variance and Cloudflare's processing — re-run twice and take the median.

- [ ] **Step 5: Final receipts visual check**

Tell the user:

> Open https://cirwelsystems.com/ in a browser. Verify visually:
> - Hero loads with "Runtime governance for heterogeneous AI-agent fleets." in serif type, "fleets." in italic
> - Cream background, oxblood accent on labels, faint paper grain visible on close inspection
> - Receipts panel shows the seven rows correctly aligned
> - All four `<code>` verdict tokens (proceed / guide / pause / reject) visible in the §01 thesis
> - Hover any link — the underline should darken from faint to oxblood
>
> Test responsive: resize the browser narrow (~375px). Mobile layout should stack the section labels above content; nav links hide.

If anything looks visibly broken, that's a bug to file as a follow-up — do not block on it unless the page is unreadable.

- [ ] **Step 6: Email contact verification**

Tell the user:

> Click the `founder@cirwel.org` link in §04. Send a one-line test email from your default mail client. Confirm delivery to `hikewa@gmail.com` (check spam).

---

## Task 21: Cleanup

**Files:** none (worktree teardown)

- [ ] **Step 1: Decide whether to keep the worktree**

If the user wants to keep the worktree around for future iteration, skip this task. Otherwise:

- [ ] **Step 2: Remove the worktree**

```bash
git -C /Users/cirwel/projects/cirwel-site worktree remove /Users/cirwel/projects/cirwel-site-redesign
git -C /Users/cirwel/projects/cirwel-site worktree prune
```

- [ ] **Step 3: Decide whether to keep the `redesign-astro` branch**

It has been merged into master. To delete:

```bash
git -C /Users/cirwel/projects/cirwel-site branch -d redesign-astro
```

The `backup/pre-astro-rewrite-wip` branch from Task 19 is kept indefinitely as a safety net.

---

## Acceptance criteria checklist (final pass)

After all tasks complete, verify each acceptance criterion from the spec:

- [ ] Lighthouse desktop performance ≥ 95 (Task 20 Step 4)
- [ ] Lighthouse mobile performance ≥ 90 (re-run Task 20 with `--preset=mobile`)
- [ ] FCP ≤ 1.5s on cable (visible in Lighthouse JSON: `audits.first-contentful-paint.numericValue`)
- [ ] axe-core no critical violations (Task 15 Step 4)
- [ ] All copy matches spec receipts (Task 13 Step 2 + Task 20 Step 1)
- [ ] Live at cirwelsystems.com via existing Cloudflare Pages project (Task 20 Step 1)
- [ ] `cirwel.org` redirects to cirwelsystems.com (Task 20 Step 3)
- [ ] `founder@cirwel.org` delivers to a real inbox (Task 20 Step 6)
- [ ] No EISV variable names, no ODE references, no Lumen-as-product framing (Task 13 Step 3 + Task 20 Step 2)

---

## Open follow-ups (out of scope for this plan)

- `/paper`, `/patents`, `/blog` subpages (referenced in nav, currently 404)
- Two-audience split (3b: cirwel.org for research, cirwelsystems.com for commercial) — deferred until single-site is proven clean
- Migration of any content from the old React app (Patents portfolio page, IP portfolio, Industries) — clean-rewrite, not port
- Visual identity / logo refresh
- OpenGraph image asset (`og:image` meta tag is currently absent — add a `public/og.png` later)
