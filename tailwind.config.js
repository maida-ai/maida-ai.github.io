/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./templates/**/*.html'],
  theme: {
    extend: {
      colors: {
        bg: '#0f1110',
        surface: '#161916',
        border: '#292d2a',
        'border-light': '#3b403c',
        green: {
          DEFAULT: '#78d6a2',
          dim: '#5fc48c',
          glow: 'rgba(120,214,162,0.12)',
          'glow-sm': 'rgba(120,214,162,0.06)',
        },
        text: {
          primary: '#f3f2ed',
          secondary: '#aeb3ad',
          muted: '#747a74',
        },
        warning: '#e8a35f',
        danger: '#ed7958',
        info: '#7fa6d9',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      boxShadow: {
        'card': '0 1px 0 rgba(255,255,255,0.04), inset 0 1px 0 rgba(255,255,255,0.02)',
      },
    },
  },
  plugins: [],
};
