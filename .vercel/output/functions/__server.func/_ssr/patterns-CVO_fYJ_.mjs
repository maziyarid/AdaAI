import { b as require_jsx_runtime } from "../_libs/@tanstack/react-router+[...].mjs";
import { a as PATTERNS } from "./content-k1oeWTfI.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/patterns-CVO_fYJ_.js
var import_jsx_runtime = require_jsx_runtime();
function PatternsPage() {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("main", {
		className: "flex flex-col gap-8",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("header", {
			className: "max-w-2xl",
			children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h1", {
				className: "font-display text-3xl font-semibold sm:text-4xl",
				children: "بانک حرکت"
			}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "mt-3 leading-7 text-ink-muted",
				children: "مکانیک را یاد بگیرید، امضا را نه. مثال ها نو ساخته شده اند و موضوعشان پژوهش است، نه فلسفه کافه."
			})]
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
			className: "flex flex-col gap-5",
			children: PATTERNS.map((p) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("article", {
				className: "overflow-hidden rounded-[24px] bg-paper-elevated shadow-[var(--shadow-border)]",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
						className: "border-b border-rule px-5 py-3 sm:px-6",
						children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
							className: "text-sm font-medium text-slate",
							children: [
								p.id,
								" · ",
								p.move
							]
						})
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "grid gap-0 md:grid-cols-2",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Block, {
							label: "پیش",
							text: p.before,
							weak: true
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Block, {
							label: "پس",
							text: p.after
						})]
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "px-5 py-3 text-sm leading-6 text-ink-muted sm:px-6",
						children: p.why
					})
				]
			}, p.id))
		})]
	});
}
function Block({ label, text, weak }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: weak ? "bg-paper-sunken/50 px-5 py-4 sm:px-6" : "px-5 py-4 sm:px-6",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
			className: "text-xs text-ink-subtle",
			children: label
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
			className: "mt-2 leading-7",
			children: text
		})]
	});
}
//#endregion
export { PatternsPage as component };
