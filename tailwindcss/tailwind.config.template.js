module.exports = {
    content: [
{{ tailwind_content }}
        "src/geant_argus/geant_argus/templatetags/**/*.py",
    ],
    theme: {
        borderWidth: {
            DEFAULT: '2px',
        },
        extend: {
            colors: {
                "incident-major": "rgba(var(--color-incident-major), <alpha-value>)",
                "incident-minor": "rgba(var(--color-incident-minor), <alpha-value>)",
                "incident-critical": "rgba(var(--color-incident-critical), <alpha-value>)",
                "incident-warning": "rgba(var(--color-incident-warning), <alpha-value>)",
                "incident-clear": "rgba(var(--color-incident-clear), <alpha-value>)",
              },
        },
    },
    safelist: [
        // these classes are dynamically generated so not seen by tailwind
        "bg-incident-major/50",
        "bg-incident-minor/50",
        "bg-incident-critical/50",
        "bg-incident-warning/50",
        "bg-incident-clear/50",
    ],
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
                "warning": "#eec200",
                "warning-content": "#140200",
                "error": "#e5545a",
                "error-content": "#120203",
                "--color-incident-clear": '80, 200, 120',
                "--color-incident-warning": '237, 250, 255', // same as base-100
                "--color-incident-minor": '238, 194, 0',
                "--color-incident-major": '238, 155, 0',
                "--color-incident-critical": '238, 32, 0',
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
