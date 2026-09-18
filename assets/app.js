"use strict";
// The catalogue is rendered in HTML; JavaScript only enhances browsing.
const search = document.querySelector("#search");
if (search) {
  const stage = document.querySelector("#stage-filter");
  const category = document.querySelector("#category-filter");
  const venue = document.querySelector("#venue-filter");
  const sort = document.querySelector("#sort");
  const list = document.querySelector("#paper-list");
  const cards = Array.from(list.querySelectorAll(".paper-card"));
  const params = new URLSearchParams(location.search);
  search.value = params.get("q") || "";
  if (Array.from(stage.options).some(o => o.value === params.get("stage"))) stage.value = params.get("stage");
  if (Array.from(category.options).some(o => o.value === params.get("category"))) category.value = params.get("category");
  if (Array.from(venue.options).some(o => o.value === params.get("venue"))) venue.value = params.get("venue");
  if (Array.from(sort.options).some(o => o.value === params.get("sort"))) sort.value = params.get("sort");
  function update() {
    const terms = search.value.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
    let visible = 0;
    cards.sort((a, b) => sort.value === "year" ? Number(b.dataset.year) - Number(a.dataset.year) : b.dataset.date.localeCompare(a.dataset.date));
    for (const card of cards) {
      card.hidden = !terms.every(term => card.dataset.search.includes(term))
        || (stage.value !== "all" && !card.dataset.stages.split(" ").includes(stage.value))
        || (category.value !== "all" && card.dataset.category !== category.value)
        || (venue.value !== "" && card.dataset.venue !== venue.value);
      if (!card.hidden) visible++;
      list.append(card);
    }
    document.querySelector("#result-count").textContent = `${visible} 篇论文`;
    document.querySelector("#empty").hidden = visible !== 0;
    const next = new URLSearchParams();
    if (search.value.trim()) next.set("q", search.value.trim());
    if (stage.value !== "all") next.set("stage", stage.value);
    if (category.value !== "all") next.set("category", category.value);
    if (venue.value !== "") next.set("venue", venue.value);
    if (sort.value !== "recent") next.set("sort", sort.value);
    try { history.replaceState(null, "", location.pathname + (next.size ? "?" + next : "") + location.hash); } catch { /* file:// remains fully usable. */ }
  }
  search.addEventListener("input", update);
  stage.addEventListener("change", update);
  category.addEventListener("change", update);
  venue.addEventListener("change", update);
  sort.addEventListener("change", update);
  document.querySelector("#reset").addEventListener("click", () => { search.value = ""; stage.value = "all"; category.value = "all"; venue.value = ""; update(); search.focus(); });
  update();
}
