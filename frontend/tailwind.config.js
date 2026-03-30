/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{js,jsx}',
  ],
  theme: {
    extend: {
      fontFamily: {
        display: ['Syne', 'sans-serif'],
        body:    ['Figtree', 'sans-serif'],
      },
      keyframes: {
        'blob-pulse': {
          '0%, 100%': { transform: 'scale(1) translate(0, 0)' },
          '33%':      { transform: 'scale(1.08) translate(-20px, 10px)' },
          '66%':      { transform: 'scale(0.95) translate(15px, -10px)' },
        },
      },
      animation: {
        'blob-pulse': 'blob-pulse 8s ease-in-out infinite',
      },
    },
  },
  plugins: [],
}