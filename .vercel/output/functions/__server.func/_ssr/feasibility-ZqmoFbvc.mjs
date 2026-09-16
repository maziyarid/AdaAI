import { o as __toESM } from "../_runtime.mjs";
import { B as require_react, b as require_jsx_runtime } from "../_libs/@tanstack/react-router+[...].mjs";
import { r as Button } from "./router-IX03nS2D.mjs";
import { t as Badge } from "./badge-BctOT3LY.mjs";
import { t as UsefulFeedback } from "./useful-feedback-BJucm6TT.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/feasibility-ZqmoFbvc.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
var DATA_OPTS = [
	{
		id: "have",
		label: "داده یا منبع در دست است"
	},
	{
		id: "access",
		label: "دسترسی محتمل است اما هنوز نگرفته ام"
	},
	{
		id: "unknown",
		label: "نمی دانم داده اصلا وجود دارد"
	},
	{
		id: "none",
		label: "می دانم داده در زمان من در دسترس نیست"
	}
];
var METHOD_OPTS = [
	{
		id: "known",
		label: "روش را بلدم یا مشاور روش دارم"
	},
	{
		id: "learnable",
		label: "روش تازه است اما در زمان باقی مانده آموختنی است"
	},
	{
		id: "new",
		label: "روش برایم ناشناخته است و استاد هم تخصصش را ندارد"
	}
];
var TIME_OPTS = [
	{
		id: "gt12",
		label: "بیش از دوازده ماه تا دفاع"
	},
	{
		id: "6to12",
		label: "شش تا دوازده ماه"
	},
	{
		id: "lt6",
		label: "کمتر از شش ماه"
	}
];
var ETHICS_OPTS = [
	{
		id: "none_needed",
		label: "داده عمومی یا بدون آزمودنی انسان"
	},
	{
		id: "in_progress",
		label: "مسیر اخلاق شروع شده"
	},
	{
		id: "not_started",
		label: "آزمودنی انسان یا داده حساس است و هنوز اقدام نشده"
	}
];
var SUPER_OPTS = [
	{
		id: "aligned",
		label: "استاد با سؤال و روش همراه است"
	},
	{
		id: "unclear",
		label: "هنوز معلوم نیست استاد این طرح را می پذیرد"
	},
	{
		id: "opposed",
		label: "استاد صریحا مخالف یا خارج از تخصص اعلام کرده"
	}
];
var FALLBACK_ROWS = [
	[
		"داده در دسترس نیست",
		"موضوع را عوض کنید یا منبع جایگزین تعریف کنید",
		"بدون داده طرح شدنی نیست"
	],
	[
		"روش ناشناخته برای دانشجو و استاد",
		"روش را ساده کنید یا مشاور روش بیاورید",
		"نرم افزار روش نمی سازد"
	],
	[
		"کمتر از شش ماه و روش تازه",
		"دامنه را ببرید",
		"زمان با یادگیری روش جمع نمی شود مگر طرح کوچک شود"
	],
	[
		"اخلاق شروع نشده و آزمودنی انسان",
		"قبل از گردآوری اقدام کنید",
		"داده بدون مجوز ممکن است غیرقابل استفاده شود"
	],
	[
		"استاد مخالف",
		"طرح را با استاد بازنویسی کنید",
		"این غربال جای جلسه استاد را نمی گیرد"
	]
];
function screenFeasibility(input) {
	if (!input.data || !input.method || !input.time || !input.ethics || !input.supervisor) return null;
	const flags = [];
	if (input.data === "none") flags.push({
		level: "stop",
		title: "منبع داده در زمان شما نیست",
		detail: "موضوع با این منبع در این پنجره زمانی شدنی نیست.",
		ask: "اگر منبع جایگزین ندارید، سؤال را عوض کنید نه اینکه امیدوار بمانید."
	});
	else if (input.data === "unknown") flags.push({
		level: "stop",
		title: "وجود داده معلوم نیست",
		detail: "تا وجود منبع ثابت نشود طرح را قفل نکنید.",
		ask: "از استاد بپرسید: این داده کجاست، مال کیست، و تا کی در دسترس است؟"
	});
	else if (input.data === "access") flags.push({
		level: "risk",
		title: "دسترسی هنوز گرفته نشده",
		detail: "وعده دسترسی داده نیست.",
		ask: "نامه، مجوز، یا مالک داده را قبل از تصویب نهایی بگیرید."
	});
	else flags.push({
		level: "ok",
		title: "منبع داده ادعا شده در دست است",
		detail: "باز هم کدبوک و کیفیت را جدا چک کنید.",
		ask: "یک نمونه واقعی از رکورد را به استاد نشان دهید."
	});
	if (input.method === "new") flags.push({
		level: "stop",
		title: "روش برای شما و استاد ناشناخته است",
		detail: "این ترکیب معمولا در یک پایان نامه آموزشی نمی گنجد.",
		ask: "روش را به چیزی که در گروه هست برگردانید، یا مشاور روش با مسئولیت روشن بیاورید."
	});
	else if (input.method === "learnable" && input.time === "lt6") flags.push({
		level: "risk",
		title: "روش تازه در پنجره کوتاه",
		detail: "یادگیری روش و اجرای پژوهش در کمتر از شش ماه با هم جا نمی شود مگر دامنه خیلی کوچک شود.",
		ask: "کدام بخش طرح حذف شود تا روش آموختنی بماند؟"
	});
	else if (input.method === "learnable") flags.push({
		level: "risk",
		title: "روش آموختنی است نه آماده",
		detail: "زمان یادگیری باید در جدول پروژه بیاید.",
		ask: "منبع آموزش روش و کسی که خروجی را بازبینی می کند کیست؟"
	});
	if (input.ethics === "not_started") flags.push({
		level: "stop",
		title: "اخلاق شروع نشده",
		detail: "گردآوری از آزمودنی یا داده حساس بدون مسیر اخلاق، طرح را شکننده می کند.",
		ask: "آیین نامه دانشگاه شما برای این داده چیست و فرم از کی باید برود؟"
	});
	else if (input.ethics === "in_progress" && input.time === "lt6") flags.push({
		level: "risk",
		title: "اخلاق در جریان و زمان کم",
		detail: "تأخیر کمیته روی دفاع اثر می گذارد.",
		ask: "تاریخ جلسه کمیته را بپرسید و برنامه بدون داده حساس داشته باشید."
	});
	if (input.supervisor === "opposed") flags.push({
		level: "stop",
		title: "استاد همراه نیست",
		detail: "غربال ما جای مخالفت استاد را عوض نمی کند.",
		ask: "طرح بدیل داخل تخصص استاد چیست؟"
	});
	else if (input.supervisor === "unclear") flags.push({
		level: "risk",
		title: "همراهی استاد معلوم نیست",
		detail: "قبل از سرمایه گذاری روی ابزار و داده یک جلسه کوتاه کافی است.",
		ask: "یک صفحه سؤال، داده، روش، و حد را ببرید نه یک پروپوزال کامل."
	});
	if (input.time === "lt6" && input.data !== "have") flags.push({
		level: "risk",
		title: "زمان کم و داده هنوز کامل نیست",
		detail: "پنجره دفاع با گردآوری تازه معمولا نمی خواند.",
		ask: "آیا داده آرشیوی داخل همان سؤال هست؟"
	});
	if (!flags.some((f) => f.level === "stop") && !flags.some((f) => f.level === "risk")) flags.push({
		level: "ok",
		title: "این غربال پرچم ایست نداده",
		detail: "یعنی مانع آشکار در این پنج سؤال نیست. شدنی بودن نهایی با استاد و آیین نامه است.",
		ask: "حالا دامنه را یک جمله کنید و فایل داده را نشان دهید."
	});
	return flags;
}
function FeasibilityPage() {
	const [input, setInput] = (0, import_react.useState)({
		data: "",
		method: "",
		time: "",
		ethics: "",
		supervisor: ""
	});
	const [submitted, setSubmitted] = (0, import_react.useState)(false);
	const flags = (0, import_react.useMemo)(() => submitted ? screenFeasibility(input) : null, [submitted, input]);
	const missing = submitted && !flags;
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("main", {
		className: "flex flex-col gap-10",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("header", {
				className: "max-w-2xl",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Badge, {
						tone: "slate",
						children: "غربال · نه نمره امکان"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h1", {
						className: "mt-3 font-display text-3xl font-semibold sm:text-4xl",
						children: "آیا این موضوع در زمان من شدنی است؟"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "mt-3 leading-7 text-ink-muted",
						children: "پرچم خطر است. درصد امکان ساخته نمی شود. جای استاد راهنما و آیین نامه دانشگاه را نمی گیرد."
					})
				]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("form", {
				className: "flex flex-col gap-6",
				onSubmit: (e) => {
					e.preventDefault();
					setSubmitted(true);
				},
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Fieldset, {
						legend: "دسترسی به داده",
						children: DATA_OPTS.map((g) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Radio, {
							name: "data",
							checked: input.data === g.id,
							onChange: () => {
								setInput((s) => ({
									...s,
									data: g.id
								}));
								setSubmitted(false);
							},
							label: g.label
						}, g.id))
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Fieldset, {
						legend: "مهارت روش",
						children: METHOD_OPTS.map((g) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Radio, {
							name: "method",
							checked: input.method === g.id,
							onChange: () => {
								setInput((s) => ({
									...s,
									method: g.id
								}));
								setSubmitted(false);
							},
							label: g.label
						}, g.id))
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Fieldset, {
						legend: "زمان تا دفاع",
						children: TIME_OPTS.map((g) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Radio, {
							name: "time",
							checked: input.time === g.id,
							onChange: () => {
								setInput((s) => ({
									...s,
									time: g.id
								}));
								setSubmitted(false);
							},
							label: g.label
						}, g.id))
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Fieldset, {
						legend: "اخلاق پژوهش",
						children: ETHICS_OPTS.map((g) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Radio, {
							name: "ethics",
							checked: input.ethics === g.id,
							onChange: () => {
								setInput((s) => ({
									...s,
									ethics: g.id
								}));
								setSubmitted(false);
							},
							label: g.label
						}, g.id))
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Fieldset, {
						legend: "همراهی استاد",
						children: SUPER_OPTS.map((g) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Radio, {
							name: "supervisor",
							checked: input.supervisor === g.id,
							onChange: () => {
								setInput((s) => ({
									...s,
									supervisor: g.id
								}));
								setSubmitted(false);
							},
							label: g.label
						}, g.id))
					}),
					missing ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "text-sm text-mark",
						role: "alert",
						children: "هر پنج پرسش را پاسخ دهید."
					}) : null,
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", { children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
						type: "submit",
						children: "پرچم ها را ببینید"
					}) })
				]
			}),
			flags ? /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", {
				className: "flex flex-col gap-3",
				"aria-live": "polite",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
					className: "font-display text-xl font-semibold",
					children: "نتیجه غربال"
				}), flags.map((f) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("article", {
					className: "rounded-[20px] bg-paper-elevated p-4 shadow-[var(--shadow-border)]",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Badge, {
							tone: f.level === "stop" ? "mark" : f.level === "risk" ? "warn" : "ok",
							children: f.level === "stop" ? "ایست" : f.level === "risk" ? "خطر" : "مانع آشکار نیست"
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h3", {
							className: "mt-2 font-medium",
							children: f.title
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
							className: "mt-1 text-sm leading-7 text-ink-muted",
							children: f.detail
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
							className: "mt-2 text-sm leading-7",
							children: ["از استاد بپرسید: ", f.ask]
						})
					]
				}, f.title))]
			}) : null,
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)(UsefulFeedback, { page: "/tools/feasibility" }),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
				className: "font-display text-2xl font-semibold",
				children: "همان غربال، بدون فرم"
			}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: "mt-4 overflow-x-auto",
				children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("table", {
					className: "w-full min-w-[36rem] border-separate border-spacing-0 text-sm",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("caption", {
							className: "mb-3 text-start text-ink-subtle",
							children: "پرچم های رایج امکان سنجی"
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("thead", { children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("tr", { children: [
							"وضعیت",
							"کار",
							"چرا"
						].map((h) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)("th", {
							className: "border-b border-rule px-3 py-2 text-start font-medium",
							children: h
						}, h)) }) }),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("tbody", { children: FALLBACK_ROWS.map((row) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)("tr", { children: row.map((cell) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)("td", {
							className: "border-b border-rule/70 px-3 py-2 align-top leading-6 text-ink-muted",
							children: cell
						}, cell)) }, row[0])) })
					]
				})
			})] })
		]
	});
}
function Fieldset({ legend, children }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("fieldset", {
		className: "rounded-[20px] bg-paper-elevated p-4 shadow-[var(--shadow-border)]",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("legend", {
			className: "px-1 text-sm font-medium",
			children: legend
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
			className: "mt-3 flex flex-col gap-2",
			children
		})]
	});
}
function Radio({ name, checked, onChange, label }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("label", {
		className: "flex min-h-11 cursor-pointer items-start gap-3 rounded-[12px] px-1 py-1 hover:bg-paper-sunken/70",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("input", {
			type: "radio",
			name,
			checked,
			onChange,
			className: "mt-1 accent-slate"
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
			className: "text-sm leading-6",
			children: label
		})]
	});
}
//#endregion
export { FeasibilityPage as component };
