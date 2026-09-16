import { o as __toESM } from "../_runtime.mjs";
import { B as require_react, b as require_jsx_runtime } from "../_libs/@tanstack/react-router+[...].mjs";
import { r as Button } from "./router-IX03nS2D.mjs";
import { t as Badge } from "./badge-BctOT3LY.mjs";
import { t as UsefulFeedback } from "./useful-feedback-BJucm6TT.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/stat-test-DZ3zcOOc.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
var GOALS = [
	{
		id: "compare2",
		label: "مقایسه میانگین یا توزیع دو گروه جدا"
	},
	{
		id: "compareK",
		label: "مقایسه سه گروه یا بیشتر"
	},
	{
		id: "paired",
		label: "دو اندازه از همان واحد (قبل/بعد)"
	},
	{
		id: "association",
		label: "ارتباط دو متغیر پیوسته یا رتبه ای"
	},
	{
		id: "prediction",
		label: "پیش بینی یک متغیر از روی چند پیش بین"
	},
	{
		id: "categorical",
		label: "ارتباط دو متغیر رده ای"
	},
	{
		id: "unsure",
		label: "هنوز سؤال پژوهش به این شکل درنیامده"
	}
];
var SCALES = [
	{
		id: "continuous",
		label: "وابسته پیوسته (نمره، زمان، مقدار)"
	},
	{
		id: "ordinal",
		label: "رتبه ای (لیکرت بدون توجیه فاصله)"
	},
	{
		id: "binary",
		label: "دو حالتی"
	},
	{
		id: "count",
		label: "شمارشی"
	}
];
var INDEPENDENCE = [
	{
		id: "independent",
		label: "هر مشاهده یک واحد جدا است"
	},
	{
		id: "paired",
		label: "تکرار روی همان واحد یا جفت همسان"
	},
	{
		id: "unknown",
		label: "نمی دانم"
	}
];
var PARAMETRIC = [
	{
		id: "ok",
		label: "مفروضات پارامتری محتمل است یا قابل بررسی است"
	},
	{
		id: "no",
		label: "نقض جدی نرمال یا واریانس، یا مقیاس رتبه ای سخت"
	},
	{
		id: "unknown",
		label: "هنوز داده ندیده ام"
	}
];
var TREE_ROWS = [
	[
		"دو گروه مستقل، وابسته پیوسته، پارامتری",
		"آزمون t مستقل",
		"نرمال بودن مانده، همگنی واریانس، استقلال"
	],
	[
		"دو گروه مستقل، رتبه ای یا نقض پارامتری",
		"من ویتنی",
		"استقلال؛ توزیع مشابه شکل اگر میانه تفسیر می شود"
	],
	[
		"قبل و بعد روی همان واحد",
		"t زوجی یا ویلکاکسون",
		"وابستگی جفت؛ تفاوت ها برای t"
	],
	[
		"سه گروه یا بیشتر مستقل، پارامتری",
		"ANOVA یک راهه سپس مقایسه برنامه ریزی شده",
		"نرمال مانده، همگنی، استقلال؛ آزمون تعقیبی بی برنامه نه"
	],
	[
		"سه گروه، رتبه ای یا نقض",
		"کروسکال والیس",
		"استقلال"
	],
	[
		"دو پیوسته، ارتباط",
		"پیرسون یا اسپیرمن",
		"خطی بودن برای پیرسون؛ علیت از همبستگی درنمی آید"
	],
	[
		"پیش بینی پیوسته",
		"رگرسیون خطی (شروع)",
		"مانده، هم خطی، مشخص بودن مدل"
	],
	[
		"دو رده ای",
		"خی دو یا فیشر",
		"فراوانی مورد انتظار؛ طرح نمونه"
	],
	[
		"شمارشی",
		"این درخت کافی نیست",
		"پواسون / دوجمله ای منفی نیاز طراحی جدا دارد"
	]
];
function advise(input) {
	if (!input.goal) return null;
	if (input.goal === "unsure") return {
		candidates: "هنوز آزمون انتخاب نکنید.",
		assumptions: "اول سؤال، واحد تحلیل، و طرح. نرم افزار روش نیست.",
		notThis: "گشتن منوی SPSS برای پیدا کردن آزمون.",
		next: "سؤال را یک جمله کنید: چه را در چه واحدی با چه مقایسه ای می خواهید بدانید.",
		hedge: "این غربال آموزشی است نه نسخه تحلیل."
	};
	if (input.goal === "categorical") return {
		candidates: "آزمون خی دو استقلال یا دقیق فیشر اگر سلول کم است.",
		assumptions: "نمونه گیری مشخص؛ فراوانی مورد انتظار خیلی کوچک نباشد.",
		notThis: "تفسیر درصد ستون بدون طرح. علیت.",
		next: "جدول توافقی و اندازه اثر (مثلاً V کرامر) را با p تنها گزارش نکنید.",
		hedge: "اگر طرح پیچیده یا جفت رده ای است، این درخت کوتاه است."
	};
	if (input.goal === "prediction") return {
		candidates: "شروع با رگرسیون خطی اگر وابسته پیوسته است؛ لجستیک اگر دو حالتی است.",
		assumptions: "مانده، مشخص بودن مدل، حجم نسبت به پیش بین ها، نبود نشت داده.",
		notThis: "وارد کردن همه متغیرها چون در پرسشنامه بودند.",
		next: "مدل را از نظریه بسازید. اندازه اثر و بازه را گزارش کنید.",
		hedge: "مدل چندسطحی و بقا خارج از این ابزار است."
	};
	if (input.goal === "association") return {
		candidates: input.scale === "ordinal" || input.parametric === "no" ? "همبستگی اسپیرمن (رتبه)." : "همبستگی پیرسون اگر هر دو پیوسته و رابطه خطی است؛ وگرنه اسپیرمن.",
		assumptions: "استقلال جفت ها. پیرسون: خطی بودن و مانده معقول.",
		notThis: "همبستگی یعنی علیت. حذف پرت فقط برای بزرگ شدن r.",
		next: "نمودار پراکنش را قبل از عدد ببینید.",
		hedge: "اندازه اثر r است نه فقط معنی داری."
	};
	if (input.goal === "paired" || input.independence === "paired") return {
		candidates: input.parametric === "no" || input.scale === "ordinal" ? "آزمون رتبه علامت دار ویلکاکسون." : "آزمون t زوجی اگر تفاوت ها تقریباً نرمال اند؛ وگرنه ویلکاکسون.",
		assumptions: "جفت واقعی (همان واحد). استقلال بین جفت ها.",
		notThis: "t مستقل روی قبل و بعد.",
		next: "تفاوت میانگین یا میانه و بازه را گزارش کنید نه فقط p.",
		hedge: "اندازه گیری مکرر بیش از دو زمان = مدل جدا."
	};
	if (input.goal === "compareK") return {
		candidates: input.parametric === "no" || input.scale === "ordinal" ? "کروسکال والیس." : "ANOVA یک راهه اگر مفروضات برقرار است.",
		assumptions: "استقلال گروه ها. ANOVA: مانده و همگنی واریانس.",
		notThis: "چندین t دو به دو بدون برنامه.",
		next: "مقایسه های از پیش نوشته. اندازه اثر کلی و ساده.",
		hedge: "طرح عاملی یا کوواریانس خارج است."
	};
	if (input.goal === "compare2") {
		if (input.independence === "unknown") return {
			candidates: "اول استقلال را روشن کنید. اگر جفت است مسیر زوجی؛ اگر دو نمونه جدا است مسیر t مستقل.",
			assumptions: "واحد تحلیل باید مشخص باشد.",
			notThis: "فشردن t مستقل پیش فرض.",
			next: "از استاد یا کدبوک بپرسید هر سطر کیست.",
			hedge: "این ابزار حدس نمی زند."
		};
		if (input.scale === "count") return {
			candidates: "t روی شمار خام معمولاً نامناسب است. مدل شمارشی را جدا طراحی کنید.",
			assumptions: "پراکندگی، صفر زیاد، زمان در معرض.",
			notThis: "نرمال فرض کردن شمار.",
			next: "با مشاور آمار طرح را بگویید. این غربال کافی نیست.",
			hedge: "خروجی قطعی نیست."
		};
		if (input.scale === "binary") return {
			candidates: "مقایسه نسبت ها (خی دو یا دقیق فیشر؛ یا رگرسیون لجستیک اگر پیش بین دارید).",
			assumptions: "استقلال. فراوانی مورد انتظار.",
			notThis: "t روی صفر و یک بدون توجیه.",
			next: "اندازه اثر نسبت یا نسبت بخت با بازه.",
			hedge: "خوشه و طرح پیچیده خارج است."
		};
		return {
			candidates: input.parametric === "no" || input.scale === "ordinal" ? "من ویتنی." : "آزمون t مستقل اگر مفروضات قابل دفاع است؛ وگرنه من ویتنی.",
			assumptions: "استقلال دو گروه. t: نرمال مانده یا حجم کافی؛ همگنی یا اصلاح.",
			notThis: "حذف موردها تا p ستاره بگیرد.",
			next: "اندازه اثر (d یا معادل رتبه) و بازه. در SPSS: Analyze → Compare Means برای t.",
			hedge: "همسان سازی و کوواریانس جدا است. این پیشنهاد شروع است."
		};
	}
	return null;
}
function StatTestPage() {
	const [input, setInput] = (0, import_react.useState)({
		goal: "",
		scale: "",
		independence: "",
		parametric: ""
	});
	const [submitted, setSubmitted] = (0, import_react.useState)(false);
	const result = (0, import_react.useMemo)(() => submitted ? advise(input) : null, [submitted, input]);
	const missing = !input.goal;
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("main", {
		className: "flex flex-col gap-10",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("header", {
				className: "max-w-2xl",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Badge, {
						tone: "slate",
						children: "ابزار تصمیم · نه تحلیل نهایی"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h1", {
						className: "mt-3 font-display text-3xl font-semibold sm:text-4xl",
						children: "کدام آزمون آماری را باید در نظر بگیرم؟"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "mt-3 leading-7 text-ink-muted",
						children: "این غربال آموزشی است. جای طرح پژوهش، حجم نمونه، و تفسیر استاد را نمی گیرد. نرم افزار روش نیست. بازبین آمار هنوز منصوب نشده است."
					})
				]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("form", {
				className: "flex flex-col gap-8",
				onSubmit: (e) => {
					e.preventDefault();
					setSubmitted(true);
				},
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Fieldset, {
						legend: "هدف تحلیل چیست؟",
						children: GOALS.map((g) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Radio, {
							name: "goal",
							checked: input.goal === g.id,
							onChange: () => {
								setInput((s) => ({
									...s,
									goal: g.id
								}));
								setSubmitted(false);
							},
							label: g.label
						}, g.id))
					}),
					input.goal && input.goal !== "unsure" && input.goal !== "categorical" && input.goal !== "prediction" ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Fieldset, {
						legend: "مقیاس متغیر وابسته",
						children: SCALES.map((g) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Radio, {
							name: "scale",
							checked: input.scale === g.id,
							onChange: () => {
								setInput((s) => ({
									...s,
									scale: g.id
								}));
								setSubmitted(false);
							},
							label: g.label
						}, g.id))
					}) : null,
					input.goal === "compare2" || input.goal === "compareK" ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Fieldset, {
						legend: "آیا مشاهده ها مستقل اند؟",
						children: INDEPENDENCE.map((g) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Radio, {
							name: "independence",
							checked: input.independence === g.id,
							onChange: () => {
								setInput((s) => ({
									...s,
									independence: g.id
								}));
								setSubmitted(false);
							},
							label: g.label
						}, g.id))
					}) : null,
					input.goal && input.goal !== "unsure" && input.goal !== "categorical" ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Fieldset, {
						legend: "مفروضات پارامتری",
						children: PARAMETRIC.map((g) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Radio, {
							name: "parametric",
							checked: input.parametric === g.id,
							onChange: () => {
								setInput((s) => ({
									...s,
									parametric: g.id
								}));
								setSubmitted(false);
							},
							label: g.label
						}, g.id))
					}) : null,
					submitted && missing ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "text-sm text-mark",
						role: "alert",
						children: "هدف تحلیل را انتخاب کنید."
					}) : null,
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", { children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
						type: "submit",
						children: "پیشنهاد آزمون را ببینید"
					}) })
				]
			}),
			result ? /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", {
				className: "rounded-[24px] bg-paper-elevated p-5 shadow-[var(--shadow-border)]",
				"aria-live": "polite",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
					className: "font-display text-xl font-semibold",
					children: "پیشنهاد غربال"
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("dl", {
					className: "mt-4 flex flex-col gap-3 text-sm leading-7",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("dt", {
							className: "text-xs text-ink-subtle",
							children: "نامزد"
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("dd", { children: result.candidates })] }),
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("dt", {
							className: "text-xs text-ink-subtle",
							children: "مفروضات"
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("dd", {
							className: "text-ink-muted",
							children: result.assumptions
						})] }),
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("dt", {
							className: "text-xs text-ink-subtle",
							children: "این کار را نکنید"
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("dd", {
							className: "text-ink-muted",
							children: result.notThis
						})] }),
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("dt", {
							className: "text-xs text-ink-subtle",
							children: "گام بعدی"
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("dd", { children: result.next })] }),
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("dt", {
							className: "text-xs text-ink-subtle",
							children: "حد"
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("dd", {
							className: "text-ink-muted",
							children: result.hedge
						})] })
					]
				})]
			}) : null,
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)(UsefulFeedback, { page: "/tools/stat-test" }),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", { children: [
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
					className: "font-display text-2xl font-semibold",
					children: "همان درخت، بدون فرم"
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
					className: "mt-2 max-w-2xl text-sm leading-6 text-ink-muted",
					children: "اگر اسکریپت خاموش باشد این جدول کافی است. آستانه جادویی تجویز نمی شود."
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
					className: "mt-4 overflow-x-auto",
					children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("table", {
						className: "w-full min-w-[36rem] border-separate border-spacing-0 text-sm",
						children: [
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("caption", {
								className: "mb-3 text-start text-ink-subtle",
								children: "غربال آزمون های پایه"
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("thead", { children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("tr", { children: [
								"وضعیت",
								"نامزد",
								"فرض"
							].map((h) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)("th", {
								className: "border-b border-rule px-3 py-2 text-start font-medium",
								children: h
							}, h)) }) }),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("tbody", { children: TREE_ROWS.map((row) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)("tr", { children: row.map((cell) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)("td", {
								className: "border-b border-rule/70 px-3 py-2 align-top leading-6 text-ink-muted",
								children: cell
							}, cell)) }, row[0])) })
						]
					})
				})
			] })
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
		className: "flex min-h-11 cursor-pointer items-center gap-3 rounded-[12px] px-2 hover:bg-paper-sunken/80",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("input", {
			type: "radio",
			name,
			checked,
			onChange,
			className: "size-4 accent-slate"
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
			className: "text-sm leading-6",
			children: label
		})]
	});
}
//#endregion
export { StatTestPage as component };
