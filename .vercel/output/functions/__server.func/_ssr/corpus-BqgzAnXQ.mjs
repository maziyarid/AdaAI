import { b as require_jsx_runtime } from "../_libs/@tanstack/react-router+[...].mjs";
import { i as CORPUS } from "./content-k1oeWTfI.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/corpus-BqgzAnXQ.js
var import_jsx_runtime = require_jsx_runtime();
function CorpusPage() {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("main", {
		className: "flex flex-col gap-10",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("header", {
				className: "max-w-2xl",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h1", {
					className: "font-display text-3xl font-semibold sm:text-4xl",
					children: CORPUS.headline
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
					className: "mt-3 leading-7 text-ink-muted",
					children: "کافه فلسفه لنگر مکانیک نثر فکری معاصر ایرانی است. نقل هایدگر، فروید، ابن عربی و شکسپیر شاهد ساخت جمله نویسندگان کانال نیست. تکیه کلام هیچ مشارکت کننده ای الگو نمی شود."
				})]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("section", {
				className: "grid grid-cols-2 gap-3 sm:grid-cols-3",
				children: CORPUS.facts.map((f) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "rounded-[20px] bg-paper-elevated p-4 shadow-[var(--shadow-border)]",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "font-display text-2xl font-semibold tabular-nums",
						children: f.v
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "mt-1 text-xs leading-5 text-ink-muted",
						children: f.k
					})]
				}, f.k))
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("section", {
				className: "grid gap-4 md:grid-cols-2",
				children: CORPUS.layers.map((l) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("article", {
					className: "rounded-[20px] bg-paper-sunken/70 p-5",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
						className: "font-display text-xl font-semibold",
						children: l.t
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "mt-2 leading-7 text-ink-muted",
						children: l.d
					})]
				}, l.t))
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", {
				className: "grid gap-6 lg:grid-cols-2",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
					className: "font-display text-2xl font-semibold",
					children: "قابل انتقال"
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("ol", {
					className: "mt-4 flex flex-col gap-2",
					children: CORPUS.transferable.map((t, i) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("li", {
						className: "flex gap-3 text-sm leading-6",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
							className: "font-mono text-xs text-ink-subtle",
							children: String(i + 1).padStart(2, "0")
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { children: t })]
					}, t))
				})] }), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
					className: "font-display text-2xl font-semibold",
					children: "کپی نکنید"
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("ul", {
					className: "mt-4 flex flex-col gap-2",
					children: CORPUS.forbidden.map((t) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)("li", {
						className: "rounded-[12px] bg-mark/8 px-3 py-2 text-sm leading-6 text-mark",
						children: t
					}, t))
				})] })]
			})
		]
	});
}
//#endregion
export { CorpusPage as component };
