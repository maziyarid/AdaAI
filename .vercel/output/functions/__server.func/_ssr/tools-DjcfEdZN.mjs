import { b as require_jsx_runtime, v as Link } from "../_libs/@tanstack/react-router+[...].mjs";
import { t as Badge } from "./badge-BctOT3LY.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/tools-DjcfEdZN.js
var import_jsx_runtime = require_jsx_runtime();
var DEMOS = [
	{
		to: "/tools/stat-test",
		name: "انتخاب آزمون آماری",
		job: "کدام آزمون را باید در نظر بگیرم؟"
	},
	{
		to: "/tools/feasibility",
		name: "امکان سنجی موضوع",
		job: "آیا این موضوع در زمان من شدنی است؟"
	},
	{
		to: "/tools/questionnaire",
		name: "غربال پرسشنامه",
		job: "چه چیزی در پرسشنامه ام غلط است؟"
	},
	{
		to: "/tools/defence",
		name: "آمادگی دفاع",
		job: "قبل از دفاع چه چیزی کم است؟"
	}
];
function ToolsHub() {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("main", {
		className: "flex flex-col gap-8",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("header", {
			className: "max-w-2xl",
			children: [
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Badge, {
					tone: "slate",
					children: "ابزار تصمیم"
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h1", {
					className: "mt-3 font-display text-3xl font-semibold sm:text-4xl",
					children: "کار را تمام کنید، ویجت نسازید."
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
					className: "mt-3 leading-7 text-ink-muted",
					children: "هر ابزار یک کار کاربر دارد، روش و حد دارد، و متن خزیدنی زیر فرم. جایگزین مشاور نیست. تا بازبین منصوب نشود نام فرد نمی گذاریم."
				})
			]
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
			className: "grid gap-3 md:grid-cols-2",
			children: DEMOS.map((a) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Link, {
				to: a.to,
				className: "rounded-[24px] bg-paper-elevated p-5 shadow-[var(--shadow-border)] transition-shadow duration-150 hover:shadow-[var(--shadow-border-hover)]",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
					className: "font-display text-xl font-semibold",
					children: a.name
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
					className: "mt-2 text-sm leading-7 text-ink-muted",
					children: a.job
				})]
			}, a.to))
		})]
	});
}
//#endregion
export { ToolsHub as component };
