module.exports = {
    content: [
{{ tailwind_content }}
    ],
    theme: {
        extend: {},
    },
    daisyui: {
        themes: ["light", "dark", "cupcake"],
      },
    plugins: [
        require('@tailwindcss/forms'),
        require('@tailwindcss/typography'),
        require('@tailwindcss/aspect-ratio'),
        require('daisyui')
    ],
}
