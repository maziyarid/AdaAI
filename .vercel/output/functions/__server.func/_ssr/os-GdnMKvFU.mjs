import { b as require_jsx_runtime, v as Link } from "../_libs/@tanstack/react-router+[...].mjs";
import { r as Button } from "./router-IX03nS2D.mjs";
import { t as Badge } from "./badge-BctOT3LY.mjs";
import { a as OS_STATE, i as OS_GAPS, n as DELIVERABLE, o as TECHNIQUES, s as VALIDATION, t as CALCULATOR_CHILDREN } from "./os-Bfwpjn7M.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/os-GdnMKvFU.js
var import_jsx_runtime = require_jsx_runtime();
var TONE = {
	fixed_here: "ok",
	queued: "warn",
	accepted: "slate",
	blocked: "mark"
};
var LABEL = {
	fixed_here: "بسته در این جعبه ابزار",
	queued: "صف با مالک",
	accepted: "آگاهانه پذیرفته",
	blocked: "مسدود بیرونی"
};
function OsPage() {
	const counts = {
		fixed_here: OS_GAPS.filter((g) => g.disposition === "fixed_here").length,
		queued: OS_GAPS.filter((g) => g.disposition === "queued").length,
		accepted: OS_GAPS.filter((g) => g.disposition === "accepted").length,
		blocked: OS_GAPS.filter((g) => g.disposition === "blocked").length
	};
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("main", {
		className: "flex flex-col gap-10",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("header", {
				className: "max-w-2xl",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Badge, {
						tone: "ok",
						children: OS_STATE.label
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h1", {
						className: "mt-3 font-display text-3xl font-semibold sm:text-4xl",
						children: "شکاف خاموش نمی ماند."
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "mt-3 leading-7 text-ink-muted",
						children: OS_STATE.meaning
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
						className: "mt-2 text-sm text-ink-subtle",
						children: [
							"تا ",
							OS_STATE.asOf,
							". سایت زنده بازنویسی نشد."
						]
					})
				]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("section", {
				className: "grid gap-3 sm:grid-cols-2 lg:grid-cols-4",
				children: [
					["بسته اینجا", counts.fixed_here],
					["صف", counts.queued],
					["پذیرفته", counts.accepted],
					["مسدود", counts.blocked]
				].map(([k, v]) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "rounded-[20px] bg-paper-elevated p-4 shadow-[var(--shadow-border)]",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "font-display text-2xl font-semibold",
						children: v
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "mt-1 text-xs text-ink-muted",
						children: k
					})]
				}, k))
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
				className: "font-display text-2xl font-semibold",
				children: "رجیستر شکاف"
			}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("ul", {
				className: "mt-4 flex flex-col gap-3",
				children: OS_GAPS.map((g) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("li", {
					className: "rounded-[20px] bg-paper-elevated p-4 shadow-[var(--shadow-border)]",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "flex flex-wrap items-center gap-2",
							children: [
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
									className: "font-mono text-xs text-ink-subtle",
									children: g.id
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Badge, {
									tone: TONE[g.disposition],
									children: LABEL[g.disposition]
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
									className: "text-xs text-ink-subtle",
									children: g.area
								})
							]
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
							className: "mt-2 text-sm leading-7",
							children: g.gap
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
							className: "mt-1 text-sm leading-6 text-ink-muted",
							children: g.next
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
							className: "mt-1 text-xs text-ink-subtle",
							children: g.owner
						})
					]
				}, g.id))
			})] }),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", { children: [
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
					className: "font-display text-2xl font-semibold",
					children: "اعتبارسنجی نوع صفحه"
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
					className: "mt-2 max-w-2xl text-sm leading-6 text-ink-muted",
					children: "راهنما، خدمات، ابزار، دانلود، انگلیسی، فارسی، و یک صفحه با روش دست اول. نمره واحد نیست."
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
					className: "mt-4 flex flex-col gap-3",
					children: VALIDATION.map((v) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("article", {
						className: "rounded-[20px] bg-paper-sunken/70 p-4",
						children: [
							/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
								className: "flex flex-wrap items-center gap-2",
								children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Badge, {
									tone: v.result === "pass" ? "ok" : v.result === "partial" ? "warn" : "mark",
									children: v.result
								}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
									className: "text-sm font-medium",
									children: v.requirement
								})]
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
								className: "mt-2 text-sm",
								children: v.page
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
								className: "text-xs text-ink-subtle",
								children: v.url
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
								className: "mt-2 text-sm leading-6 text-ink-muted",
								children: ["کار: ", v.task]
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
								className: "text-sm leading-6 text-ink-muted",
								children: ["اعتماد: ", v.trust]
							})
						]
					}, v.id))
				})
			] }),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
				className: "font-display text-2xl font-semibold",
				children: "سیزده بند بستن"
			}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("dl", {
				className: "mt-4 flex flex-col gap-3",
				children: [
					["شکاف ها", DELIVERABLE.gaps],
					["زیرساخت", DELIVERABLE.infrastructure],
					["تعمیر E-E-A-T", DELIVERABLE.eeat],
					["ارزش افزوده", DELIVERABLE.original],
					["UX", DELIVERABLE.ux],
					["تعامل", DELIVERABLE.interactive],
					["دسترسی", DELIVERABLE.a11y],
					["چندرسانه ای", DELIVERABLE.media],
					["اسکیما", DELIVERABLE.schema],
					["اندازه گیری هوش مصنوعی", DELIVERABLE.aiMeasure],
					["کارخانه", DELIVERABLE.factory],
					["عمدا ساخته نشد", DELIVERABLE.notDone],
					["مانع", DELIVERABLE.blockers]
				].map(([k, items]) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "rounded-[16px] bg-paper-elevated p-4 shadow-[var(--shadow-border)]",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("dt", {
						className: "text-sm font-medium",
						children: k
					}), items.map((x) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)("dd", {
						className: "mt-1 text-sm leading-7 text-ink-muted",
						children: x
					}, x))]
				}, k))
			})] }),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
				className: "font-display text-2xl font-semibold",
				children: "تکنیک تازه — هنوز بهترین عمل نیست"
			}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("ul", {
				className: "mt-4 flex flex-col gap-3",
				children: TECHNIQUES.map((t) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("li", {
					className: "rounded-[16px] bg-paper-sunken/70 p-4 text-sm leading-6",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Badge, { children: t.status }),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
							className: "mt-2 font-medium",
							children: t.name
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
							className: "text-ink-muted",
							children: t.evidence
						})
					]
				}, t.id))
			})] }),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
				className: "font-display text-2xl font-semibold",
				children: "نمونه فرزندان ماشین حساب"
			}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("ul", {
				className: "mt-4 flex flex-col gap-3",
				children: CALCULATOR_CHILDREN.map((c) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("li", {
					className: "rounded-[16px] bg-paper-elevated p-4 shadow-[var(--shadow-border)]",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
							className: "font-medium",
							children: c.title
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
							className: "mt-1 text-sm leading-6 text-ink-muted",
							children: c.note
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
							className: "mt-1 text-xs text-ink-subtle",
							children: [
								"روش ",
								c.methodologySeen,
								" · ",
								c.action
							]
						})
					]
				}, c.id))
			})] }),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "flex flex-wrap gap-3",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Link, {
					to: "/factory/intake",
					children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, { children: "دریافت تجربه دست اول" })
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Link, {
					to: "/factory/pages",
					children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
						variant: "secondary",
						children: "ممیزی صفحات"
					})
				})]
			})
		]
	});
}
//#endregion
export { OsPage as component };
