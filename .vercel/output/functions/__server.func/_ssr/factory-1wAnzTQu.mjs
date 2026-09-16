import { b as require_jsx_runtime, v as Link } from "../_libs/@tanstack/react-router+[...].mjs";
import { r as Button } from "./router-IX03nS2D.mjs";
import { t as Badge } from "./badge-BctOT3LY.mjs";
import { a as FLOW, d as SITES, l as PRINCIPLES, n as CHANGELOG, t as ACTIONS, u as REJECTS } from "./ops-DvnC5rvY.mjs";
import { n as FINDINGS, t as COVERAGE } from "./findings-agLrY6r0.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/factory-1wAnzTQu.js
var import_jsx_runtime = require_jsx_runtime();
function FactoryHome() {
	const sh = COVERAGE.sources[0];
	const community = COVERAGE.sources[1];
	const now = FINDINGS.filter((f) => f.actionability === "now").length;
	const rejected = FINDINGS.filter((f) => f.actionability === "reject").length;
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("main", {
		className: "flex flex-col gap-10",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("header", {
				className: "max-w-2xl",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Badge, {
						tone: "slate",
						children: "حافظه سئو · لایه تصمیم"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h1", {
						className: "mt-3 font-display text-3xl font-semibold sm:text-4xl",
						children: "کارخانه محتوا تصمیم می گیرد، قلم می نویسد."
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "mt-3 leading-7 text-ink-muted",
						children: "تجربه عملی سئوی فارسی اینجا به قانون شرطی تبدیل می شود. هیچ پستی از تلگرام مستقیم مقاله نمی شود. نگارش همچنان روی قلم و کتابچه است."
					})
				]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("section", {
				className: "grid gap-3 sm:grid-cols-2 lg:grid-cols-4",
				children: [
					{
						k: "پست شهرام",
						v: String(sh.inspected)
					},
					{
						k: "یافته ساخت یافته",
						v: String(FINDINGS.length)
					},
					{
						k: "الان قابل اجرا",
						v: String(now)
					},
					{
						k: "نپذیرید",
						v: String(rejected)
					}
				].map((x) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "rounded-[20px] bg-paper-elevated p-4 shadow-[var(--shadow-border)]",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "font-display text-2xl font-semibold",
						children: x.v
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "mt-1 text-xs text-ink-muted",
						children: x.k
					})]
				}, x.k))
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", {
				className: "rounded-[24px] bg-mark/8 p-5",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
						className: "font-display text-xl font-semibold",
						children: "شکاف پوشش"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "mt-2 leading-7 text-ink-muted",
						children: community.inaccessible
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "mt-2 text-sm leading-6 text-ink-muted",
						children: "پاسخ های نقل شده در کانال شهرام به عنوان وکیل پرسش و پاسخ ثبت شده اند، نه به عنوان تاریخ کامل گروه. ویدئوهای مرادی رونوشت ندارند."
					})
				]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
				className: "font-display text-2xl font-semibold",
				children: "چرخه ورود دانش"
			}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("ol", {
				className: "mt-4 flex flex-col gap-2",
				children: FLOW.map((step, i) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("li", {
					className: "flex gap-3 rounded-[16px] bg-paper-sunken/70 px-4 py-3 text-sm leading-6",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
						className: "font-mono text-xs text-ink-subtle",
						children: String(i + 1).padStart(2, "0")
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { children: step })]
				}, step))
			})] }),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
				className: "font-display text-2xl font-semibold",
				children: "اصول جاری"
			}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("ol", {
				className: "mt-4 flex flex-col gap-2",
				children: PRINCIPLES.map((p, i) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("li", {
					className: "flex gap-3 rounded-[16px] bg-paper-sunken/70 px-4 py-3 text-sm leading-6",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
						className: "font-mono text-xs text-ink-subtle",
						children: String(i + 1).padStart(2, "0")
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { children: p })]
				}, p))
			})] }),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "flex items-end justify-between gap-3",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
					className: "font-display text-2xl font-semibold",
					children: "اقدام فوری"
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Link, {
					to: "/factory/queue",
					className: "text-sm text-slate hover:underline",
					children: "صف کامل"
				})]
			}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("ul", {
				className: "mt-4 flex flex-col gap-3",
				children: ACTIONS.filter((a) => a.priority === "P0").map((a) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("li", {
					className: "rounded-[20px] bg-paper-elevated p-4 shadow-[var(--shadow-border)]",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Badge, {
							tone: "mark",
							children: a.priority
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
							className: "mt-2 font-medium",
							children: a.title
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
							className: "mt-1 text-sm leading-6 text-ink-muted",
							children: a.why
						})
					]
				}, a.id))
			})] }),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", {
				className: "rounded-[24px] bg-paper-elevated p-5 shadow-[var(--shadow-border)]",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
					className: "font-display text-xl font-semibold",
					children: "نمایه سایت در این جعبه ابزار"
				}), SITES.map((s) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "mt-3",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
							className: "font-medium",
							children: s.domain
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
							className: "mt-1 text-sm leading-6 text-ink-muted",
							children: s.role
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
							className: "mt-2 text-sm leading-6 text-ink-muted",
							children: s.notes
						})
					]
				}, s.id))]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", { children: [
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
					className: "font-display text-2xl font-semibold",
					children: "نمونه نپذیرید"
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("ul", {
					className: "mt-4 grid gap-2 sm:grid-cols-2",
					children: REJECTS.slice(0, 6).map((r) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("li", {
						className: "rounded-[16px] bg-paper-sunken/70 px-4 py-3 text-sm leading-6",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
							className: "font-mono text-xs text-ink-subtle",
							children: r.id
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
							className: "mt-1",
							children: r.title
						})]
					}, r.id))
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
					className: "mt-3 text-sm text-ink-muted",
					children: "فهرست کامل در تعارض و صف."
				})
			] }),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
				className: "font-display text-2xl font-semibold",
				children: "لایه سودمندی"
			}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: "mt-4 grid gap-3 sm:grid-cols-2",
				children: [
					{
						to: "/factory/trust",
						t: "اعتماد",
						d: "رجیستری نقش، سیاست، ریست اسکیما. نمره E-E-A-T نیست."
					},
					{
						to: "/factory/pages",
						t: "صفحات",
						d: "ممیزی کار کاربر روی URL زنده. پیش فرض حفظ است."
					},
					{
						to: "/factory/ux",
						t: "تجربه",
						d: "زبان رابط، دسترسی، ابزار تصمیم، تجربه دست اول."
					},
					{
						to: "/factory/intel",
						t: "پژوهش",
						d: "خوشه رویداد گوگل. تیتر صنعت وارد تولید نمی شود."
					},
					{
						to: "/factory/os",
						t: "وضعیت",
						d: "شکاف ها بسته، صف، پذیرفته یا مسدودند. نمره واحد نیست."
					},
					{
						to: "/factory/intake",
						t: "تجربه دست اول",
						d: "حکایت قانون نمی شود. درگاه ارزش افزوده برای نشانی تازه."
					}
				].map((x) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Link, {
					to: x.to,
					className: "rounded-[20px] bg-paper-elevated p-4 shadow-[var(--shadow-border)] transition-shadow duration-150 hover:shadow-[var(--shadow-border-hover)]",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "font-medium",
						children: x.t
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "mt-1 text-sm leading-6 text-ink-muted",
						children: x.d
					})]
				}, x.to))
			})] }),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", {
				className: "text-sm leading-6 text-ink-subtle",
				children: [
					"آخرین تغییر کارخانه: ",
					CHANGELOG[CHANGELOG.length - 1]?.at,
					" · ",
					CHANGELOG.length,
					" بند دفتر تغییر. شیت زنده بیرون این پیش نمایش دست نخورده است؛ اینجا لایه افزودنی مدل شده."
				]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "flex flex-wrap gap-3",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Link, {
					to: "/factory/corpus",
					children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, { children: "پیکره را بگردید" })
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Link, {
					to: "/desk",
					children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
						variant: "secondary",
						children: "برگردید به میز نگارش"
					})
				})]
			})
		]
	});
}
//#endregion
export { FactoryHome as component };
