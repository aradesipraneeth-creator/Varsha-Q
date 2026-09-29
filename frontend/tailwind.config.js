/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        ivory: {
          50: '#FCFBF9',
          100: '#FAF8F5',
          200: '#F5F2EB',
          300: '#EBE5D8',
          400: '#DFD7C5',
          500: '#CFC3AC',
        },
        charcoal: {
          900: '#1C1917',
          800: '#292524',
          700: '#44403C',
          600: '#57534E',
          500: '#78716C',
        },
        terracotta: {
          DEFAULT: '#B85D3B',
          50: '#FBF2EE',
          100: '#F7E4DC',
          200: '#EEC7B7',
          300: '#E3A68F',
          400: '#CE7856',
          500: '#B85D3B',
          600: '#9C4729',
          700: '#7E361E',
        },
        atmospheric: {
          DEFAULT: '#2C5282',
          light: '#4B7B94',
          subtle: '#EBF3F8',
          dark: '#1A365D',
        },
        borderMuted: '#E7E2DA',
      },
      fontFamily: {
        serif: ['Playfair Display', 'Newsreader', 'Georgia', 'serif'],
        sans: ['Inter', 'Plus Jakarta Sans', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
    },
  },
  plugins: [],
}
