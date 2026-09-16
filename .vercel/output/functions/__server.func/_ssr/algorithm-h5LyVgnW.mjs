import { b as require_jsx_runtime, v as Link } from "../_libs/@tanstack/react-router+[...].mjs";
import { r as Button } from "./router-IX03nS2D.mjs";
import { t as ALGORITHM } from "./content-k1oeWTfI.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/algorithm-h5LyVgnW.js
var import_jsx_runtime = require_jsx_runtime();
function AlgorithmPage() {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("main", {
		className: "flex flex-col gap-8",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("header", {
			className: "max-w-2xl",
			children: [
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h1", {
					className: "font-display text-3xl font-semibold sm:text-4xl",
					children: "الگوریتم نگارش"
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
					className: "mt-3 leading-7 text-ink-muted",
					children: "هفده گام قابل اجرا. اگر مصنوع اجازه ندهد، گام را رد کنید — نه اینکه قالبی روی فکر بگذارید."
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Link, {
					to: "/desk",
					className: "mt-4 inline-block",
					children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, { children: "روی یک پیش نویس پیاده کنید" })
				})
			]
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("ol", {
			className: "grid gap-3 sm:grid-cols-2",
			children: ALGORITHM.map((step) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("li", {
				className: "rounded-[20px] bg-paper-elevated p-4 shadow-[var(--shadow-border)]",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "font-mono text-xs tabular-nums text-ink-subtle",
						children: String(step.n).padStart(2, "0")
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
						className: "mt-1 font-display text-lg font-semibold",
						children: step.t
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "mt-2 text-sm leading-7 text-ink-muted",
						children: step.d
					})
				]
			}, step.n))
		})]
	});
}
//#endregion
export { AlgorithmPage as component };
