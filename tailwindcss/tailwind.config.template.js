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
        themes: ['light', 'dark',
        {
            'argus': {
                ...baseArgusColors,
                ...incidentColors
            },
        },
        {
            'geant': {
                ...baseArgusColors,
                'accent': baseArgusColors['neutral'],
                'accent-content': baseArgusColors['neutral-content'],
                'warning': '#eec200',
                ...incidentColors
            }
        }],
      },

    plugins: [
        require('@tailwindcss/aspect-ratio'),
        require('daisyui')
    ],
}
