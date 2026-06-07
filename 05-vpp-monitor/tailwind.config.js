/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: ['./src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        // Energy-themed accent palette
        solar: { 400: '#34d399', 500: '#10b981' },      // emerald — solar yield
        battery: { 400: '#22d3ee', 500: '#06b6d4' },    // cyan — battery SOC
        price: { 400: '#fbbf24', 500: '#f59e0b' },      // amber — day-ahead price
        grid: { 400: '#fb7185', 500: '#f43f5e' },       // rose — grid import
        margin: { 400: '#a78bfa', 500: '#8b5cf6' },     // violet — margins
      },
    },
  },
  plugins: [],
};
