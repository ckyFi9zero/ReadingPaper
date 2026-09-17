"use strict";
// Add library navigation without changing the authored reader's style or scripts.
const bar = document.createElement("div");
bar.setAttribute("role", "navigation");
bar.setAttribute("aria-label", "论文库导航");
bar.style.cssText = "display:flex;flex-wrap:wrap;gap:12px 24px;padding:12px 24px;border-bottom:1px solid #dce4dc;background:#fff;font:14px/1.8 system-ui,sans-serif;";
for (const [href, label] of [["../index.html", "← 论文库"], ["index.html", "论文总览"], ["first-pass.html", "第一遍初读"], ["deep-read.html", "第二遍深读"], ["code.html", "代码阅读"]]) {
  const a = document.createElement("a"); a.href = href; a.textContent = label;
  a.style.cssText = "color:#176758;text-decoration:none;padding:2px 0";
  if (href === location.pathname.split("/").pop()) { a.setAttribute("aria-current", "page"); a.style.fontWeight = "700"; }
  bar.append(a);
}
document.body.prepend(bar);
