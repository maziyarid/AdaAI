import { o as __toESM } from "../_runtime.mjs";
import { B as require_react, b as require_jsx_runtime } from "../_libs/@tanstack/react-router+[...].mjs";
import { r as Button } from "./router-IX03nS2D.mjs";
import { t as Badge } from "./badge-BctOT3LY.mjs";
import { r as ORIGINAL_VALUE_KINDS } from "./os-Bfwpjn7M.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/intake-CL5W2yuE.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
var KINDS = [
	{
		id: "FIRST_PARTY_OBSERVATION",
		label: "مشاهده دست اول"
	},
	{
		id: "FIRST_PARTY_DATA",
		label: "داده دست اول"
	},
	{
		id: "FIRST_PARTY_EXPERIMENT",
		label: "آزمایش دست اول"
	},
	{
		id: "EDITORIAL_INTERPRETATION",
		label: "تفسیر تحریریه"
	},
	{
		id: "ANECDOTE",
		label: "حکایت"
	}
];
function loadNotes() {
	try {
		return JSON.parse(localStorage.getItem("qalam-experience-intake") || "[]");
	} catch {
		return [];
	}
}
function IntakePage() {
	const [kind, setKind] = (0, import_react.useState)("FIRST_PARTY_OBSERVATION");
	const [topic, setTopic] = (0, import_react.useState)("");
	const [observation, setObservation] = (0, import_react.useState)("");
	const [cannot, setCannot] = (0, import_react.useState)("");
	const [notes, setNotes] = (0, import_react.useState)(() => typeof window === "undefined" ? [] : loadNotes());
	const [values, setValues] = (0, import_react.useState)([]);
	const [intent, setIntent] = (0, import_react.useState)("");
	const [gate, setGate] = (0, import_react.useState)(null);
	const ready = topic.trim() && observation.trim() && cannot.trim();
	const gateOk = (0, import_react.useMemo)(() => values.length > 0 && intent.trim().length > 8, [values, intent]);
	function saveNote() {
		if (!ready) return;
		const next = {
			kind,
			topic: topic.trim(),
			observation: observation.trim(),
			cannotPromoteTo: cannot.trim(),
			at: (/* @__PURE__ */ new Date()).toISOString()
		};
		const all = [...notes, next].slice(-40);
		setNotes(all);
		try {
			localStorage.setItem("qalam-experience-intake", JSON.stringify(all));
		} catch {}
		setTopic("");
		setObservation("");
		setCannot("");
	}
	function runGate() {
		if (!gateOk) {
			setGate("نشانی تازه بدون ارزش افزوده نام برده و نیت مشخص تصویب نمی شود.");
			return;
		}
		setGate("این فقط غربال کارخانه است. اگر مالک کانونی برای همین نیت هست، همان را تازه کنید. حکایت تلگرام هنوز صفحه نیست.");
	}
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("main", {
		className: "flex flex-col gap-10",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("header", {
				className: "max-w-2xl",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Badge, {
						tone: "slate",
						children: "تجربه دست اول · محرمانه بماند"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h1", {
						className: "mt-3 font-display text-3xl font-semibold sm:text-4xl",
						children: "حکایت قانون سایت نمی شود."
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "mt-3 leading-7 text-ink-muted",
						children: "پرونده دانشجو اینجا ننویسید. مشاهده را طبقه بندی کنید. داده فقط روی همین دستگاه می ماند؛ سیگنال محصول است نه فاکتور گوگل."
					})
				]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", {
				className: "rounded-[24px] bg-paper-elevated p-5 shadow-[var(--shadow-border)]",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
						className: "font-display text-xl font-semibold",
						children: "یادداشت تجربه"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("fieldset", {
						className: "mt-4",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("legend", {
							className: "text-sm font-medium",
							children: "طبقه"
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
							className: "mt-2 flex flex-col gap-2",
							children: KINDS.map((k) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("label", {
								className: "flex min-h-11 items-center gap-2 text-sm",
								children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("input", {
									type: "radio",
									name: "kind",
									checked: kind === k.id,
									onChange: () => setKind(k.id),
									className: "accent-slate"
								}), k.label]
							}, k.id))
						})]
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("label", {
						className: "mt-4 block text-sm",
						children: ["موضوع", /* @__PURE__ */ (0, import_jsx_runtime.jsx)("input", {
							className: "mt-1 h-11 w-full rounded-[12px] bg-paper-sunken px-3",
							value: topic,
							onChange: (e) => setTopic(e.target.value)
						})]
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("label", {
						className: "mt-3 block text-sm",
						children: ["مشاهده", /* @__PURE__ */ (0, import_jsx_runtime.jsx)("textarea", {
							className: "mt-1 min-h-28 w-full rounded-[12px] bg-paper-sunken p-3",
							value: observation,
							onChange: (e) => setObservation(e.target.value)
						})]
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("label", {
						className: "mt-3 block text-sm",
						children: ["به چه قانونی ارتقا داده نشود", /* @__PURE__ */ (0, import_jsx_runtime.jsx)("input", {
							className: "mt-1 h-11 w-full rounded-[12px] bg-paper-sunken px-3",
							value: cannot,
							onChange: (e) => setCannot(e.target.value)
						})]
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
						className: "mt-4",
						children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
							onClick: saveNote,
							disabled: !ready,
							children: "یادداشت را نگه دارید"
						})
					})
				]
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", { children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
				className: "font-display text-xl font-semibold",
				children: "یادداشت های همین دستگاه"
			}), notes.length === 0 ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "mt-3 text-sm text-ink-muted",
				children: "هنوز یادداشتی نیست."
			}) : /* @__PURE__ */ (0, import_jsx_runtime.jsx)("ul", {
				className: "mt-3 flex flex-col gap-2",
				children: notes.slice().reverse().map((n, i) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("li", {
					className: "rounded-[16px] bg-paper-sunken/70 p-4 text-sm leading-6",
					children: [
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Badge, { children: n.kind }),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
							className: "mt-2 font-medium",
							children: n.topic
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
							className: "text-ink-muted",
							children: n.observation
						}),
						/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("p", {
							className: "mt-1 text-xs text-ink-subtle",
							children: ["ارتقا نه: ", n.cannotPromoteTo]
						})
					]
				}, `${n.at}-${i}`))
			})] }),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("section", {
				className: "rounded-[24px] bg-paper-elevated p-5 shadow-[var(--shadow-border)]",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h2", {
						className: "font-display text-xl font-semibold",
						children: "درگاه ارزش افزوده برای نشانی تازه"
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "mt-2 text-sm leading-6 text-ink-muted",
						children: "خلاصه وب کافی نیست. حداقل یک دلیل واقعی. حجم جستجو دلیل وجود صفحه نیست."
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("label", {
						className: "mt-4 block text-sm",
						children: ["نیت کاربر به یک جمله", /* @__PURE__ */ (0, import_jsx_runtime.jsx)("input", {
							className: "mt-1 h-11 w-full rounded-[12px] bg-paper-sunken px-3",
							value: intent,
							onChange: (e) => setIntent(e.target.value)
						})]
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("fieldset", {
						className: "mt-4",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("legend", {
							className: "text-sm font-medium",
							children: "ارزش اصلی (حداقل یکی)"
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
							className: "mt-2 grid gap-2 sm:grid-cols-2",
							children: ORIGINAL_VALUE_KINDS.map((v) => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("label", {
								className: "flex min-h-11 items-center gap-2 text-sm",
								children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("input", {
									type: "checkbox",
									className: "accent-slate",
									checked: values.includes(v.id),
									onChange: () => setValues((s) => s.includes(v.id) ? s.filter((x) => x !== v.id) : [...s, v.id])
								}), v.label]
							}, v.id))
						})]
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
						className: "mt-4",
						children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
							onClick: runGate,
							children: "غربال نشانی تازه"
						})
					}),
					gate ? /* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
						className: "mt-3 text-sm leading-7",
						role: "status",
						children: gate
					}) : null
				]
			})
		]
	});
}
//#endregion
export { IntakePage as component };
