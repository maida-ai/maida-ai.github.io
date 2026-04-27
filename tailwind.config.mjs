/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
  theme: {
    extend: {
      colors: {
        bg: '#0a0a0a',
        surface: '#111111',
        border: '#1e1e1e',
        'border-light': '#2a2a2a',
        green: {
          DEFAULT: '#00ff88',
          dim: '#00cc6e',
          glow: 'rgba(0,255,136,0.15)',
          'glow-sm': 'rgba(0,255,136,0.08)',
        },
        text: {
          primary: '#f0f0f0',
          secondary: '#888888',
          muted: '#555555',
        },
        warning: '#ffaa00',
        danger: '#ff4444',
        info: '#4488ff',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      backgroundImage: {
        'grid-pattern': `linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px)`,
        'green-radial': 'radial-gradient(ellipse 80% 40% at 50% 0%, rgba(0,255,136,0.07) 0%, transparent 70%)',
        'green-spot': 'radial-gradient(circle at center, rgba(0,255,136,0.12) 0%, transparent 60%)',
      },
      backgroundSize: {
        'grid': '40px 40px',
      },
      boxShadow: {
        'green': '0 0 30px rgba(0,255,136,0.2)',
        'green-sm': '0 0 12px rgba(0,255,136,0.15)',
        'green-lg': '0 0 60px rgba(0,255,136,0.15)',
        'card': '0 1px 0 rgba(255,255,255,0.04), inset 0 1px 0 rgba(255,255,255,0.02)',
      },
      animation: {
        'pulse-slow': 'pulse 4s cubic-bezier(0.4,0,0.6,1) infinite',
        'blink': 'blink 1s step-end infinite',
        'fade-up': 'fadeUp 0.6s ease forwards',
        'scan': 'scan 3s linear infinite',
      },
      keyframes: {
        blink: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0' },
        },
        fadeUp: {
          from: { opacity: '0', transform: 'translateY(20px)' },
          to: { opacity: '1', transform: 'translateY(0)' },
        },
        scan: {
          '0%': { backgroundPosition: '0 0' },
          '100%': { backgroundPosition: '0 100%' },
        },
      },
    },
  },
  plugins: [],
};
