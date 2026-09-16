import { b as require_jsx_runtime, v as Link } from "../_libs/@tanstack/react-router+[...].mjs";
import { r as Button } from "./router-IX03nS2D.mjs";
import { o as REGISTERS } from "./content-k1oeWTfI.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/registers-DYdJTRHF.js
var import_jsx_runtime = require_jsx_runtime();
function RegistersPage() {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("main", {
		className: "flex flex-col gap-8",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("header", {
			className: "max-w-2xl",
			children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h1", {
				className: "font-display text-3xl font-semibold sm:text-4xl",
				children: "نقشه رجیستر"
			}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "mt-3 leading-7 text-ink-muted",
				children: "سیزده پیش تنظیم عملی. قاطی کردن مجله و کافه، یا دری و فارسی ایران، در یک بند از قوی ترین نشانه های ناهماهنگی است. عامل باید همه را بداند و یکی را انتخاب کند."
			})]
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
			className: "grid gap-4",
			children: REGISTERS.map((r) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("article", {
				className: "rounded-[24px] bg-paper-elevated p-5 shadow-[var(--shadow-border)] sm:p-6",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "flex flex-wrap items-start justify-between gap-3",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
							className: "font-display text-2xl font-semibold",
							children: r.name
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
							className: "mt-1 text-sm text-ink-muted",
							children: r.use
						})] }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Link, {
							to: "/desk",
							search: { register: r.id },
							children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
								size: "sm",
								variant: "secondary",
								children: "سنجش در این رجیستر"
							})
						})]
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("dl", {
						className: "mt-5 grid gap-3 sm:grid-cols-2",
						children: [
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Item, {
								k: "رسمیت",
								v: r.formality
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Item, {
								k: "ضمیر",
								v: r.you
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Item, {
								k: "پرسش",
								v: r.questions
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Item, {
								k: "تمثیل",
								v: r.analogy
							})
						]
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
						className: "mt-4 text-sm text-mark",
						children: ["پرهیز: ", r.avoid]
					})
				]
			}, r.id))
		})]
	});
}
function Item({ k, v }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "rounded-[12px] bg-paper-sunken/70 px-3 py-2",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("dt", {
			className: "text-xs text-ink-subtle",
			children: k
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("dd", {
			className: "mt-0.5 text-sm leading-6",
			children: v
		})]
	});
}
//#endregion
export { RegistersPage as component };
