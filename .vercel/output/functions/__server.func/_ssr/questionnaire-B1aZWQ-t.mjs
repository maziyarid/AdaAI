import { o as __toESM } from "../_runtime.mjs";
import { B as require_react, b as require_jsx_runtime } from "../_libs/@tanstack/react-router+[...].mjs";
import { r as Button } from "./router-IX03nS2D.mjs";
import { t as Badge } from "./badge-BctOT3LY.mjs";
import { t as UsefulFeedback } from "./useful-feedback-BJucm6TT.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/questionnaire-B1aZWQ-t.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
var Q_ITEMS = [
	{
		id: "construct",
		prompt: "سازه هر مقیاس در یک جمله تعریف شده است؟",
		hint: "اگر ندانید چه چیزی اندازه گرفته می شود، پایایی عدد تزئینی است."
	},
	{
		id: "leading",
		prompt: "گویه هدایت گر یا دو سؤالی ندارید؟",
		hint: "«آیا شما هم مثل بقیه موافق اید که…» داده نمی سازد."
	},
	{
		id: "scale",
		prompt: "نوع مقیاس (اسمی، رتبه ای، فاصله ای ادعایی) نوشته شده است؟",
		hint: "لیکرت را بی توجیه فاصله ای نگیرید. آزمون بعداً روی همین ادعا سوار می شود."
	},
	{
		id: "reverse",
		prompt: "گویه معکوس اگر هست، نمره گذاری اش نوشته شده است؟",
		hint: "معکوس فراموش شده آلفا را خراب می کند و کسی نمی فهمد چرا."
	},
	{
		id: "pretest",
		prompt: "پیش آزمون روی چند نفر شبیه نمونه انجام شده است؟",
		hint: "ابهام گویه قبل از نمونه اصلی ارزان تر درست می شود."
	},
	{
		id: "translation",
		prompt: "اگر ترجمه است، مسیر ترجمه و تطبیق فرهنگی ثبت شده است؟",
		hint: "کپی زیرنویس ابزار خارجی روایی نمی آورد."
	},
	{
		id: "length",
		prompt: "زمان پر کردن برای پاسخ دهنده واقع بینانه است؟",
		hint: "پرسشنامه خسته کننده داده گمشده و پاسخ تصادفی می سازد."
	},
	{
		id: "ethics",
		prompt: "رضایت، محرمانگی، و حق انصراف در مقدمه آمده است؟",
		hint: "حتی مقیاس کوتاه بدون این مقدمه در بسیاری از دانشگاه ها نمی گذرد."
	}
];
function screenQuestionnaire(answers) {
	if (Q_ITEMS.some((i) => !answers[i.id])) return null;
	const flags = [];
	const fail = (id, stop, title, detail) => {
		const a = answers[id];
		if (a === "no") flags.push({
			id,
			level: stop ? "stop" : "risk",
			title,
			detail
		});
		else if (a === "unsure") flags.push({
			id,
			level: "risk",
			title: `معلوم نیست: ${title}`,
			detail
		});
	};
	fail("construct", true, "سازه تعریف نشده", "اول بگویید هر مقیاس چه چیزی را می سنجد. وگرنه تحلیل تفسیر ندارد.");
	fail("leading", false, "گویه هدایت گر یا دو سؤالی", "گویه را دو تکه کنید و بار ارزشی را بردارید.");
	fail("scale", true, "نوع مقیاس نوشته نشده", "قبل از انتخاب آزمون، مقیاس را قفل کنید. درخت آزمون روی این ادعا سوار است.");
	fail("reverse", false, "نمره گذاری معکوس مبهم", "در کدبوک ستون معکوس را مشخص کنید.");
	fail("pretest", false, "پیش آزمون نیست", "پنج تا ده نفر شبیه نمونه، با یادداشت ابهام، کافی است برای غربال.");
	fail("translation", false, "ترجمه بدون مسیر", "حداقل ترجمه مستقیم و بازبینی فرد دوم. ادعای روایی ابزار اصلی به فارسی منتقل نمی شود.");
	fail("length", false, "طول واقع بینانه نیست", "زمان را با ساعت اندازه بگیرید نه با حدس.");
	fail("ethics", true, "مقدمه اخلاق نیست", "رضایت و محرمانگی را قبل از گویه اول بگذارید.");
	if (flags.length === 0) flags.push({
		id: "ok",
		level: "ok",
		title: "این غربال مانع آشکار نشان نداد",
		detail: "جای روایی سازه، تحلیل عاملی، و نظر استاد را نمی گیرد. فقط نقص های رایج را کم می کند."
	});
	return flags;
}
var Q_FALLBACK = Q_ITEMS.map((i) => [i.prompt, i.hint]);
function QuestionnairePage() {
	const [answers, setAnswers] = (0, import_react.useState)(Object.fromEntries(Q_ITEMS.map((i) => [i.id, ""])));
	const [submitted, setSubmitted] = (0, import_react.useState)(false);
	const flags = (0, import_react.useMemo)(() => submitted ? screenQuestionnaire(answers) : null, [submitted, answers]);
	const missing = submitted && !flags;
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("main", {
		className: "flex flex-col gap-10",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("header", {
				className: "max-w-2xl",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Badge, {
						tone: "slate",
						children: "غربال · نه نمره روایی"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h1", {
						className: "mt-3 font-display text-3xl font-semibold sm:text-4xl",
						children: "چه چیزی در پرسشنامه ام غلط است؟"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "mt-3 leading-7 text-ink-muted",
						children: "نقص های رایج قبل از نمونه اصلی. روایی سازه، تحلیل عاملی، و هنجاریابی را نمی فروشد."
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
					Q_ITEMS.map((item) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("fieldset", {
						className: "rounded-[20px] bg-paper-elevated p-4 shadow-[var(--shadow-border)]",
						children: [
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("legend", {
								className: "px-1 text-sm font-medium",
								children: item.prompt
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
								className: "mt-2 text-xs leading-6 text-ink-subtle",
								children: item.hint
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
								className: "mt-3 flex flex-wrap gap-2",
								children: [
									["yes", "بله"],
									["no", "خیر"],
									["unsure", "نمی دانم"]
								].map(([id, label]) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("label", {
									className: "flex h-11 cursor-pointer items-center gap-2 rounded-full bg-paper-sunken px-4 text-sm",
									children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("input", {
										type: "radio",
										name: item.id,
										checked: answers[item.id] === id,
										onChange: () => {
											setAnswers((s) => ({
												...s,
												[item.id]: id
											}));
											setSubmitted(false);
										},
										className: "accent-slate"
									}), label]
								}, id))
							})
						]
					}, item.id)),
					missing ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "text-sm text-mark",
						role: "alert",
						children: "به هر هشت پرسش پاسخ دهید."
					}) : null,
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", { children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
						type: "submit",
						children: "غربال را ببینید"
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
						})
					]
				}, f.id))]
			}) : null,
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)(UsefulFeedback, { page: "/tools/questionnaire" }),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
				className: "font-display text-2xl font-semibold",
				children: "همان پرسش ها، بدون فرم"
			}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: "mt-4 overflow-x-auto",
				children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("table", {
					className: "w-full min-w-[32rem] border-separate border-spacing-0 text-sm",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("caption", {
							className: "mb-3 text-start text-ink-subtle",
							children: "غربال پرسشنامه"
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("thead", { children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)("tr", { children: ["پرسش", "چرا"].map((h) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)("th", {
							className: "border-b border-rule px-3 py-2 text-start font-medium",
							children: h
						}, h)) }) }),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("tbody", { children: Q_FALLBACK.map((row) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)("tr", { children: row.map((cell) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)("td", {
							className: "border-b border-rule/70 px-3 py-2 align-top leading-6 text-ink-muted",
							children: cell
						}, cell)) }, row[0])) })
					]
				})
			})] })
		]
	});
}
//#endregion
export { QuestionnairePage as component };
