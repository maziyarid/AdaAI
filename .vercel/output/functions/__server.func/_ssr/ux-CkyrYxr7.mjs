import { b as require_jsx_runtime, v as Link } from "../_libs/@tanstack/react-router+[...].mjs";
import { r as Button } from "./router-IX03nS2D.mjs";
import { t as Badge } from "./badge-BctOT3LY.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/ux-CkyrYxr7.js
var import_jsx_runtime = require_jsx_runtime();
var UX_SURFACES = [
	{
		id: "UX-CTA-INQUIRY",
		surface: "دکمه خدمات",
		bad: "شروع کنید / مشاوره رایگان",
		better: "بررسی اولیه پژوهش",
		why: "بازدیدکننده باید بفهمد بعد از کلیک چه می شود."
	},
	{
		id: "UX-CTA-TOOL",
		surface: "ابزار آزمون",
		bad: "شروع کنید",
		better: "پیشنهاد آزمون را ببینید",
		why: "خروجی درخت است نه ثبت نام."
	},
	{
		id: "UX-EMPTY-SEARCH",
		surface: "جستجوی مرکز دانش",
		bad: "نتیجه ای یافت نشد.",
		better: "این عبارت راهنمایی در مرکز دانش ندارد. مسیر خدمات یا فرم بررسی را ببینید.",
		why: "صفر نتیجه باید راه بعدی بدهد."
	},
	{
		id: "UX-404",
		surface: "صفحه پیدا نشد",
		bad: "404 Not Found",
		better: "این صفحه در کارگاه نیست. میز ویرایش، کارخانه، یا خانه را امتحان کنید.",
		why: "fa-IR؛ کار بعدی."
	},
	{
		id: "UX-FORM-ERROR",
		surface: "خطای فرم",
		bad: "مقدار نامعتبر است",
		better: "نوع مقیاس متغیر وابسته را انتخاب کنید.",
		why: "خطا فیلد را نام می برد."
	},
	{
		id: "UX-SUCCESS",
		surface: "موفقیت ارسال",
		bad: "موفق",
		better: "درخواست ثبت شد. برای بررسی اولیه فایل داده لازم نیست همین الان کامل باشد.",
		why: "بعد چه می شود."
	},
	{
		id: "UX-LOADING",
		surface: "بارگذاری",
		bad: "لطفا صبر کنید...",
		better: "پیشنهاد آزمون در حال محاسبه است.",
		why: "محتوا نه انیمیشن تنها."
	},
	{
		id: "UX-CHAT",
		surface: "چت زنده",
		bad: "پاپ اجباری، شمارش معکوس، اعلان جعلی اپراتور",
		better: "اگر هست، اختیاری و پس از اسکرول؛ خاموشی آسان",
		why: "تعامل باید کار را جلو ببرد. R-18."
	}
];
var A11Y = [
	{
		id: "A11Y-01",
		where: "Qalam پوسته",
		issue: "پیوند پرش به محتوا نبود.",
		fix: "پیوند «رفتن به محتوا» در همین نسخه.",
		status: "fixed_here"
	},
	{
		id: "A11Y-02",
		where: "Qalam خطا و 404",
		issue: "خطای چارچوب انگلیسی/زینک بود و 404 نبود.",
		fix: "404 فارسی و خطای هماهنگ با کاغذ/مرکب.",
		status: "fixed_here"
	},
	{
		id: "A11Y-03",
		where: "teznevise.ir",
		issue: "lang/dir، برچسب فرم inquiry، و alt در این بازبینی کامل تأیید نشد.",
		fix: "ممیزی دستی HTML زنده؛ هدف لمسی ≥44px؛ خطا کنار فیلد.",
		status: "queued_for_site"
	},
	{
		id: "A11Y-04",
		where: "ابزارها",
		issue: "خروجی فقط در حالت تعاملی کافی نیست.",
		fix: "جدول/فهرست خزیدنی زیر ویجت.",
		status: "fixed_here"
	},
	{
		id: "A11Y-05",
		where: "راهنماهای تزنویسه",
		issue: "اطلاعات مهم نباید فقط در تصویر منو یا هاور باشد.",
		fix: "مسیر منو و حد عددی در متن.",
		status: "queued_for_site"
	}
];
var INTERACTIVE_ASSETS = [
	{
		id: "IA-STAT",
		name: "انتخاب آزمون آماری",
		userJob: "کدام آزمون آماری را باید در نظر بگیرم؟",
		inputs: [
			"هدف تحلیل",
			"مقیاس وابسته",
			"استقلال مشاهده",
			"آمادگی مفروضات پارامتری"
		],
		outputs: [
			"آزمون نامزد",
			"مفروضات",
			"آنچه نیست",
			"گام بعدی",
			"حد"
		],
		methodology: "درخت آموزشی استاندارد آزمون های پایه (t، واریانس، همبستگی، رگرسیون، خی دو و ناپارامتری معادل). جایگزینی برای طراحی پژوهش نیست.",
		evidence: "کتاب های روش؛ نه داده داخلی تزنویسه. آستانه p یا حجم نمونه تجویز نمی شود.",
		limitations: "طرح آشیانه، اندازه گیری مکرر پیچیده، بقای، چندسطحی، و داده شمارشی پیشرفته خارج است. نرم افزار روش نیست. بازبین آمار هنوز unassigned است.",
		canonicalOwner: "https://teznevise.ir/service-statistics/",
		fallback: "جدول همان درخت در HTML زیر فرم.",
		a11y: "fieldset، label، کیبورد، بدون هاور. خروجی متن انتخاب شدنی.",
		analytics: [
			"tool_started",
			"tool_completed",
			"useful_yes",
			"useful_no"
		],
		maintenanceOwner: "C-STATS (خالی) / کارخانه تا انتصاب",
		lastVerification: "2026-09-16",
		demoPath: "/tools/stat-test",
		status: "demoed_here"
	},
	{
		id: "IA-DEFENCE",
		name: "چک لیست آمادگی دفاع",
		userJob: "قبل از دفاع چه فایل و چه آمادگی کم دارم؟",
		inputs: ["موارد پرونده، اسلاید، داده، صداقت، پرسش داور"],
		outputs: ["فهرست ناقص ها", "فایل متنی قابل ذخیره"],
		methodology: "موارد تکراری مسیر تا دفاع. دانشگاه واحد نیست.",
		evidence: "مشاهده تحریریه ناشناس — نه پرونده دانشجو.",
		limitations: "آیین نامه دانشگاه شما ممکن است موارد اضافه بخواهد.",
		canonicalOwner: "مسیر تا دفاع — مالک URL روی دامنه هنوز قفل نشده",
		fallback: "فهرست کامل بدون جاوااسکریپت در همان صفحه.",
		a11y: "چک باکس برچسب دار؛ درصد پیشرفت متنی.",
		analytics: ["checklist_toggle", "checklist_saved"],
		maintenanceOwner: "کارخانه",
		lastVerification: "2026-09-16",
		demoPath: "/tools/defence",
		status: "demoed_here"
	},
	{
		id: "IA-FEASIBILITY",
		name: "امکان سنجی موضوع",
		userJob: "آیا این موضوع پژوهش در زمان من شدنی است؟",
		inputs: [
			"دسترسی داده",
			"مهارت روش",
			"زمان تا دفاع",
			"تجهیز",
			"اخلاق"
		],
		outputs: ["پرچم خطر", "سؤال برای استاد"],
		methodology: "غربال منابع و زمان. نمره امکان ساختگی نمی دهد.",
		evidence: "منطق تصمیم آموزشی. داده پرونده نیست.",
		limitations: "بدون استاد راهنما تصمیم نهایی نیست.",
		canonicalOwner: "راهنمای انتخاب موضوع وقتی مالک روشن است",
		fallback: "پرسش های غربال در متن.",
		a11y: "فرم استاندارد.",
		analytics: ["feasibility_completed"],
		maintenanceOwner: "C-METHODS",
		lastVerification: "2026-09-16",
		demoPath: "/tools/feasibility",
		status: "demoed_here"
	},
	{
		id: "IA-QUESTIONNAIRE",
		name: "غربال پرسشنامه",
		userJob: "چه چیزی در پرسشنامه ام غلط است؟",
		inputs: [
			"سازه",
			"گویه هدایت گر",
			"مقیاس",
			"معکوس",
			"پیش آزمون",
			"ترجمه",
			"طول",
			"اخلاق"
		],
		outputs: ["پرچم ایست یا خطر", "کار بعدی"],
		methodology: "نقص های رایج طراحی مقیاس در مشاوره. نمره روایی نمی دهد.",
		evidence: "مشاهده تحریریه ناشناس.",
		limitations: "روایی سازه، تحلیل عاملی، و هنجاریابی بیرون است.",
		canonicalOwner: "راهنمای ابزار اندازه گیری وقتی مالک روشن است",
		fallback: "همان هشت پرسش در جدول.",
		a11y: "radiogroup برچسب دار.",
		analytics: [
			"questionnaire_completed",
			"useful_yes",
			"useful_no"
		],
		maintenanceOwner: "C-METHODS",
		lastVerification: "2026-09-16",
		demoPath: "/tools/questionnaire",
		status: "demoed_here"
	}
];
var FEEDBACK_EVENTS = [
	{
		id: "useful_yes",
		meaning: "صفحه یا ابزار کار را جلو برد",
		source: "PRODUCT_UX"
	},
	{
		id: "useful_no",
		meaning: "کار حل نشد",
		source: "PRODUCT_UX"
	},
	{
		id: "reason_unclear",
		meaning: "زبان یا گام مبهم بود",
		source: "PRODUCT_UX"
	},
	{
		id: "reason_wrong_test",
		meaning: "پیشنهاد آزمون نامربوط بود",
		source: "PRODUCT_UX"
	},
	{
		id: "reason_need_human",
		meaning: "به مشاور انسان نیاز است",
		source: "PRODUCT_UX"
	},
	{
		id: "tool_completed",
		meaning: "خروجی دیده شد",
		source: "PRODUCT_UX"
	},
	{
		id: "form_abandoned",
		meaning: "inquiry نیمه رها شد",
		source: "GA4"
	}
];
var EXPERIENCE_NOTES = [
	{
		id: "XP-01",
		kind: "FIRST_PARTY_OBSERVATION",
		topic: "نیت تماس",
		observation: "خانه زنده 2026-09-16 به /inquiry/ می رود. ممیزی قبلی /contact/ و /contact-us/ را همپوشان دیده بود. باید زنده 200 بودن قدیمی ها چک شود.",
		cannotPromoteTo: "قانون 301 بدون سر وضعیت.",
		factory: "O-01 با وضعیت NEEDS_LIVE_CHECK.",
		date: "2026-09-16"
	},
	{
		id: "XP-02",
		kind: "FIRST_PARTY_OBSERVATION",
		topic: "نویسنده نمایان",
		observation: "نمونه مرکز دانش (فصل سوم، شکاف، EFA) نویسنده، بازبین، و منبع خارجی ندارد.",
		cannotPromoteTo: "قانون «همه صفحات باید نویسنده داشته باشند» بدون فرد واقعی.",
		factory: "رجیستری نقش خالی نگه داشته شد. نام جعلی نگذارید.",
		date: "2026-09-16"
	},
	{
		id: "XP-03",
		kind: "EDITORIAL_INTERPRETATION",
		topic: "ارزش افزوده خدمات آمار",
		observation: "/service-statistics/ از خانه و thesis برای how قوی تر است: مفروضات، اندازه اثر، حد دستکاری.",
		cannotPromoteTo: "این که همه خدمات کامل اند.",
		factory: "الگوی how برای thesis/proposal.",
		date: "2026-09-16"
	},
	{
		id: "XP-04",
		kind: "ANECDOTE",
		topic: "تازه سازی دسته ای",
		observation: "تاریخ های بلاگ در یک باند کوتاه شهریور ۱۴۰۵ جمع شده اند.",
		cannotPromoteTo: "اثبات تئاتر تاریخ. ممکن است نشر واقعی دسته ای باشد.",
		factory: "اگر GSC افت بعد از دستکاری تاریخ نشان داد، C-DATES. تا آن موقع مشاهده.",
		date: "2026-09-16"
	},
	{
		id: "XP-05",
		kind: "FIRST_PARTY_EXPERIMENT",
		topic: "EX-01 تا EX-03",
		observation: "آزمایش ها هنوز روی سایت وایید نشده اند. فرضیه اند.",
		cannotPromoteTo: "نتیجه بازنویسی 5.45 جایگاه شهرام.",
		factory: "صف آزمایش دست نخورده.",
		date: "2026-09-16"
	},
	{
		id: "XP-06",
		kind: "FIRST_PARTY_OBSERVATION",
		topic: "تماس زنده",
		observation: "/contact-us/ تلفن، ایمیل، واتساپ و ساعات دارد. /inquiry/ فرم است. باز کردن /contact/ همان عنوان تماس را نشان داد — همزاد محتمل. خانه هنوز CTA را به inquiry می برد.",
		cannotPromoteTo: "یک مالک تماس برای هر دو کار. روش تماس و فرم دو نیت اند اگر محتوا فرق دارد.",
		factory: "A-17. O-01 به 301 همزاد محدود شود نه حذف /contact-us/.",
		date: "2026-09-16"
	},
	{
		id: "XP-07",
		kind: "FIRST_PARTY_OBSERVATION",
		topic: "مزرعه ماشین حساب",
		observation: "هاب بیش از هجده فرزند دارد. حجم نمونه کوکران روش، فرض، و حد طرح پیچیده دارد. این الگو است نه مجوز تولید قالب تازه.",
		cannotPromoteTo: "همه ماشین حساب ها باکیفیت اند. یا باید ماشین حساب بیشتر بسازیم.",
		factory: "A-16. ارزش افزوده = روش مرئی. فرزند بدون how صف EVIDENCE_REFRESH.",
		date: "2026-09-16"
	},
	{
		id: "XP-08",
		kind: "FIRST_PARTY_OBSERVATION",
		topic: "حریم",
		observation: "/privacy-policy/ عنوان سیاست دارد اما متن در این بازبینی استخراج نشد.",
		cannotPromoteTo: "نبود کامل. ممکن است متن پشت اسکریپت باشد — هنوز برای انسان کنار فرم کافی نیست.",
		factory: "POL-PRIVACY exists_weak. A-18.",
		date: "2026-09-16"
	}
];
var PERFORMANCE_RULES = [
	"LCP، INP، CLS را برای قابلیت استفاده ببینید نه برای نمره کامل.",
	"ویجت تصمیم نباید LCP را با اسکریپت سنگین خراب کند.",
	"اطلاعات مهم در HTML اول باشد.",
	"فرم inquiry خطای ارسال را گم نکند."
];
var MULTIMEDIA_GAPS = [
	{
		url: "https://teznevise.ir/service-statistics/",
		opportunity: "نمودار درخت آزمون با متن جایگزین و همان داده در جدول.",
		not: "ویدئوی استوک «تحلیلگر در لپ تاپ»."
	},
	{
		url: "https://teznevise.ir/efa-payan-namayeh-rahnegah-gambe-gam/",
		opportunity: "اسکرین منوی SPSS با alt مسیر دقیق.",
		not: "اینفوگرافیک تزئینی بدون عدد."
	},
	{
		url: "https://teznevise.ir/thesis/",
		opportunity: "نمودار مسیر همکاری مرحله ای.",
		not: "ویدئوی فروش بدون رونوشت."
	}
];
function UxPage() {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("main", {
		className: "flex flex-col gap-10",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("header", {
				className: "max-w-2xl",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Badge, {
						tone: "slate",
						children: "تجربه · دسترسی · ابزار"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h1", {
						className: "mt-3 font-display text-3xl font-semibold sm:text-4xl",
						children: "زبان رابط هم قلم است."
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "mt-3 leading-7 text-ink-muted",
						children: "دکمه باید کار را بگوید. ویجت فقط اگر تصمیمی را جلو ببرد. دسترسی بخشی از سودمندی است نه تزئین."
					})
				]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
				className: "font-display text-2xl font-semibold",
				children: "زبان سطوح"
			}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: "mt-4 flex flex-col gap-3",
				children: UX_SURFACES.map((u) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("article", {
					className: "grid gap-3 rounded-[20px] bg-paper-elevated p-4 shadow-[var(--shadow-border)] md:grid-cols-2",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "text-xs text-ink-subtle",
						children: u.surface
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "mt-1 text-sm text-mark",
						children: u.bad
					})] }), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "text-sm",
						children: u.better
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "mt-1 text-xs leading-6 text-ink-muted",
						children: u.why
					})] })]
				}, u.id))
			})] }),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "flex flex-wrap items-end justify-between gap-3",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
					className: "font-display text-2xl font-semibold",
					children: "ابزارهای تصمیم"
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "flex gap-2",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Link, {
							to: "/tools/stat-test",
							children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
								size: "sm",
								children: "انتخاب آزمون"
							})
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Link, {
							to: "/tools/feasibility",
							children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
								size: "sm",
								variant: "secondary",
								children: "امکان سنجی"
							})
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Link, {
							to: "/tools/questionnaire",
							children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
								size: "sm",
								variant: "secondary",
								children: "پرسشنامه"
							})
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Link, {
							to: "/tools/defence",
							children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
								size: "sm",
								variant: "secondary",
								children: "آمادگی دفاع"
							})
						})
					]
				})]
			}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: "mt-4 flex flex-col gap-3",
				children: INTERACTIVE_ASSETS.map((a) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("article", {
					className: "rounded-[24px] bg-paper-elevated p-5 shadow-[var(--shadow-border)]",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "flex flex-wrap gap-2",
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
								className: "font-mono text-xs text-ink-subtle",
								children: a.id
							}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Badge, { children: a.status })]
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h3", {
							className: "mt-2 font-display text-lg font-semibold",
							children: a.name
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
							className: "mt-1 text-sm leading-7",
							children: a.userJob
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
							className: "mt-2 text-sm leading-6 text-ink-muted",
							children: ["حد: ", a.limitations]
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
							className: "mt-1 text-sm text-ink-subtle",
							children: ["مالک کانونی: ", a.canonicalOwner]
						})
					]
				}, a.id))
			})] }),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
				className: "font-display text-2xl font-semibold",
				children: "دسترسی"
			}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("ul", {
				className: "mt-4 flex flex-col gap-3",
				children: A11Y.map((a) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("li", {
					className: "rounded-[16px] bg-paper-sunken/70 p-4 text-sm leading-6",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Badge, {
							tone: a.status === "fixed_here" ? "ok" : "warn",
							children: a.status
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
							className: "mt-2 font-medium",
							children: a.where
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
							className: "text-ink-muted",
							children: a.issue
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
							className: "text-ink-muted",
							children: a.fix
						})
					]
				}, a.id))
			})] }),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", { children: [
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
					className: "font-display text-2xl font-semibold",
					children: "تجربه دست اول"
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
					className: "mt-2 max-w-2xl text-sm leading-6 text-ink-muted",
					children: "حکایت یک پرونده قانون نمی شود. داده خصوصی دانشجو اینجا نیست."
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
					className: "mt-4 flex flex-col gap-3",
					children: EXPERIENCE_NOTES.map((x) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("article", {
						className: "rounded-[20px] bg-paper-elevated p-4 shadow-[var(--shadow-border)]",
						children: [
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Badge, { children: x.kind }),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h3", {
								className: "mt-2 font-medium",
								children: x.topic
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
								className: "mt-1 text-sm leading-7 text-ink-muted",
								children: x.observation
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
								className: "mt-2 text-xs text-ink-subtle",
								children: ["به این ارتقا ندهید: ", x.cannotPromoteTo]
							})
						]
					}, x.id))
				})
			] }),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
				className: "font-display text-2xl font-semibold",
				children: "بازخورد محصول"
			}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("ul", {
				className: "mt-3 flex flex-col gap-2 text-sm leading-6 text-ink-muted",
				children: FEEDBACK_EVENTS.map((e) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("li", { children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
						className: "font-mono text-xs",
						children: e.id
					}),
					" — ",
					e.meaning,
					" (",
					e.source,
					")"
				] }, e.id))
			})] }),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", { children: [
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
					className: "font-display text-2xl font-semibold",
					children: "عملکرد و رسانه"
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("ul", {
					className: "mt-3 flex flex-col gap-2 text-sm leading-6",
					children: PERFORMANCE_RULES.map((r) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)("li", {
						className: "rounded-[12px] bg-paper-sunken/70 px-4 py-3",
						children: r
					}, r))
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
					className: "mt-4 flex flex-col gap-3",
					children: MULTIMEDIA_GAPS.map((m) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("article", {
						className: "rounded-[16px] bg-paper-elevated p-4 text-sm leading-6 shadow-[var(--shadow-border)]",
						children: [
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
								className: "text-ink-subtle",
								children: m.url
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
								className: "mt-1",
								children: m.opportunity
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
								className: "text-ink-muted",
								children: ["نه: ", m.not]
							})
						]
					}, m.url))
				})
			] })
		]
	});
}
//#endregion
export { UxPage as component };
