function withOpacity(variableName) {
  return ({ opacityValue }) => {
    if (opacityValue !== undefined) {
      return `rgba(var(${variableName}), ${opacityValue})`
    }
    return `rgb(var(${variableName}))`
  }
}


/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{html,js}"],
  theme: {
    extend: {
      textColor: {
        skin: {
          base: withOpacity('--color-text-base'),
          muted: withOpacity('--color-text-muted'),
          inverted: withOpacity('--color-text-inverted'),
          'active-section': withOpacity('--color-text-active-section'),
          'disabled-section': withOpacity('--color-text-disabled-section'),
          'table-row': withOpacity('--color-table-row-text'),
          'table-hover': withOpacity('--color-table-hover-text'),
          'table-header': withOpacity('--color-table-header-text'),
        },
      },
      backgroundColor: {
        skin: {
          fill: withOpacity('--color-fill'),
          'button-accent': withOpacity('--color-button-accent'),
          'button-accent-hover': withOpacity('--color-button-accent-hover'),
          'button-muted': withOpacity('--color-button-muted'),
          'active-section': withOpacity('--color-fill-active-section'),
          'disabled-section': withOpacity('--color-fill-disabled-section'),
          'active-section-body': withOpacity('--color-fill-active-section-body'),
          'table-head': withOpacity('--color-fill-table-head'),
          'table-row': withOpacity('--color-table-row-background'),
          'table-row-hover': withOpacity('--color-table-hover-background'),
        },
      },
      gradientColorStops: {
        skin: {
          hue: withOpacity('--color-fill'),
        },
      },
      borderColor: {
        skin: {
          'table': withOpacity('--color-table-border'),
          'table-row': withOpacity('--color-table-row-border'),
          'active-section': withOpacity('--color-border-active-section'),
          'disabled-section': withOpacity('--color-border-disabled-section'),
        },
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
}

