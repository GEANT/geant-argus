module.exports = {
    content: [
{{ tailwind_content }}
    ],
    theme: {
        borderWidth: {
            DEFAULT: '2px',
        },
        extend: {},
    },
    daisyui: {
        themes: ["light", "dark",
            {
            "argus": {
                "primary": "#006d91",
                "primary-content": "#d1e1e9",
                "secondary": "#f3b61f",
                "secondary-content": "#140c00",
                "accent": "#006d91",
                "accent-content": "#d1e1e9",
                "neutral": "#006d91",
                "neutral-content": "#d1e1e9",
                "base-100": "#edfaff",
                "base-200": "#ced9de",
                "base-300": "#b0babd",
                "base-content": "#141516",
                "info": "#0073e5",
                "info-content": "#000512",
                "success": "#008700",
                "success-content": "#d3e7d1",
                "warning": "#ee4900",
                "warning-content": "#140200",
                "error": "#e5545a",
                "error-content": "#120203",
            }
        }],
      },
    plugins: [
        require('@tailwindcss/forms'),
        require('@tailwindcss/typography'),
        require('@tailwindcss/aspect-ratio'),
        require('daisyui')
    ],
}
