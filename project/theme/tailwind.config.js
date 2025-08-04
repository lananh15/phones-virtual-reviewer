module.exports = {
  content: [
    '../templates/**/*.html',
    './src/**/*.{js,css}',
  ],
  theme: {
    extend: {
      colors: {
        black: '#1E1E1E',
        blue: '#3096E1',
      },
    },
  },
  plugins: [require("daisyui")],
};