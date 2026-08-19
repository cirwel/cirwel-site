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
