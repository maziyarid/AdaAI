import { o as __toESM } from "../_runtime.mjs";
import { B as require_react, b as require_jsx_runtime } from "../_libs/@tanstack/react-router+[...].mjs";
import { i as cn } from "./router-IX03nS2D.mjs";
import { t as Badge } from "./badge-BctOT3LY.mjs";
import { n as FINDINGS } from "./findings-agLrY6r0.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/corpus-D6S89Dmz.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
var STANCE = {
	DO: {
		label: "انجام دهید",
		tone: "ok"
	},
	DONT: {
		label: "نکنید",
		tone: "mark"
	},
	DEPENDS: {
		label: "مشروط",
		tone: "warn"
	},
	TEST: {
		label: "آزمایش",
		tone: "slate"
	}
};
var CURRENCY = {
	CURRENT: "جاری",
	CURRENT_BUT_CONTEXTUAL: "جاری مشروط",
	NEEDS_REVALIDATION: "نیاز به بازآزمایی",
	HISTORICAL_ONLY: "فقط تاریخی",
	SUPERSEDED: "باطل شده"
};
function CorpusPage() {
	const [q, setQ] = (0, import_react.useState)("");
	const [stance, setStance] = (0, import_react.useState)("ALL");
	const [topic, setTopic] = (0, import_react.useState)("ALL");
	const topics = (0, import_react.useMemo)(() => Array.from(new Set(FINDINGS.map((f) => f.topic))), []);
	const items = (0, import_react.useMemo)(() => {
		const needle = q.trim().toLowerCase();
		return FINDINGS.filter((f) => {
			if (stance !== "ALL" && f.stance !== stance) return false;
			if (topic !== "ALL" && f.topic !== topic) return false;
			if (!needle) return true;
			return [
				f.id,
				f.topic,
				f.subtopic,
				f.normalised,
				f.observation,
				f.factory,
				f.source,
				f.author
			].join(" ").toLowerCase().includes(needle);
		});
	}, [
		q,
		stance,
		topic
	]);
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("main", {
		className: "flex flex-col gap-8",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("header", {
				className: "max-w-2xl",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h1", {
					className: "font-display text-3xl font-semibold sm:text-4xl",
					children: "پیکره میدانی سئو"
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
					className: "mt-3 leading-7 text-ink-muted",
					children: "نقل ساخت یافته، نه بازنشر کانال. نثر منبع کپی نمی شود. اعتماد بر اساس سند است نه شهرت گوینده."
				})]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "flex flex-col gap-3",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("label", {
						className: "sr-only",
						htmlFor: "corpus-search",
						children: "جستجوی پیکره"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("input", {
						id: "corpus-search",
						value: q,
						onChange: (e) => setQ(e.target.value),
						placeholder: "جستجو: ایندکس، تازه سازی، برخورد نیت، رپورتاژ…",
						className: "h-12 rounded-[14px] border-0 bg-paper-elevated px-4 text-sm shadow-[var(--shadow-border)] outline-none focus:shadow-[var(--shadow-border-hover)]"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
						className: "flex gap-2 overflow-x-auto pb-1",
						children: [
							"ALL",
							"DO",
							"DONT",
							"DEPENDS",
							"TEST"
						].map((s) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
							type: "button",
							onClick: () => setStance(s),
							className: cn("h-11 shrink-0 rounded-full px-4 text-sm", stance === s ? "bg-slate text-slate-fg" : "bg-paper-elevated text-ink-muted shadow-[var(--shadow-border)]"),
							children: s === "ALL" ? "همه موضع ها" : STANCE[s].label
						}, s))
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "flex gap-2 overflow-x-auto pb-1",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
							type: "button",
							onClick: () => setTopic("ALL"),
							className: cn("h-11 shrink-0 rounded-full px-4 text-sm", topic === "ALL" ? "bg-slate text-slate-fg" : "bg-paper-elevated text-ink-muted shadow-[var(--shadow-border)]"),
							children: "همه موضوع ها"
						}), topics.map((t) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
							type: "button",
							onClick: () => setTopic(t),
							className: cn("h-11 shrink-0 rounded-full px-4 text-sm", topic === t ? "bg-slate text-slate-fg" : "bg-paper-elevated text-ink-muted shadow-[var(--shadow-border)]"),
							children: t
						}, t))]
					})
				]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
				className: "text-sm text-ink-subtle",
				children: [items.length, " یافته"]
			}),
			items.length === 0 ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "rounded-[20px] bg-paper-sunken/70 p-5 text-sm leading-7 text-ink-muted",
				children: "چیزی با این صافی پیدا نشد. موضوع یا موضع را عوض کنید."
			}) : null,
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: "flex flex-col gap-4",
				children: items.map((f) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("article", {
					className: "rounded-[24px] bg-paper-elevated p-5 shadow-[var(--shadow-border)]",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "flex flex-wrap items-center gap-2",
							children: [
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
									className: "font-mono text-xs text-ink-subtle",
									children: f.id
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Badge, {
									tone: STANCE[f.stance].tone,
									children: STANCE[f.stance].label
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Badge, { children: CURRENCY[f.currency] }),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Badge, {
									tone: "slate",
									children: f.confidence
								})
							]
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("h2", {
							className: "mt-3 font-display text-xl font-semibold",
							children: [
								f.topic,
								" · ",
								f.subtopic
							]
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
							className: "mt-2 leading-7",
							children: f.normalised
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
							className: "mt-3 text-sm leading-7 text-ink-muted",
							children: f.observation
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("dl", {
							className: "mt-4 grid gap-2 text-sm sm:grid-cols-2",
							children: [
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Row, {
									k: "شرط",
									v: f.conditions
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Row, {
									k: "کارخانه",
									v: f.factory
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Row, {
									k: "ریسک",
									v: f.risk
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Row, {
									k: "منبع",
									v: `${f.source} · ${f.date}`
								})
							]
						}),
						f.url ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)("a", {
							href: f.url,
							className: "mt-3 inline-block text-sm text-slate hover:underline",
							target: "_blank",
							rel: "noreferrer",
							children: "سند منبع"
						}) : null
					]
				}, f.id))
			})
		]
	});
}
function Row({ k, v }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("dt", {
		className: "text-xs text-ink-subtle",
		children: k
	}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("dd", {
		className: "mt-0.5 leading-6 text-ink-muted",
		children: v
	})] });
}
//#endregion
export { CorpusPage as component };
