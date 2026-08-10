/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./index.html'],
  theme: {
    extend: {
      colors: {
        kanazawa: {
          red: '#9E2A2B',
          gold: '#C5A059',
          goldlight: '#F4E8C1',
          dark: '#1C1D21',
          slate: '#2D3142',
          washi: '#FAF8F5',
          card: '#FFFFFF',
          green: '#4A6B5D',
          blue: '#1B4965'
        }
      },
      fontFamily: {
        sans: ['"Noto Sans TC"', 'sans-serif'],
        serif: ['"Zen Old Mincho"', 'serif']
      }
    }
  },
  plugins: []
};
