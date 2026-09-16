import { o as __toESM } from "../_runtime.mjs";
import { B as require_react, b as require_jsx_runtime } from "../_libs/@tanstack/react-router+[...].mjs";
import { r as Button } from "./router-IX03nS2D.mjs";
import { t as Badge } from "./badge-BctOT3LY.mjs";
import { t as UsefulFeedback } from "./useful-feedback-BJucm6TT.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/defence-BSsElGaQ.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
var DEFENCE_SECTIONS = [
	{
		id: "files",
		title: "پرونده",
		items: [
			"نسخه نهایی فصول با شماره صفحه ثابت",
			"پروپوزال تصویب شده برای تطبیق انحراف ها",
			"فرم های اخلاق یا مجوز داده اگر لازم بوده",
			"فهرست منابع همسان با استنادهای متن"
		]
	},
	{
		id: "data",
		title: "داده و بازتولید",
		items: [
			"فایل داده خام جدا از فایل کاری",
			"کدبوک متغیرها",
			"قواعد پاکسازی نوشته شده",
			"خروجی آزمون ها قابل بازتولید در نرم افزار اعلام شده"
		]
	},
	{
		id: "slides",
		title: "اسلاید و زمان",
		items: [
			"اسلاید با زمان واقعی تمرین شده",
			"یک اسلاید روش: طرح، نمونه، آزمون، مفروضات",
			"یک اسلاید یافته بدون جدول شلوغ",
			"یک اسلاید حد و آنچه پژوهش نمی گوید"
		]
	},
	{
		id: "questions",
		title: "پرسش داور",
		items: [
			"چرا این طرح نه طرح بدیل",
			"اگر مفروضات آزمون نقض شود چه کرده اید",
			"اندازه اثر چه می گوید اگر p معنی دار نیست یا هست",
			"تعمیم به کجا بند است"
		]
	},
	{
		id: "integrity",
		title: "صداقت",
		items: [
			"نقل قول ها با صفحه",
			"همسان جویی روی نسخه دفاع",
			"سهم مشاور و نرم افزار در متن روشن است",
			"داده ساختگی در کار نیست"
		]
	}
];
function defenceText(checked) {
	const lines = [
		"چک لیست آمادگی دفاع — تزنویسه / قلم",
		"این فهرست عمومی است. آیین نامه دانشگاه شما ممکن است موارد اضافه بخواهد.",
		""
	];
	for (const section of DEFENCE_SECTIONS) {
		lines.push(`## ${section.title}`);
		section.items.forEach((item, i) => {
			const key = `${section.id}-${i}`;
			lines.push(`${checked[key] ? "[x]" : "[ ]"} ${item}`);
		});
		lines.push("");
	}
	return lines.join("\n");
}
function DefencePage() {
	const [checked, setChecked] = (0, import_react.useState)({});
	const total = DEFENCE_SECTIONS.reduce((n, s) => n + s.items.length, 0);
	const done = Object.values(checked).filter(Boolean).length;
	const text = (0, import_react.useMemo)(() => defenceText(checked), [checked]);
	function saveFile() {
		const blob = new Blob([text], { type: "text/plain;charset=utf-8" });
		const url = URL.createObjectURL(blob);
		const a = document.createElement("a");
		a.href = url;
		a.download = "defence-checklist.txt";
		a.click();
		URL.revokeObjectURL(url);
	}
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("main", {
		className: "flex flex-col gap-10",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("header", {
				className: "max-w-2xl",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Badge, {
						tone: "slate",
						children: "چک لیست · قابل ذخیره"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h1", {
						className: "mt-3 font-display text-3xl font-semibold sm:text-4xl",
						children: "قبل از دفاع چه چیزی کم است؟"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "mt-3 leading-7 text-ink-muted",
						children: "فهرست عمومی مسیر تا دفاع. آیین نامه دانشگاه شما ممکن است موارد اضافه بخواهد. داده دانشجو اینجا ذخیره نمی شود."
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
						className: "mt-2 text-sm text-ink-subtle",
						"aria-live": "polite",
						children: [
							done,
							" از ",
							total,
							" مورد علامت خورده است."
						]
					})
				]
			}),
			DEFENCE_SECTIONS.map((section) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", {
				className: "rounded-[24px] bg-paper-elevated p-5 shadow-[var(--shadow-border)]",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
					className: "font-display text-xl font-semibold",
					children: section.title
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("ul", {
					className: "mt-3 flex flex-col gap-2",
					children: section.items.map((item, i) => {
						const key = `${section.id}-${i}`;
						return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("li", { children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("label", {
							className: "flex min-h-11 cursor-pointer items-start gap-3 rounded-[12px] px-1 py-1 hover:bg-paper-sunken/70",
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("input", {
								type: "checkbox",
								className: "mt-1 size-4 accent-slate",
								checked: Boolean(checked[key]),
								onChange: (e) => setChecked((s) => ({
									...s,
									[key]: e.target.checked
								}))
							}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
								className: "text-sm leading-6",
								children: item
							})]
						}) }, key);
					})
				})]
			}, section.id)),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", { children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
				onClick: saveFile,
				children: "فهرست را ذخیره کنید"
			}) }),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)(UsefulFeedback, { page: "/tools/defence" }),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
				className: "font-display text-xl font-semibold",
				children: "نسخه متنی"
			}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("pre", {
				className: "mt-3 overflow-x-auto whitespace-pre-wrap rounded-[16px] bg-paper-sunken/70 p-4 text-sm leading-7",
				children: text
			})] })
		]
	});
}
//#endregion
export { DefencePage as component };
