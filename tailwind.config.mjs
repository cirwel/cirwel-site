/**
 * Two impressions of one plate.
 *
 * LIGHT is the house register: a copperplate line engraving pulled on laid
 * cream. DARK is not that register inverted — it is the same plate pulled as a
 * MEZZOTINT, the one intaglio process that works dark-to-light: the ground is
 * bitten to print solid, and the lights are burnished back out of it. So the
 * dark page is warm bistre-black with the lights burnished in ivory, and the
 * oxblood rises to a burnished sanguine, because a 0.5px hairline in #7A1F1F
 * on black does not survive the pull.
 *
 * Each dark token holds the SAME contrast ratio against its ground that its
 * light counterpart holds against cream (rules ~1.5:1, secondary text ~7:1,
 * accent >=4.5:1). That is what keeps the two impressions the same design and
 * not two designs.
 *
 * The hex literals below are load-bearing beyond documentation:
 * cirwel.github.io/scripts/check-index.py leg E parses THIS FILE for
 * `name: '#hex'` pairs and asserts each one appears in that page's CSS. Adding
 * a token here therefore requires mirroring it there. Keep the literal form.
 */
const light = {
  cream:   '#F5F1E8',
  ink:     '#1A1612',
  oxblood: '#7A1F1F',
  ochre:   '#B8862F',
  stone:   '#5C544A',
  sepia:   '#C9C0AE',
};

const dark = {
  creamDark:   '#15110D',
  inkDark:     '#E8E0D0',
  oxbloodDark: '#D0604A',
  ochreDark:   '#D6A44A',
  stoneDark:   '#A89F90',
  sepiaDark:   '#3A3229',
};

/* The six names stay ROLES — `text-stone` means "secondary voice", not "grey".
   Each resolves through a custom property so one media query re-inks the whole
   page without touching a single utility class in the markup. */
const role = (name) => `rgb(var(--c-${name}) / <alpha-value>)`;

export { light as palette, dark as paletteDark };

/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
  theme: {
    extend: {
      colors: {
        cream:   role('cream'),
        ink:     role('ink'),
        oxblood: role('oxblood'),
        ochre:   role('ochre'),
        stone:   role('stone'),
        sepia:   role('sepia'),
      },
      fontFamily: {
        // Two roles, two faces. `serif` is the reading face applied to <body>;
        // the didone is reached through the .display class, never as a default.
        serif:   ['"EB Garamond Variable"', 'Garamond Fallback', 'ui-serif', 'Georgia', 'serif'],
        display: ['"Bodoni Moda Variable"', 'Bodoni Fallback', 'Didot', 'Georgia', 'serif'],
        mono:    ['"JetBrains Mono"', 'ui-monospace', 'monospace'],
      },
      maxWidth: {
        prose: '40rem',
      },
    },
  },
  plugins: [],
};
