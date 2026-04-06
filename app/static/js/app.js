// DevDash – global helpers

// Utility used by all list pages to show/hide the add form
function toggleForm(id) {
  const el = document.getElementById(id);
  if (!el) return;
  el.classList.toggle("hidden");
  // focus first input when opening
  if (!el.classList.contains("hidden")) {
    const first = el.querySelector("input[type=text], input[type=number], textarea");
    if (first) setTimeout(() => first.focus(), 50);
  }
}
