/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                brand: {
                    navy: '#0F172A',
                    emerald: '#0F766E',
                    offwhite: '#F8FAFC',
                    lightrose: '#FEF2F2',
                    darkred: '#B91C1C',
                    amber: '#D97706',
                    safe: '#065F46'
                }
            }
        },
    },
    plugins: [],
}
