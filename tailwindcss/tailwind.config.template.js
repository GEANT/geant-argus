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
    'info': '#0073e5',
    'info-content': '#000512',
    'success': '#008700',
    'success-content': '#d3e7d1',
    'warning': '#ee4900',
    'warning-content': '#140200',
    'error': '#e5545a',
    'error-content': '#120203',
}
const incidentColors = {
    '--color-incident-clear': '80, 200, 120',
    '--color-incident-warning': '237, 250, 255', // same as base-100
    '--color-incident-minor': '238, 194, 0',
    '--color-incident-major': '238, 155, 0',
    '--color-incident-critical': '240, 67, 67',
}

module.exports = {
    content: [
        {{ tailwind_content }}
'src/geant_argus/geant_argus/templatetags/**/*.py',
    ],
theme: {
    borderWidth: {
        DEFAULT: '2px',
        },
    extend: {
        colors: {
            'incident-major': 'rgba(var(--color-incident-major), <alpha-value>)',
                'incident-minor': 'rgba(var(--color-incident-minor), <alpha-value>)',
                'incident-critical': 'rgba(var(--color-incident-critical), <alpha-value>)',
                'incident-warning': 'rgba(var(--color-incident-warning), <alpha-value>)',
                'incident-clear': 'rgba(var(--color-incident-clear), <alpha-value>)',
            },
        },
    },

safelist: [
    // these classes are dynamically generated so not seen by tailwind
    {
        pattern: /bg-incident-(clear|warning|minor|major|critical)\/50/,
    },
],
    daisyui: {
        themes: [{
            'light': {
                ...require("daisyui/src/theming/themes")["light"],
                ...incidentColors
            },
            'dark': {
                ...require("daisyui/src/theming/themes")["dark"],
                ...incidentColors
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
                "primary-content": "#e4f0f5",
                "secondary": "#faedd6",
                "secondary-content": "#6e5840",
                "accent": "#b4cc7f",
                "accent-content": "#f0f5e4",
                "neutral": "#d5c8b0",
                "neutral-content": "#f5f0e4",
                "base-100": "#f7f8f2",
                "base-200": "#e2e5d9",
                "base-300": "#cfd3c6",
                "base-content": "#4a4b4c",
                "info": "#85baf0",
                "info-content": "#4d5b6e",
                "success": "#81ce81",
                "success-content": "#e7f2e6",
                "warning": "#f5a48f",
                "warning-content": "#6e463a",
                "error": "#f2a5a9",
                "error-content": "#4d2a2b",
                ...incidentColors
            },
            "geant-uat": {
                "primary": "#d1a7c4",
                "primary-content": "#f7ebf3",
                "secondary": "#e6f3e8",
                "secondary-content": "#405947",
                "accent": "#d1c4a7",
                "accent-content": "#f3f0e7",
                "neutral": "#c4a7d1",
                "neutral-content": "#f5ebf7",
                "base-100": "#f5f7f2",
                "base-200": "#e0e5da",
                "base-300": "#ccd3c6",
                "base-content": "#464847",
                "info": "#a7c4d1",
                "info-content": "#4b5b65",
                "success": "#a7d1a7",
                "success-content": "#e7f2e7",
                "warning": "#d1b7a7",
                "warning-content": "#594a3e",
                "error": "#d1a7a7",
                "error-content": "#4a2d2d",
                ...incidentColors
            },
            "geant-prod": {
                "primary": "#f2c94c",
                "primary-content": "#fff9e0",
                "secondary": "#f2e5d6",
                "secondary-content": "#1b4d73",
                "accent": "#ff6f61",
                "accent-content": "#ffe6e2",
                "neutral": "#d9b7a1",
                "neutral-content": "#f5ebdf",
                "base-100": "#f9f7f6",
                "base-200": "#e2e1e2",
                "base-300": "#c8c6c8",
                "base-content": "#4a4a4a",
                "info": "#56c5e0",
                "info-content": "#0e4e6b",
                "success": "#6fcf6f",
                "success-content": "#e6f7e6",
                "warning": "#ffb74d",
                "warning-content": "#5c4d27",
                "error": "#f2a3a3",
                "error-content": "#6e2c2c",
                ...incidentColors
            }
        }],
      },

plugins: [
    require('@tailwindcss/aspect-ratio'),
    require('daisyui')
],
}
