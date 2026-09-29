/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: '#FF4400',
        'primary-light': '#FF6B35',
        'orange-bg': '#FFF5F0',
        'orange-light': '#FFE8DD',
        'orange-glow': '#FFD5C8',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
