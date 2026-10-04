/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./templates/**/*.html'],
  theme: {
    extend: {
      colors: {
        /* Palette/semantic tokens from static/brand-tokens.css */
        bg: 'var(--maida-ink)',
        surface: 'color-mix(in srgb, var(--maida-paper) 6%, var(--maida-ink))',
        border: 'var(--maida-rule-on-ink)',
        'border-light': 'color-mix(in srgb, var(--maida-paper) 22%, var(--maida-ink))',
        green: {
          DEFAULT: 'var(--maida-mint)',
          dim: 'color-mix(in srgb, var(--maida-mint) 82%, var(--maida-ink))',
          glow: 'color-mix(in srgb, var(--maida-mint) 12%, transparent)',
          'glow-sm': 'color-mix(in srgb, var(--maida-mint) 6%, transparent)',
        },
        text: {
          primary: 'var(--maida-paper)',
          secondary: 'color-mix(in srgb, var(--maida-paper) 68%, var(--maida-ink))',
          muted: 'color-mix(in srgb, var(--maida-paper) 45%, var(--maida-ink))',
        },
        warning: 'color-mix(in srgb, var(--maida-coral) 70%, var(--maida-mint))',
        danger: 'var(--maida-coral)',
        info: 'color-mix(in srgb, var(--maida-mint) 35%, var(--maida-paper))',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      boxShadow: {
        'card': '0 1px 0 color-mix(in srgb, var(--maida-paper) 4%, transparent), inset 0 1px 0 color-mix(in srgb, var(--maida-paper) 2%, transparent)',
      },
    },
  },
  plugins: [],
};
