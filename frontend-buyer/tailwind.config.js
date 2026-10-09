/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: '#17483B',
        'primary-light': '#2B6253',
        'orange-bg': '#F0F3E8',
        'orange-light': '#DFF263',
        'orange-glow': '#E8F49D',
        'footer-dark': '#123B31',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      maxWidth: {
        'tb': '1440px',
      },
    },
  },
  plugins: [],
}
