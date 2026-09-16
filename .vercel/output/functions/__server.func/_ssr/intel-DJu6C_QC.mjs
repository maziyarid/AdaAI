import { o as __toESM } from "../_runtime.mjs";
import { B as require_react, b as require_jsx_runtime, v as Link } from "../_libs/@tanstack/react-router+[...].mjs";
import { i as cn, r as Button } from "./router-IX03nS2D.mjs";
import { t as Badge } from "./badge-BctOT3LY.mjs";
import { i as PUB_FINDINGS, n as INTEL_SOURCES, r as PUB_EVENTS, t as BRIEFING } from "./intel-CApmGZAD.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/intel-DJu6C_QC.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
function IntelPage() {
	const [tier, setTier] = (0, import_react.useState)("ALL");
	const sources = (0, import_react.useMemo)(() => INTEL_SOURCES.filter((s) => tier === "ALL" ? true : s.tier === tier), [tier]);
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("main", {
		className: "flex flex-col gap-10",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("header", {
				className: "max-w-2xl",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Badge, {
						tone: "slate",
						children: "پژوهش بیرونی · ضد نویز"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h1", {
						className: "mt-3 font-display text-3xl font-semibold sm:text-4xl",
						children: "خبر صنعت قانون کارخانه نمی شود."
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "mt-3 leading-7 text-ink-muted",
						children: "منبع اولیه حاکم است. بیست بازنویسی یک رویدادند. متن کامل مقاله ذخیره نمی شود. تیتر وارد صف تولید نمی شود."
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Link, {
						to: "/factory/briefing",
						className: "mt-4 inline-block",
						children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
							variant: "secondary",
							children: "English briefing"
						})
					})
				]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", {
				className: "rounded-[24px] bg-paper-elevated p-5 shadow-[var(--shadow-border)]",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
						className: "font-display text-xl font-semibold",
						children: "خلاصه این دور"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("ul", {
						className: "mt-3 flex flex-col gap-2 text-sm leading-7",
						children: BRIEFING.fa.changed.map((x) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)("li", { children: x }, x))
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "mt-3 text-sm leading-6 text-ink-muted",
						children: BRIEFING.fa.action
					})
				]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", { children: [
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
					className: "font-display text-2xl font-semibold",
					children: "منابع"
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
					className: "mt-3 flex gap-2 overflow-x-auto pb-1",
					children: [
						"ALL",
						0,
						1,
						2,
						3
					].map((t) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
						type: "button",
						onClick: () => setTier(t),
						className: cn("h-11 shrink-0 rounded-full px-4 text-sm", tier === t ? "bg-slate text-slate-fg" : "bg-paper-elevated text-ink-muted shadow-[var(--shadow-border)]"),
						children: t === "ALL" ? "همه سطح ها" : `سطح ${t}`
					}, String(t)))
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("ul", {
					className: "mt-4 flex flex-col gap-3",
					children: sources.map((s) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("li", {
						className: "rounded-[16px] bg-paper-sunken/70 p-4 text-sm leading-6",
						children: [
							/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
								className: "flex flex-wrap gap-2",
								children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Badge, { children: ["T", s.tier] }), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
									className: "font-medium",
									children: s.name
								})]
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
								className: "mt-1 text-ink-muted",
								children: s.note
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
								className: "mt-1 text-xs text-ink-subtle",
								children: [
									"آخرین بررسی ",
									s.lastChecked,
									" · آخرین مطلب ",
									s.lastProcessedDate
								]
							})
						]
					}, s.id))
				})
			] }),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
				className: "font-display text-2xl font-semibold",
				children: "خوشه رویداد"
			}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: "mt-4 flex flex-col gap-4",
				children: PUB_EVENTS.map((e) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("article", {
					className: "rounded-[24px] bg-paper-elevated p-5 shadow-[var(--shadow-border)]",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
							className: "font-mono text-xs text-ink-subtle",
							children: e.id
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h3", {
							className: "mt-1 font-display text-lg font-semibold",
							children: e.title
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
							className: "mt-2 text-sm leading-7",
							children: e.newEvidence
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
							className: "mt-2 text-sm text-ink-muted",
							children: ["سؤال باز: ", e.openQuestions]
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("a", {
							href: e.primarySource,
							className: "mt-2 inline-block text-sm text-slate hover:underline",
							target: "_blank",
							rel: "noreferrer",
							children: "منبع اولیه"
						})
					]
				}, e.id))
			})] }),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
				className: "font-display text-2xl font-semibold",
				children: "یافته های راستی آزمایی شده"
			}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: "mt-4 flex flex-col gap-3",
				children: PUB_FINDINGS.map((f) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("article", {
					className: "rounded-[20px] bg-paper-sunken/70 p-4",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "flex flex-wrap gap-2",
							children: [
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
									className: "font-mono text-xs",
									children: f.id
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Badge, { children: f.claimClass }),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Badge, {
									tone: f.urgency === "P1" || f.urgency === "P0" ? "mark" : "ink",
									children: f.urgency
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Badge, {
									tone: "slate",
									children: f.websiteImpact
								})
							]
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
							className: "mt-2 text-sm leading-7",
							children: f.finding
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
							className: "mt-1 text-xs leading-6 text-ink-subtle",
							children: ["کارخانه: ", f.factoryImpact]
						})
					]
				}, f.id))
			})] })
		]
	});
}
//#endregion
export { IntelPage as component };
