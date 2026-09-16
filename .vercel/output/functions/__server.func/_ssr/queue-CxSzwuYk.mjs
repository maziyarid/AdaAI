import { b as require_jsx_runtime } from "../_libs/@tanstack/react-router+[...].mjs";
import { t as Badge } from "./badge-BctOT3LY.mjs";
import { c as OPPORTUNITIES, d as SITES, i as EXPERIMENTS, t as ACTIONS } from "./ops-DvnC5rvY.mjs";
import { t as COVERAGE } from "./findings-agLrY6r0.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/queue-CxSzwuYk.js
var import_jsx_runtime = require_jsx_runtime();
function QueuePage() {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("main", {
		className: "flex flex-col gap-10",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("header", {
				className: "max-w-2xl",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h1", {
					className: "font-display text-3xl font-semibold sm:text-4xl",
					children: "صف اقدام و آزمایش"
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
					className: "mt-3 leading-7 text-ink-muted",
					children: "هیچ آزمایش سایت وایید. همگروه محدود، متریک، و مسیر بازگشت. یافته تلگرام به خودی خود صفحه تازه نمی سازد."
				})]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
				className: "font-display text-2xl font-semibold",
				children: "اقدام ها"
			}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("ul", {
				className: "mt-4 flex flex-col gap-3",
				children: ACTIONS.map((a) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("li", {
					className: "rounded-[20px] bg-paper-elevated p-4 shadow-[var(--shadow-border)]",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "flex flex-wrap items-center gap-2",
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Badge, {
								tone: a.priority === "P0" ? "mark" : a.priority === "P1" ? "warn" : "slate",
								children: a.priority
							}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
								className: "font-mono text-xs text-ink-subtle",
								children: a.id
							})]
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
							className: "mt-2 font-medium",
							children: a.title
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
							className: "mt-1 text-sm leading-6 text-ink-muted",
							children: a.why
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
							className: "mt-2 text-xs text-ink-subtle",
							children: [
								a.owner,
								" · ",
								a.sources.join(" ")
							]
						})
					]
				}, a.id))
			})] }),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
				className: "font-display text-2xl font-semibold",
				children: "فرصت سایت"
			}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("ul", {
				className: "mt-4 flex flex-col gap-3",
				children: OPPORTUNITIES.map((o) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("li", {
					className: "rounded-[20px] bg-paper-elevated p-4 shadow-[var(--shadow-border)]",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "flex flex-wrap items-center gap-2",
							children: [
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Badge, {
									tone: o.priority === "P0" ? "mark" : o.priority === "P4" ? "ink" : "slate",
									children: o.priority
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Badge, { children: o.kind }),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
									className: "font-mono text-xs text-ink-subtle",
									children: o.id
								})
							]
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
							className: "mt-2 font-medium",
							children: o.target
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
							className: "mt-1 text-sm leading-6 text-ink-muted",
							children: o.action
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
							className: "mt-2 text-xs text-ink-subtle",
							children: [
								o.site,
								" · ",
								o.intent,
								" · ",
								o.sources.join(" ")
							]
						})
					]
				}, o.id))
			})] }),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
				className: "font-display text-2xl font-semibold",
				children: "آزمایش ها"
			}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: "mt-4 flex flex-col gap-4",
				children: EXPERIMENTS.map((e) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("article", {
					className: "rounded-[24px] bg-paper-elevated p-5 shadow-[var(--shadow-border)]",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "flex flex-wrap gap-2",
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
								className: "font-mono text-xs text-ink-subtle",
								children: e.id
							}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Badge, {
								tone: e.status === "rejected" ? "mark" : e.status === "ready_for_review" ? "ok" : "slate",
								children: e.status === "rejected" ? "رد شده" : e.status === "ready_for_review" ? "آماده بازبینی" : "صف"
							})]
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h3", {
							className: "mt-2 font-display text-lg font-semibold",
							children: e.hypothesis
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("dl", {
							className: "mt-3 grid gap-2 text-sm leading-6 sm:grid-cols-2",
							children: [
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(KV, {
									k: "محدوده",
									v: e.scope
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(KV, {
									k: "متغیر",
									v: e.variable
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(KV, {
									k: "کنترل",
									v: e.control
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(KV, {
									k: "متریک اصلی",
									v: e.primary
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(KV, {
									k: "پنجره",
									v: e.window
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(KV, {
									k: "بازگشت",
									v: e.rollback
								})
							]
						})
					]
				}, e.id))
			})] }),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
				className: "font-display text-2xl font-semibold",
				children: "نمایه و پوشش"
			}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "mt-4 grid gap-3",
				children: [SITES.map((s) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "rounded-[20px] bg-paper-sunken/70 p-4 text-sm leading-7",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
							className: "font-medium",
							children: s.domain
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
							className: "mt-1 text-ink-muted",
							children: s.notes
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("ul", {
							className: "mt-2",
							children: s.serviceOwners.map((o) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("li", { children: [
								o.intent,
								": ",
								o.url
							] }, o.url))
						})
					]
				}, s.id)), COVERAGE.sources.map((s) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "rounded-[20px] bg-paper-elevated p-4 text-sm leading-6 shadow-[var(--shadow-border)]",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
							className: "font-medium",
							children: s.id
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
							className: "text-ink-muted",
							children: [
								s.earliest ?? "—",
								" تا ",
								s.latest ?? "—",
								" · ",
								s.inspected,
								" پیام · ویدئو ",
								s.videos
							]
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
							className: "mt-1 text-ink-muted",
							children: s.inaccessible
						})
					]
				}, s.id))]
			})] })
		]
	});
}
function KV({ k, v }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("dt", {
		className: "text-xs text-ink-subtle",
		children: k
	}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("dd", {
		className: "text-ink-muted",
		children: v
	})] });
}
//#endregion
export { QueuePage as component };
