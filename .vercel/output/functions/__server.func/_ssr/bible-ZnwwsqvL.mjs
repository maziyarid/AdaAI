import { b as require_jsx_runtime } from "../_libs/@tanstack/react-router+[...].mjs";
import { n as BIBLE } from "./content-k1oeWTfI.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/bible-ZnwwsqvL.js
var import_jsx_runtime = require_jsx_runtime();
function BiblePage() {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("main", {
		className: "flex flex-col gap-8",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("header", {
			className: "max-w-2xl",
			children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h1", {
				className: "font-display text-3xl font-semibold sm:text-4xl",
				children: "کتابچه نگارش"
			}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "mt-3 leading-7 text-ink-muted",
				children: "استاندارد زنده برای عامل های نگارش. سبک هیچ وقت حقیقت را باطل نمی کند. نسخه کامل مهارتی در مخزن مهارت است؛ اینجا ستون فقرات اجرایی است."
			})]
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
			className: "flex flex-col gap-4",
			children: BIBLE.map((s) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("article", {
				className: "rounded-[24px] bg-paper-elevated p-5 shadow-[var(--shadow-border)] sm:p-6",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
					className: "font-display text-xl font-semibold",
					children: s.title
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
					className: "mt-3 leading-8 text-ink-muted",
					children: s.body
				})]
			}, s.id))
		})]
	});
}
//#endregion
export { BiblePage as component };
