/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ["class"],
  content: [
    "./pages/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./app/**/*.{ts,tsx}",
    "./src/**/*.{ts,tsx}",
  ],
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1400px",
      },
    },
    extend: {
      fontFamily: {
        sans: ['"IBM Plex Sans"', "sans-serif"],
        heading: ['"Space Grotesk"', "sans-serif"],
        mono: ['"JetBrains Mono"', "monospace"],
      },
      colors: {
        border: "#1C2230",
        input: "#1C2230",
        ring: "#4F8CFF",
        background: "#07090F",
        foreground: "#F8FAFC",
        primary: {
          DEFAULT: "#4F8CFF",
          foreground: "#ffffff",
        },
        secondary: {
          DEFAULT: "#8B5CF6",
          foreground: "#ffffff",
        },
        accent: {
          DEFAULT: "#1C2230",
          foreground: "#F8FAFC",
        },
        danger: {
          DEFAULT: "#EF4444",
        },
        success: {
          DEFAULT: "#22C55E",
        },
        warning: {
          DEFAULT: "#F59E0B",
        },
        muted: {
          DEFAULT: "#0F1117",
          foreground: "#94A3B8",
        },
        card: {
          DEFAULT: "#0F1117",
          foreground: "#F8FAFC",
        },
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'noise': 'url("data:image/svg+xml,%3Csvg viewBox=%220 0 200 200%22 xmlns=%22http://www.w3.org/2000/svg%22%3E%3Cfilter id=%22noiseFilter%22%3E%3CfeTurbulence type=%22fractalNoise%22 baseFrequency=%220.65%22 numOctaves=%223%22 stitchTiles=%22stitch%22/%3E%3C/filter%3E%3Crect width=%22100%25%22 height=%22100%25%22 filter=%22url(%23noiseFilter)%22/%3E%3C/svg%3E")',
      },
      boxShadow: {
        'glow': '0 0 20px -5px rgba(79, 140, 255, 0.4)',
        'glow-danger': '0 0 20px -5px rgba(239, 68, 68, 0.4)',
        'glass': 'inset 0 1px 1px 0 rgba(255, 255, 255, 0.05)',
      },
      borderRadius: {
        lg: "16px",
        md: "12px",
        sm: "8px",
      },
      keyframes: {
        "accordion-down": {
          from: { height: 0 },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: 0 },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
};
