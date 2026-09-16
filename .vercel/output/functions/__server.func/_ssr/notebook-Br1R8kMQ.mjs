import { b as require_jsx_runtime } from "../_libs/@tanstack/react-router+[...].mjs";
import { f as TREES, o as LIBRARY, s as NOTEBOOK } from "./ops-DvnC5rvY.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/notebook-Br1R8kMQ.js
var import_jsx_runtime = require_jsx_runtime();
function NotebookPage() {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("main", {
		className: "flex flex-col gap-10",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("header", {
				className: "max-w-2xl",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h1", {
					className: "font-display text-3xl font-semibold sm:text-4xl",
					children: "دفتر تجربه"
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
					className: "mt-3 leading-7 text-ink-muted",
					children: "مرتب بر اساس مسئله، نه کانال. هر موضوع چهار خانه دارد: انجام دهید، نکنید، مشروط، آزمایش."
				})]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: "flex flex-col gap-8",
				children: NOTEBOOK.map((block) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("article", {
					className: "rounded-[24px] bg-paper-elevated p-5 shadow-[var(--shadow-border)] sm:p-6",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
						className: "font-display text-2xl font-semibold",
						children: block.topic
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "mt-5 grid gap-4 md:grid-cols-2",
						children: [
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Col, {
								title: "انجام دهید",
								items: block.do,
								tone: "ok"
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Col, {
								title: "نکنید",
								items: block.dont,
								tone: "mark"
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Col, {
								title: "مشروط",
								items: block.depends,
								tone: "warn"
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Col, {
								title: "آزمایش",
								items: block.test,
								tone: "slate"
							})
						]
					})]
				}, block.topic))
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
				className: "font-display text-2xl font-semibold",
				children: "درخت تصمیم"
			}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				className: "mt-4 grid gap-4",
				children: TREES.map((t) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("article", {
					className: "rounded-[20px] bg-paper-sunken/70 p-5",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h3", {
						className: "font-display text-lg font-semibold",
						children: t.title
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("ol", {
						className: "mt-3 flex flex-col gap-2",
						children: t.steps.map((s, i) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("li", {
							className: "flex gap-3 text-sm leading-6",
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
								className: "font-mono text-xs text-ink-subtle",
								children: String(i + 1).padStart(2, "0")
							}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", { children: s })]
						}, s))
					})]
				}, t.id))
			})] }),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", { children: [
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
					className: "font-display text-2xl font-semibold",
					children: "ورود کتابخانه پژوهش"
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
					className: "mt-2 max-w-2xl text-sm leading-7 text-ink-muted",
					children: "فقط سنتز قابل استفاده مجدد. پست تلگرام خام اینجا نیست. وضعیت باطل شده حذف نمی شود."
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("ul", {
					className: "mt-4 flex flex-col gap-3",
					children: LIBRARY.map((x) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("li", {
						className: "rounded-[20px] bg-paper-elevated p-4 shadow-[var(--shadow-border)]",
						children: [
							/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
								className: "font-mono text-xs text-ink-subtle",
								children: [
									x.id,
									" · ",
									x.status,
									" · ",
									x.evidenceKind
								]
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
								className: "mt-2 font-medium",
								children: x.topic
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
								className: "mt-1 text-sm leading-6 text-ink-muted",
								children: x.claim
							})
						]
					}, x.id))
				})
			] })
		]
	});
}
function Col({ title, items, tone }) {
	const border = {
		ok: "border-ok/25",
		mark: "border-mark/25",
		warn: "border-warn/30",
		slate: "border-rule"
	}[tone];
	if (!items.length) return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: `rounded-[16px] border ${border} p-4`,
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
			className: "text-xs text-ink-subtle",
			children: title
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
			className: "mt-2 text-sm text-ink-subtle",
			children: "خالی — هنوز شاهد تکراری نداریم."
		})]
	});
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: `rounded-[16px] border ${border} p-4`,
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
			className: "text-xs text-ink-subtle",
			children: title
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("ul", {
			className: "mt-2 flex flex-col gap-2",
			children: items.map((x) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)("li", {
				className: "text-sm leading-6",
				children: x
			}, x))
		})]
	});
}
//#endregion
export { NotebookPage as component };
