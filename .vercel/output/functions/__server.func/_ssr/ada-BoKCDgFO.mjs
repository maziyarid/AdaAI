import { o as __toESM } from "../_runtime.mjs";
import { B as require_react, b as require_jsx_runtime } from "../_libs/@tanstack/react-router+[...].mjs";
import { n as TSS_SERVER_FUNCTION, r as getServerFnById, t as createServerFn } from "./ssr.mjs";
import { i as cn, r as Button } from "./router-IX03nS2D.mjs";
import { t as Badge } from "./badge-BctOT3LY.mjs";
import { t as Textarea } from "./textarea-LLVL0RMq.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/ada-BoKCDgFO.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
var createSsrRpc = (functionId) => {
	const url = "/_serverFn/" + functionId;
	const serverFnMeta = { id: functionId };
	const fn = async (...args) => {
		return (await getServerFnById(functionId, { origin: "server" }))(...args);
	};
	return Object.assign(fn, {
		url,
		serverFnMeta,
		[TSS_SERVER_FUNCTION]: true
	});
};
var adaBootstrap = createServerFn({ method: "POST" }).validator((d) => d).handler(createSsrRpc("e2783f68d3a24b8b11a24743b9a49d642c877b4997f44988a816b0bedcd90b66"));
var adaValidateReceipt = createServerFn({ method: "POST" }).validator((d) => d).handler(createSsrRpc("83b2377a2aa25180609c41a04b4203afc5b683e0fe22459c200d6b3181941e97"));
var adaListMemory = createServerFn({ method: "POST" }).handler(createSsrRpc("bd181e364d476b0f4d1795e829dc2e3b5c4beb7d503538562c3b037e66dec2d6"));
var adaAuthorize = createServerFn({ method: "POST" }).validator((d) => d).handler(createSsrRpc("757f7404502eeea822ff82d4285fe5a444e219a785f4dbedb372674a0bd43123"));
var adaQuarantine = createServerFn({ method: "POST" }).validator((d) => d).handler(createSsrRpc("f2f2bad8ddec0d3d59607398bf0c38878b16e6c9cb2aef0234e36cc1d77bdd54"));
var AGENTS = [{
	id: "qalam-desk",
	label: "qalam-desk"
}, {
	id: "mistral-shadow",
	label: "mistral-shadow"
}];
var TASKS = [
	{
		id: "web_content",
		label: "web_content"
	},
	{
		id: "academic_content",
		label: "academic_content"
	},
	{
		id: "landing_product",
		label: "landing_product"
	},
	{
		id: "editorial",
		label: "editorial"
	}
];
function AdaPage() {
	const [agent, setAgent] = (0, import_react.useState)("qalam-desk");
	const [task, setTask] = (0, import_react.useState)("web_content");
	const [busy, setBusy] = (0, import_react.useState)(null);
	const [error, setError] = (0, import_react.useState)(null);
	const [list, setList] = (0, import_react.useState)(null);
	const [receipt, setReceipt] = (0, import_react.useState)(null);
	const [validation, setValidation] = (0, import_react.useState)(null);
	const [auth, setAuth] = (0, import_react.useState)([]);
	const [quarantineText, setQuarantineText] = (0, import_react.useState)("چطور تو سه سوت پیشینه ات را بنویسی!؟ ۱۲ راز طلایی پژوهشگران برتر 👇");
	const [quarantine, setQuarantine] = (0, import_react.useState)(null);
	async function refreshList() {
		const out = await adaListMemory();
		setList(out);
	}
	(0, import_react.useEffect)(() => {
		let cancelled = false;
		(async () => {
			setBusy("list");
			try {
				const out = await adaListMemory();
				if (!cancelled) setList(out);
			} catch (e) {
				if (!cancelled) setError(e instanceof Error ? e.message : "بارگذاری حافظه ناموفق بود.");
			} finally {
				if (!cancelled) setBusy(null);
			}
		})();
		return () => {
			cancelled = true;
		};
	}, []);
	async function onBootstrap() {
		setBusy("boot");
		setError(null);
		setValidation(null);
		setAuth([]);
		try {
			const out = await adaBootstrap({ data: {
				agent_id: agent,
				task_type: task,
				project_id: "qalam",
				site_id: "teznevise.ir"
			} });
			setReceipt(out);
			await refreshList();
		} catch (e) {
			setError(e instanceof Error ? e.message : "bootstrap ناموفق بود.");
		} finally {
			setBusy(null);
		}
	}
	async function onValidate() {
		if (!receipt) return;
		setBusy("validate");
		setError(null);
		try {
			const out = await adaValidateReceipt({ data: { receipt_id: receipt.receipt_id } });
			setValidation(out);
		} catch (e) {
			setError(e instanceof Error ? e.message : "اعتبارسنجی ناموفق بود.");
		} finally {
			setBusy(null);
		}
	}
	async function onAuthorize(tool_name) {
		setBusy(`auth:${tool_name}`);
		setError(null);
		try {
			const out = await adaAuthorize({ data: {
				agent_id: agent,
				task_type: task,
				tool_name,
				receipt_id: receipt?.receipt_id,
				site_id: "teznevise.ir"
			} });
			setAuth((prev) => [{
				tool: tool_name,
				...out
			}, ...prev.filter((a) => a.tool !== tool_name)]);
		} catch (e) {
			setError(e instanceof Error ? e.message : "مجوز ناموفق بود.");
		} finally {
			setBusy(null);
		}
	}
	async function onQuarantine() {
		setBusy("quarantine");
		setError(null);
		try {
			const out = await adaQuarantine({ data: {
				source_kind: "telegram_public",
				content_text: quarantineText,
				source_uri: "t.me/s/example"
			} });
			setQuarantine(out);
		} catch (e) {
			setError(e instanceof Error ? e.message : "قرنطینه ناموفق بود.");
		} finally {
			setBusy(null);
		}
	}
	const memories = receipt?.mandatory_memory ?? list?.memories ?? [];
	const iranian = memories.find((m) => m.canonical_key === "writing.iranian-not-dari");
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("main", {
		className: "flex flex-col gap-10",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("header", {
				className: "max-w-2xl",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Badge, {
						tone: "slate",
						children: "Ada Context Core · v0.2"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h1", {
						className: "mt-3 font-display text-3xl font-semibold sm:text-4xl",
						children: "حافظه قطعی، نه شباهت."
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "mt-3 leading-7 text-ink-muted",
						children: "قبل از نگارش پیامددار، عامل باید بسته زمینه را با دامنه دقیق بار کند. جستجوی معنایی این لایه را عوض نمی کند. پایگاه آماده است؛ ورود حساب نیست؛ ردیف ها مالک شخصی ندارند."
					})
				]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("section", {
				className: "grid gap-3 sm:grid-cols-3",
				children: [
					{
						t: "P0/P1 دامنه دار",
						d: "global، پروژه، سایت، نوع کار، عامل — نه embedding."
					},
					{
						t: "رسید امضاشده",
						d: "HMAC در پیش نمایش. نسخه دامنه کهنه کار را می بندد."
					},
					{
						t: "اسکرپ قرنطینه",
						d: "UNTRUSTED_EXTERNAL تا بازبینی. سیاست نمی شود."
					}
				].map((c) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("article", {
					className: "rounded-[20px] bg-paper-elevated p-4 shadow-[var(--shadow-border)]",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
						className: "font-display text-lg font-semibold",
						children: c.t
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "mt-2 text-sm leading-6 text-ink-muted",
						children: c.d
					})]
				}, c.t))
			}),
			error ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "rounded-[16px] bg-mark/10 px-4 py-3 text-sm leading-6 text-mark",
				role: "alert",
				children: error
			}) : null,
			list?.preview_hmac || receipt?.preview_hmac ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "rounded-[16px] bg-warn/12 px-4 py-3 text-sm leading-6 text-warn",
				children: "کلید HMAC پیش نمایش است و برای تولید نیست. کلید واقعی در محیط جدا می ماند؛ اینجا فایل .env نوشته نمی شود."
			}) : null,
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", {
				className: "rounded-[24px] bg-paper-elevated p-5 shadow-[var(--shadow-border)] sm:p-6",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
						className: "font-display text-xl font-semibold",
						children: "bootstrap"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "mt-2 max-w-2xl text-sm leading-7 text-ink-muted",
						children: "عامل و نوع کار را انتخاب کنید. حافظه اجباری همان دامنه برمی گردد، همراه رسید و وضعیت پروژه qalam/main."
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "mt-4 flex flex-col gap-4",
						children: [
							/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("fieldset", {
								className: "flex flex-col gap-2",
								children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("legend", {
									className: "text-sm text-ink-muted",
									children: "عامل"
								}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
									className: "flex flex-wrap gap-2",
									children: AGENTS.map((a) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
										type: "button",
										onClick: () => setAgent(a.id),
										className: cn("h-11 rounded-full px-4 text-sm", agent === a.id ? "bg-slate text-slate-fg" : "bg-paper-sunken text-ink-muted"),
										children: a.label
									}, a.id))
								})]
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("fieldset", {
								className: "flex flex-col gap-2",
								children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("legend", {
									className: "text-sm text-ink-muted",
									children: "نوع کار"
								}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
									className: "flex flex-wrap gap-2",
									children: TASKS.map((t) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
										type: "button",
										onClick: () => setTask(t.id),
										className: cn("h-11 rounded-full px-4 text-sm", task === t.id ? "bg-slate text-slate-fg" : "bg-paper-sunken text-ink-muted"),
										children: t.label
									}, t.id))
								})]
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
								className: "flex flex-wrap gap-2",
								children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
									onClick: onBootstrap,
									disabled: busy !== null,
									children: busy === "boot" ? "در حال بارگذاری…" : "بسته زمینه"
								}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
									variant: "secondary",
									onClick: onValidate,
									disabled: !receipt || busy !== null,
									children: "اعتبار رسید"
								})]
							})
						]
					}),
					receipt ? /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("dl", {
						className: "mt-5 grid gap-3 sm:grid-cols-2",
						children: [
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Item, {
								k: "شناسه رسید",
								v: receipt.receipt_id,
								mono: true
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Item, {
								k: "انقضا",
								v: receipt.expires_at
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Item, {
								k: "آزادسازی قلم",
								v: receipt.qalam_release ?? "—"
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Item, {
								k: "گذرنامه",
								v: receipt.passport?.agent_id ?? "ندارد"
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Item, {
								k: "وضعیت پروژه",
								v: receipt.project_state?.verified_status ?? "—"
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Item, {
								k: "حافظه اجباری",
								v: String(receipt.mandatory_memory.length)
							})
						]
					}) : null,
					validation ? /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
						className: "mt-4 text-sm",
						children: [
							"اعتبار رسید:",
							" ",
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Badge, {
								tone: validation.valid ? "ok" : "mark",
								children: validation.valid ? "معتبر" : validation.reason
							})
						]
					}) : null,
					iranian ? /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("article", {
						className: "mt-5 rounded-[16px] bg-ok/10 p-4",
						children: [
							/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
								className: "text-xs text-ok",
								children: ["P0 الزامی · ", iranian.canonical_key]
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h3", {
								className: "mt-1 font-display text-lg font-semibold",
								children: iranian.title
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
								className: "mt-2 text-sm leading-7",
								children: iranian.content
							})
						]
					}) : null
				]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", { children: [
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
					className: "font-display text-2xl font-semibold",
					children: "حافظه اجباری این بسته"
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
					className: "mt-2 max-w-2xl text-sm leading-7 text-ink-muted",
					children: "اگر بسته هنوز ساخته نشده، فهرست فعال کل پایگاه دیده می شود. کلید writing.iranian-not-dari باید در کارهای جهانی باشد."
				}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)("ul", {
					className: "mt-4 flex flex-col gap-3",
					children: memories.length === 0 && busy === "list" ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)("li", {
						className: "text-sm text-ink-muted",
						children: "در حال خواندن جدول ها…"
					}) : memories.map((m) => /* @__PURE__ */ (0, import_jsx_runtime.jsx)(MemoryCard, {
						memory: m,
						highlight: Boolean(receipt)
					}, m.id))
				})
			] }),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", {
				className: "rounded-[24px] bg-paper-elevated p-5 shadow-[var(--shadow-border)] sm:p-6",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
						className: "font-display text-xl font-semibold",
						children: "مجوز ابزار"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "mt-2 text-sm leading-7 text-ink-muted",
						children: "qalam-desk فقط خواندن دارد. انتشار باید رد یا به تصویب برود. مدل پیشنهاد می دهد؛ این لایه تصمیم می گیرد."
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "mt-4 flex flex-wrap gap-2",
						children: [
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
								variant: "secondary",
								onClick: () => onAuthorize("ada_memory_read"),
								disabled: busy !== null,
								children: "ada_memory_read"
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
								variant: "secondary",
								onClick: () => onAuthorize("wp_read"),
								disabled: busy !== null,
								children: "wp_read"
							}),
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
								variant: "ghost",
								onClick: () => onAuthorize("wp_publish"),
								disabled: busy !== null,
								children: "wp_publish"
							})
						]
					}),
					auth.length ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)("ul", {
						className: "mt-4 flex flex-col gap-2",
						children: auth.map((a) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("li", {
							className: "flex flex-wrap items-center gap-2 text-sm",
							children: [
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
									className: "font-mono text-xs",
									children: a.tool
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Badge, {
									tone: a.decision === "ALLOW" ? "ok" : a.decision === "ESCALATE" ? "warn" : "mark",
									children: a.decision
								}),
								/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
									className: "text-ink-muted",
									children: a.reason
								})
							]
						}, a.tool))
					}) : null
				]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", {
				className: "rounded-[24px] bg-paper-sunken/70 p-5 sm:p-6",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
						className: "font-display text-xl font-semibold",
						children: "قرنطینه ورودی بیرونی"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "mt-2 text-sm leading-7 text-ink-muted",
						children: "متن تلگرام یا خبر صنعت خودش سیاست نگارش نمی شود. اینجا فقط قرنطینه می شود."
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Textarea, {
						dir: "rtl",
						className: "mt-3 min-h-[120px]",
						value: quarantineText,
						onChange: (e) => setQuarantineText(e.target.value),
						"aria-label": "متن مشکوک برای قرنطینه"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
						className: "mt-3",
						children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
							variant: "secondary",
							onClick: onQuarantine,
							disabled: busy !== null || !quarantineText.trim(),
							children: "قرنطینه کن"
						})
					}),
					quarantine ? /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
						className: "mt-3 text-sm",
						children: [
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Badge, {
								tone: "warn",
								children: quarantine.quarantine_status
							}),
							" ",
							/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
								className: "font-mono text-xs text-ink-subtle",
								children: quarantine.id
							})
						]
					}) : null
				]
			}),
			list ? /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", {
				className: "grid gap-4 lg:grid-cols-2",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("article", {
					className: "rounded-[24px] bg-paper-elevated p-5 shadow-[var(--shadow-border)]",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
						className: "font-display text-xl font-semibold",
						children: "ابزارها"
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("ul", {
						className: "mt-3 flex flex-col gap-2 text-sm",
						children: list.tools.map((t) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("li", {
							className: "flex flex-wrap items-center justify-between gap-2",
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
								className: "font-mono text-xs",
								children: t.tool_name
							}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
								className: "text-ink-muted",
								children: [
									t.side_effect_class,
									" · ",
									t.default_decision
								]
							})]
						}, t.tool_name))
					})]
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("article", {
					className: "rounded-[24px] bg-paper-elevated p-5 shadow-[var(--shadow-border)]",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
							className: "font-display text-xl font-semibold",
							children: "گذرنامه و وضعیت"
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("ul", {
							className: "mt-3 flex flex-col gap-2 text-sm",
							children: list.passports.map((p) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("li", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
								className: "font-medium",
								children: p.agent_id
							}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
								className: "text-ink-muted",
								children: [
									" · ",
									p.task_type,
									" · ",
									p.allowed_tools.join("، ")
								]
							})] }, p.id))
						}),
						list.state ? /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
							className: "mt-4 text-sm leading-7 text-ink-muted",
							children: [
								list.state.objective,
								" — ",
								list.state.next_action
							]
						}) : null,
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
							className: "mt-2 text-xs text-ink-subtle",
							children: ["آزادسازی قلم ", list.qalam_release ?? "—"]
						})
					]
				})]
			}) : null,
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", {
				className: "max-w-2xl text-sm leading-7 text-ink-muted",
				children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
					className: "font-display text-lg font-semibold text-ink",
					children: "حد این فاز"
				}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
					className: "mt-2",
					children: "pgvector و استنتاج مدل اینجا نیست. برش های B و C و G و پیکره نویسندگان نام دار در این بسته ضمیمه نبودند و جعل نشدند. سایت زنده teznevise.ir منتشر نشد."
				})]
			})
		]
	});
}
function MemoryCard({ memory, highlight }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("li", {
		className: "rounded-[20px] bg-paper-elevated p-4 shadow-[var(--shadow-border)]",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "flex flex-wrap items-center gap-2",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
						className: "font-mono text-xs text-ink-subtle",
						children: memory.canonical_key
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Badge, {
						tone: memory.priority === 0 ? "ok" : "slate",
						children: ["P", memory.priority]
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
						className: "text-xs text-ink-subtle",
						children: [
							memory.scope_type,
							":",
							memory.scope_id
						]
					}),
					highlight && memory.priority <= 1 ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Badge, {
						tone: "ink",
						children: "در بسته"
					}) : null
				]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h3", {
				className: "mt-2 font-medium",
				children: memory.title
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "mt-1 text-sm leading-7 text-ink-muted",
				children: memory.summary ?? memory.content
			})
		]
	});
}
function Item({ k, v, mono }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "rounded-[12px] bg-paper-sunken/70 px-3 py-2",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("dt", {
			className: "text-xs text-ink-subtle",
			children: k
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("dd", {
			className: cn("mt-0.5 text-sm leading-6 break-all", mono && "font-mono text-xs"),
			children: v
		})]
	});
}
//#endregion
export { AdaPage as component };
