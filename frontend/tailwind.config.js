/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      colors: {
        // Warm stone palette — the core of the design
        sand: {
          50:  '#faf8f5',
          100: '#f3efe9',
          200: '#e8e0d6',
          300: '#d4c8b8',
          400: '#bba997',
          500: '#a08b76',
          600: '#8a7462',
          700: '#6f5d4f',
          800: '#5a4b40',
          900: '#3d342c',
          950: '#211c18',
        },
        // Accent — warm amber/copper
        copper: {
          50:  '#fdf6ee',
          100: '#f9e8d0',
          200: '#f2ce9e',
          300: '#ebb06a',
          400: '#e49541',
          500: '#dc7b25',
          600: '#c35f1a',
          700: '#a34618',
          800: '#85381b',
          900: '#6e2f19',
          950: '#3c160a',
        },
        // Background system
        surface: {
          0:   '#0f0d0b',
          1:   '#161311',
          2:   '#1e1a17',
          3:   '#272220',
          4:   '#312b28',
        },
      },
      borderRadius: {
        'xl': '0.875rem',
        '2xl': '1.125rem',
        '3xl': '1.5rem',
      },
      boxShadow: {
        'glow': '0 0 20px rgba(220, 123, 37, 0.08)',
        'glow-lg': '0 0 40px rgba(220, 123, 37, 0.12)',
        'card': '0 1px 3px rgba(0,0,0,0.4), 0 1px 2px rgba(0,0,0,0.3)',
        'card-hover': '0 4px 12px rgba(0,0,0,0.5), 0 2px 4px rgba(0,0,0,0.4)',
        'inner-glow': 'inset 0 1px 0 rgba(255,255,255,0.03)',
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'hero-glow': 'radial-gradient(ellipse 60% 50% at 50% -10%, rgba(220, 123, 37, 0.08), transparent)',
        'card-shine': 'linear-gradient(135deg, rgba(255,255,255,0.02) 0%, transparent 50%, rgba(255,255,255,0.01) 100%)',
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-out forwards',
        'fade-up': 'fadeUp 0.6s ease-out forwards',
        'slide-in': 'slideIn 0.4s ease-out forwards',
        'pulse-soft': 'pulseSoft 3s ease-in-out infinite',
        'shimmer': 'shimmer 2s linear infinite',
        'float': 'float 6s ease-in-out infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        fadeUp: {
          '0%': { opacity: '0', transform: 'translateY(16px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideIn: {
          '0%': { opacity: '0', transform: 'translateX(-8px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
        pulseSoft: {
          '0%, 100%': { opacity: '0.5' },
          '50%': { opacity: '1' },
        },
        shimmer: {
          '0%': { backgroundPosition: '200% 0' },
          '100%': { backgroundPosition: '-200% 0' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-8px)' },
        },
      },
    },
  },
  plugins: [],
}
