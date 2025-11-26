import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "var(--background)",
        foreground: "var(--foreground)",
        // Primary colors from reference
        "primary-orange": "#F29F67",
        "primary-navy": "#1E1E2C",
        // Supporting colors
        "accent-blue": "#3B8FF3",
        "accent-teal": "#34B1AA",
        "accent-yellow": "#E0B50F",
        // Semantic colors
        "admin-bg": "#F7F7F7",
        "admin-card": "#ffffff",
        "admin-sidebar": "#1E1E2C",
        "admin-header": "#1E1E2C",
        "admin-primary": "#F29F67",
        "admin-hover": "#F29F67",
        "admin-blue": "#3B8FF3",
        "admin-teal": "#34B1AA",
        "admin-yellow": "#E0B50F",
        "admin-text": "#1E1E2C",
        "admin-text-light": "#6c757d",
        "admin-border": "#e9ecef",
      },
    },
  },
  plugins: [],
};
export default config;
