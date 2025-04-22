const alertColors = {
    'info': '#0073e5',
    'info-content': '#ffffff',
    'success': '#50c878',
    'success-content': '#141516',
    'warning': '#eec200',
    'warning-content': '#141516',
    'error': '#f04343',
    'error-content': '#ffffff',
}
const baseArgusColors = {
    'primary': '#006d91',
    'primary-content': '#d1e1e9',
    'secondary': '#f3b61f',
    'secondary-content': '#140c00',
    'accent': '#c84700',
    'accent-content': '#f8dbd1',
    'neutral': '#006d91',
    'neutral-content': '#d1e1e9',
    'base-100': '#edfaff',
    'base-200': '#ced9de',
    'base-300': '#b0babd',
    'base-content': '#141516',
    ...alertColors
}
const incidentColors = {
    '--color-incident-clear': '80, 200, 120', // #50c878, same as success
    '--color-incident-minor': '255, 255, 0', // #ffff00
    '--color-incident-major': '255, 166, 0', // #ffa600
    '--color-incident-critical': '240, 67, 67', // #f04343, same as critical
}


module.exports = {
    content: [
{{ projectpaths }}
        'src/geant_argus/**/*.py',
    ],
    theme: {
        borderWidth: {
            DEFAULT: '2px',
            '0': '0',
            '1': '1px',
            '2': '2px',
            '3': '3px',
            '4': '4px',
            '6': '6px',
            '8': '8px',
        },
        extend: {
            colors: {
                'incident-major': 'rgba(var(--color-incident-major), <alpha-value>)',
                'incident-minor': 'rgba(var(--color-incident-minor), <alpha-value>)',
                'incident-critical': 'rgba(var(--color-incident-critical), <alpha-value>)',
                'incident-warning': 'var(--fallback-n,oklch(var(--n)))', // neutral
                'incident-clear': 'rgba(var(--color-incident-clear), <alpha-value>)',
            },
            height: {
                '13': '3.25rem',
            },
            lineHeight: {
                '2': '0.5rem',
            },
            animation: {
                'blink': 'blink 2s infinite'
            },
            keyframes: {
                blink: {
                    '0%, 49%, 100%': { opacity: '1' },
                    '50%, 99%': { opacity: '0' },
                }
            },
        },
    },
    safelist: [
        // these classes are dynamically generated so not seen by tailwind
        {
            pattern: /(bg|border)-incident-(clear|warning|minor|major|critical)/,
        },
        {
            pattern: /bg-(success|warning|error|slate-300)/,
        },
        "htmx-request"
    ],
    daisyui: {
        themes: [{
            'light': {
                ...require("daisyui/src/theming/themes")["light"],
                ...incidentColors
            },
            'dark': {
                ...require("daisyui/src/theming/themes")["dark"],
                ...incidentColors,
                '--color-incident-critical': '182, 35, 35',
                '--color-incident-major': '195, 101, 1',
                '--color-incident-minor': '146, 137, 0',
                '--color-incident-clear': '18, 103, 0',
            },
            'argus': {
                ...baseArgusColors,
                ...incidentColors
            },
            'geant': {
                ...baseArgusColors,
                'accent': baseArgusColors['neutral'],
                'accent-content': baseArgusColors['neutral-content'],
                'warning': '#eec200',
                ...incidentColors
            },
            "geant-test": {
                "primary": "#a8c5d5",
                "primary-content": "#000000",
                "secondary": "#faedd6",
                "secondary-content": "#000000",
                "accent": "#b4cc7f",
                "accent-content": "#000000",
                "neutral": "#d5c8b0",
                "neutral-content": "#000000",
                "base-100": "#f8f7f0",
                "base-200": "#e2e5d9",
                "base-300": "#cfd3c6",
                "base-content": "#000000",
                ...alertColors,
                ...incidentColors
            },
            "geant-uat": {
                "primary": "#d1a7c4",
                "primary-content": "#3E143D",
                "secondary": "#e6f3e8",
                "secondary-content": "#464847",
                "accent": "#e8c8d1",
                "accent-content": "#6B1919",
                "neutral": "#c4a7d1",
                "neutral-content": "#4D0000",
                "base-100": "#f5f7f2",
                "base-200": "#e0e5da",
                "base-300": "#cfd3c6",
                "base-content": "#284336",
                ...alertColors,
                ...incidentColors
            },
            "geant-prod": {
                "primary": "#a78ac4",
                "primary-content": "#1E003D",
                "secondary": "#d3e8e6",
                "secondary-content": "#2E3D3E",
                "accent": "#d1b8c8",
                "accent-content": "#3B1919",
                "neutral": "#a7c4d1",
                "neutral-content": "#2D0000",
                "base-100": "#f0f2f5",
                "base-200": "#d4d9e0",
                "base-300": "#b8c3d0",
                "base-content": "#223344",
                ...alertColors,
                ...incidentColors
            }
        }],
      },

    plugins: [
        require('daisyui')
    ],
}
