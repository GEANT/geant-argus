document.body.addEventListener('htmx:afterSwap', () => {
  const selected = document.querySelector('input[name="theme"]:checked');
  if (selected?.value) {
    document.documentElement.setAttribute('data-theme', selected.value);
  }
});