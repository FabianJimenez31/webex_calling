/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: [
    './pages/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
    './app/**/*.{ts,tsx}',
    './src/**/*.{ts,tsx}',
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
      colors: {
        // Davivienda Portal Colors (Real from website)
        davivienda: {
          red: {
            50: '#FFF0F0',
            100: '#FFE0E0',
            200: '#FFC2C2',
            300: '#FF9999',
            400: '#FF5C5D',
            500: '#E30519',  // Shojo's Blood - Primary red (navigation, buttons, CTA)
            600: '#C70416',  // Hover state
            700: '#A80313',  // Active state
            800: '#8A0210',
            900: '#6B010D',
          },
          gold: {
            50: '#FFF9F0',
            100: '#FFEFD6',
            200: '#FFDFAD',
            300: '#FFCF85',
            400: '#FFBF5C',
            500: '#F39800',  // Kin Gold - Only in logo house roof
            600: '#D68600',
            700: '#B97400',
            800: '#9C6200',
            900: '#7F5000',
          },
          yellow: {
            50: '#FFFEF5',
            100: '#FFFCE0',
            200: '#FFF9C2',
            300: '#FFF6A3',
            400: '#FFF385',
            500: '#FEE000',  // Tibetan Yellow - Only in logo details
            600: '#E0C600',
            700: '#C2AD00',
            800: '#A39300',
            900: '#857A00',
          },
          gray: {
            50: '#FAFAFA',
            100: '#F5F5F5',  // Light gray - Section backgrounds
            200: '#E5E5E5',
            300: '#D4D4D4',
            400: '#A3A3A3',
            500: '#737373',
            600: '#525252',
            700: '#404040',
            800: '#262626',
            900: '#010101',  // Binary Black - Dark backgrounds, text
          },
        },
        // shadcn/ui semantic colors adapted to Davivienda
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
      fontFamily: {
        sans: ['Davivienda', 'Manrope', 'sans-serif'],
      },
      fontSize: {
        'h1': ['56px', { lineHeight: '73px', fontWeight: '700' }],
        'h2': ['36px', { lineHeight: '1.3', fontWeight: '700' }],
        'h3': ['30px', { lineHeight: '1.4', fontWeight: '600' }],
        'h4': ['24px', { lineHeight: '1.5', fontWeight: '600' }],
        'h5': ['20px', { lineHeight: '1.5', fontWeight: '500' }],
        'h6': ['18px', { lineHeight: '1.5', fontWeight: '500' }],
        'body-lg': ['18px', { lineHeight: '1.6', fontWeight: '400' }],
        'body': ['16px', { lineHeight: '1.6', fontWeight: '400' }],
        'body-sm': ['14px', { lineHeight: '1.5', fontWeight: '400' }],
        'caption': ['12px', { lineHeight: '1.4', fontWeight: '400' }],
      },
      spacing: {
        'xs': '4px',
        'sm': '8px',
        'md': '16px',
        'lg': '24px',
        'xl': '32px',
        '2xl': '48px',
        '3xl': '64px',
      },
      boxShadow: {
        'sm': '0 1px 2px rgba(0, 0, 0, 0.05)',
        'md': '0 4px 6px rgba(0, 0, 0, 0.1)',
        'lg': '0 10px 15px rgba(0, 0, 0, 0.1)',
        'xl': '0 20px 25px rgba(0, 0, 0, 0.1)',
        'davivienda': '0 2px 4px rgba(227, 5, 25, 0.2)',  // #E30519 - Shojo's Blood
        'davivienda-lg': '0 4px 12px rgba(227, 5, 25, 0.3)',
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
        "slide-in-from-right": {
          from: { transform: "translateX(100%)" },
          to: { transform: "translateX(0)" },
        },
        "slide-out-to-right": {
          from: { transform: "translateX(0)" },
          to: { transform: "translateX(100%)" },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
        "slide-in": "slide-in-from-right 0.3s ease-out",
        "slide-out": "slide-out-to-right 0.3s ease-out",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
}
