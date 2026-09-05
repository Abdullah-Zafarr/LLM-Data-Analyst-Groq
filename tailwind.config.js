/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        canvas: "#06090F",
        panel: "#0A0F1D",
        card: "#0F172A",
        cardHover: "#162038",
        cyanAccent: "#06B6D4",
        indigoAccent: "#6366F1",
        emeraldAccent: "#10B981",
        amberAccent: "#F59E0B",
        roseAccent: "#F43F5E",
      },
      fontFamily: {
        sans: ["var(--font-fira-sans)", "system-ui", "sans-serif"],
        mono: ["var(--font-fira-code)", "monospace"],
      },
    },
  },
  plugins: [],
};
