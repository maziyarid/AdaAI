import { o as __toESM } from "../_runtime.mjs";
import { B as require_react, b as require_jsx_runtime } from "../_libs/@tanstack/react-router+[...].mjs";
import { i as cn } from "./router-IX03nS2D.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/useful-feedback-BJucm6TT.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
var REASONS = [
	{
		id: "unclear",
		label: "گام یا زبان مبهم بود"
	},
	{
		id: "wrong",
		label: "پیشنهاد به کارم نمی آمد"
	},
	{
		id: "need_human",
		label: "به مشاور انسان نیاز دارم"
	}
];
function UsefulFeedback({ page }) {
	const [choice, setChoice] = (0, import_react.useState)(null);
	const [reason, setReason] = (0, import_react.useState)(null);
	function save(next, why) {
		setChoice(next);
		if (why) setReason(why);
		try {
			const key = "qalam-product-ux";
			const prev = JSON.parse(localStorage.getItem(key) || "[]");
			prev.push({
				page,
				useful: next,
				reason: why ?? null,
				at: (/* @__PURE__ */ new Date()).toISOString()
			});
			localStorage.setItem(key, JSON.stringify(prev.slice(-50)));
		} catch {}
	}
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", {
		className: "rounded-[20px] bg-paper-sunken/70 p-5",
		"aria-label": "بازخورد سودمندی",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "text-sm font-medium",
				children: "آیا این صفحه کارتان را جلو برد؟"
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "mt-1 text-xs leading-6 text-ink-subtle",
				children: "سیگنال محصول است نه فاکتور رتبه گوگل."
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "mt-3 flex flex-wrap gap-2",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
					type: "button",
					className: cn("h-11 rounded-full px-4 text-sm", choice === "yes" ? "bg-ok text-paper-elevated" : "bg-paper-elevated text-ink-muted shadow-[var(--shadow-border)]"),
					onClick: () => save("yes"),
					children: "بله"
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
					type: "button",
					className: cn("h-11 rounded-full px-4 text-sm", choice === "no" ? "bg-mark text-paper-elevated" : "bg-paper-elevated text-ink-muted shadow-[var(--shadow-border)]"),
					onClick: () => save("no"),
					children: "خیر"
				})]
			}),
			choice === "no" ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: "mt-3 flex flex-col gap-2",
				children: REASONS.map((r) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
					type: "button",
					className: cn("h-11 rounded-[12px] px-3 text-start text-sm", reason === r.id ? "bg-slate text-slate-fg" : "bg-paper-elevated text-ink-muted"),
					onClick: () => save("no", r.id),
					children: r.label
				}, r.id))
			}) : null,
			choice ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "mt-3 text-sm text-ink-muted",
				children: "ثبت شد. برای بهبود محصول می ماند."
			}) : null
		]
	});
}
//#endregion
export { UsefulFeedback as t };
