import { o as __toESM } from "../_runtime.mjs";
import { B as require_react, _ as createRootRoute, b as require_jsx_runtime, d as useRouterState, g as createFileRoute, h as lazyRouteComponent, l as Scripts, m as Outlet, p as createRouter, u as HeadContent, v as Link, y as useRouter } from "../_libs/@tanstack/react-router+[...].mjs";
import { n as clsx, t as cva } from "../_libs/class-variance-authority+clsx.mjs";
import { t as twMerge } from "../_libs/tailwind-merge.mjs";
import { a as union, i as string, n as number, r as object, t as literal } from "../_libs/zod.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/utils-C_uf36nf.js
function cn(...inputs) {
	return twMerge(clsx(inputs));
}
//#endregion
//#region node_modules/.nitro/vite/services/ssr/assets/router-IX03nS2D.js
var import_react = /* @__PURE__ */ __toESM(require_react());
var import_jsx_runtime = require_jsx_runtime();
var __defProp = Object.defineProperty;
var __exportAll = (all, no_symbols) => {
	let target = {};
	for (var name in all) __defProp(target, name, {
		get: all[name],
		enumerable: true
	});
	if (!no_symbols) __defProp(target, Symbol.toStringTag, { value: "Module" });
	return target;
};
var FALLBACK_MESSAGE = "خطای پیش بینی نشده. صفحه را تازه کنید.";
function errorMessage(error) {
	if (error instanceof Error && error.message) return error.message;
	if (typeof error === "string" && error) return error;
	return FALLBACK_MESSAGE;
}
function AppErrorComponent({ error }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("main", {
		className: "mx-auto flex min-h-[70dvh] max-w-lg flex-col items-start justify-center gap-4 px-6",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "text-sm text-ink-subtle",
				children: "خطای کارگاه"
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h1", {
				className: "font-display text-3xl font-semibold",
				children: "این صفحه الان کار نمی کند."
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "text-sm leading-7 text-ink-muted break-words",
				children: errorMessage(error)
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Link, {
				to: "/",
				className: "text-sm text-slate hover:underline",
				children: "بازگشت به خانه"
			})
		]
	});
}
var buttonVariants = cva("inline-flex items-center justify-center gap-2 font-medium transition-[opacity,transform,box-shadow] duration-150 ease-[cubic-bezier(0.22,1,0.36,1)] disabled:pointer-events-none disabled:opacity-40 active:scale-[0.98] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-slate/40", {
	variants: {
		variant: {
			primary: "bg-slate text-slate-fg shadow-[var(--shadow-border)] hover:opacity-92",
			secondary: "bg-paper-elevated text-ink shadow-[var(--shadow-border)] hover:shadow-[var(--shadow-border-hover)]",
			ghost: "bg-transparent text-ink-muted hover:bg-paper-sunken hover:text-ink",
			danger: "bg-mark text-paper-elevated hover:opacity-92"
		},
		size: {
			sm: "h-9 rounded-[8px] px-3 text-sm",
			md: "h-11 rounded-[12px] px-4 text-sm",
			lg: "h-12 rounded-[14px] px-5 text-base"
		}
	},
	defaultVariants: {
		variant: "primary",
		size: "md"
	}
});
function Button({ className, variant, size, type = "button", ...props }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("button", {
		type,
		className: cn(buttonVariants({
			variant,
			size
		}), className),
		...props
	});
}
function NotFound() {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("main", {
		className: "flex min-h-[60dvh] max-w-lg flex-col justify-center gap-5",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "text-sm text-ink-subtle",
				children: "صفحه پیدا نشد"
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("h1", {
				className: "font-display text-3xl font-semibold sm:text-4xl",
				children: "این نشانی در کارگاه نیست."
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("p", {
				className: "leading-7 text-ink-muted",
				children: "شاید پیوند کهنه باشد. میز ویرایش، کارخانه، یا انتخاب آزمون را امتحان کنید."
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
				className: "flex flex-wrap gap-3",
				children: [
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Link, {
						to: "/",
						children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, { children: "خانه" })
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Link, {
						to: "/desk",
						children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
							variant: "secondary",
							children: "میز ویرایش"
						})
					}),
					/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Link, {
						to: "/factory",
						children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Button, {
							variant: "secondary",
							children: "کارخانه"
						})
					})
				]
			})
		]
	});
}
/**
* App-wide client provider mounted once near the root (in `src/routes/__root.tsx`):
*
*   <AuthProvider><Outlet /></AuthProvider>
*
* Better Auth's React client (`@/lib/auth/client`) needs NO context provider —
* its `useSession()` works standalone — so this is a passthrough today. It's
* kept as the single, stable mount point for any future client-side providers
* (e.g. a toast or theme provider) without churning the root shell.
*/
function AuthProvider({ children }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)(import_jsx_runtime.Fragment, { children });
}
var CONNECTOR_TOKEN_READY_EVENT = "grok:connector-token-ready";
function isGrokEmbedderOrigin(origin) {
	try {
		const url = new URL(origin);
		if (url.protocol !== "https:" && url.protocol !== "http:") return false;
		const host = url.hostname.toLowerCase();
		if (host === "grok.com" || host.endsWith(".grok.com")) return true;
		if (host === "localhost" || host === "127.0.0.1" || host === "[::1]") return true;
		return false;
	} catch {
		return false;
	}
}
function isSandboxPreviewGuestHost(hostname) {
	const host = hostname.toLowerCase();
	return host === "grok-sandbox.com" || host.endsWith(".grok-sandbox.com");
}
function isRemintPreviewPair(guestHost, parentHost) {
	const guest = guestHost.toLowerCase();
	const parent = parentHost.toLowerCase();
	const i = guest.indexOf(".preview.");
	if (i <= 0) return false;
	const label = guest.slice(0, i);
	const rest = guest.slice(i + 9);
	if (label.includes(".") || !rest.includes(".")) return false;
	return parent === rest || parent === `grok.${rest}`;
}
function resolveParentEmbedderOrigin(parentIsSelf, referrer, ancestorOrigin, guestHostname = "") {
	if (parentIsSelf) return null;
	for (const candidate of [referrer, ancestorOrigin ?? ""].filter(Boolean)) try {
		const url = new URL(candidate.includes("://") ? candidate : `https://${candidate}`);
		if (url.protocol !== "https:" && url.protocol !== "http:") continue;
		if (isGrokEmbedderOrigin(url.origin)) return url.origin;
		if (isSandboxPreviewGuestHost(guestHostname) || isRemintPreviewPair(guestHostname, url.hostname)) return url.origin;
	} catch {}
	return null;
}
/**
* Guest side of the grok-web ↔ sandbox preview postMessage bridge.
*
* Activates only when this page is framed by an allowlisted Grok embedder.
* Top-level runs (download/export, local `npm run dev`, deployed sites) noop.
*/
var PREVIEW_BRIDGE_CHANNEL = "grok-preview-bridge";
var EnvelopeSchema = object({
	channel: literal(PREVIEW_BRIDGE_CHANNEL),
	version: number().int().positive(),
	type: string().min(1)
});
var HelloSchema = EnvelopeSchema.extend({ type: literal("hello") });
var NavigateSchema = EnvelopeSchema.extend({
	type: literal("navigate"),
	path: string().min(1)
});
var HistorySchema = EnvelopeSchema.extend({
	type: literal("history"),
	delta: union([literal(-1), literal(1)])
});
var ConnectorTokenReadySchema = EnvelopeSchema.extend({ type: literal("connector-token-ready") });
function isSafeBridgePath(path) {
	if (!path.startsWith("/") || path.startsWith("//") || path.includes("\\")) return false;
	try {
		return new URL(path, "https://preview.invalid").origin === "https://preview.invalid";
	} catch {
		return false;
	}
}
/**
* Origin of the Grok embedder framing this page, or null when the page runs
* top-level (download/export, local `npm run dev`, deployed sites) or under a
* non-Grok parent. Client-only; null during SSR.
*/
function resolveCurrentEmbedderOrigin() {
	if (typeof window === "undefined") return null;
	const ancestorOrigin = typeof location.ancestorOrigins !== "undefined" && location.ancestorOrigins.length > 0 ? location.ancestorOrigins[0] : null;
	return resolveParentEmbedderOrigin(window.parent === window, document.referrer, ancestorOrigin, window.location.hostname);
}
/**
* Install host↔guest messaging. Returns a dispose function.
* Noops (returns a no-op dispose) when not embedded under a Grok parent.
*/
function installPreviewHostBridge(options = {}) {
	const parentOrigin = resolveCurrentEmbedderOrigin();
	if (parentOrigin === null) return () => {};
	const ROOT_STATE_KEY = "__grokPreviewBridgeRoot";
	const originalPushState = window.history.pushState.bind(window.history);
	const originalReplaceState = window.history.replaceState.bind(window.history);
	const isAtHistoryRoot = () => {
		const state = window.history.state;
		return Boolean(state && typeof state === "object" && state[ROOT_STATE_KEY] === true);
	};
	try {
		const current = window.history.state;
		if (!(current !== null && typeof current === "object" && Object.prototype.hasOwnProperty.call(current, ROOT_STATE_KEY))) {
			const isRoot = window.history.length <= 1;
			originalReplaceState(current && typeof current === "object" ? {
				...current,
				[ROOT_STATE_KEY]: isRoot
			} : { [ROOT_STATE_KEY]: isRoot }, "", window.location.href);
		}
	} catch {}
	const post = (message) => {
		window.parent.postMessage(message, parentOrigin);
	};
	const reportLocation = () => {
		post({
			channel: PREVIEW_BRIDGE_CHANNEL,
			version: 1,
			type: "location",
			path: window.location.pathname || "/",
			search: window.location.search,
			hash: window.location.hash
		});
	};
	const reportRoutes = () => {
		const paths = options.getRoutePaths?.() ?? [];
		post({
			channel: PREVIEW_BRIDGE_CHANNEL,
			version: 1,
			type: "routes",
			paths
		});
	};
	const defaultNavigate = (path) => {
		if (!isSafeBridgePath(path)) return;
		try {
			const url = new URL(path, window.location.origin);
			if (url.origin !== window.location.origin) return;
			const next = `${url.pathname}${url.search}${url.hash}`;
			window.history.pushState(window.history.state, "", next);
			window.dispatchEvent(new PopStateEvent("popstate", { state: window.history.state }));
		} catch {}
	};
	const navigate = (path) => {
		if (!isSafeBridgePath(path)) return;
		if (options.navigate) {
			options.navigate(path);
			return;
		}
		defaultNavigate(path);
	};
	const announce = () => {
		reportLocation();
		reportRoutes();
		post({
			channel: PREVIEW_BRIDGE_CHANNEL,
			version: 1,
			type: "ready"
		});
	};
	const onHello = (data) => {
		if (!HelloSchema.safeParse(data).success) return;
		announce();
	};
	const onNavigate = (data) => {
		const parsed = NavigateSchema.safeParse(data);
		if (!parsed.success) return;
		navigate(parsed.data.path);
		queueMicrotask(reportLocation);
	};
	const onHistory = (data) => {
		const parsed = HistorySchema.safeParse(data);
		if (!parsed.success) return;
		if (parsed.data.delta === -1 && isAtHistoryRoot()) return;
		window.history.go(parsed.data.delta);
	};
	const onConnectorTokenReady = (data) => {
		if (!ConnectorTokenReadySchema.safeParse(data).success) return;
		window.dispatchEvent(new Event(CONNECTOR_TOKEN_READY_EVENT));
	};
	const hostMessageHandlers = /* @__PURE__ */ new Map([
		["hello", onHello],
		["navigate", onNavigate],
		["history", onHistory],
		["connector-token-ready", onConnectorTokenReady]
	]);
	const onMessage = (event) => {
		if (event.source !== window.parent) return;
		if (event.origin !== parentOrigin) return;
		const envelope = EnvelopeSchema.safeParse(event.data);
		if (!envelope.success || envelope.data.version !== 1) return;
		hostMessageHandlers.get(envelope.data.type)?.(event.data);
	};
	const onPopState = () => {
		reportLocation();
	};
	const onHashChange = () => {
		reportLocation();
	};
	window.history.pushState = (data, unused, url) => {
		const next = data && typeof data === "object" ? {
			...data,
			[ROOT_STATE_KEY]: false
		} : data;
		originalPushState(next, unused, url);
		reportLocation();
	};
	window.history.replaceState = (data, unused, url) => {
		const next = isAtHistoryRoot() ? {
			...data && typeof data === "object" ? data : {},
			[ROOT_STATE_KEY]: true
		} : data;
		originalReplaceState(next, unused, url);
		reportLocation();
	};
	window.addEventListener("message", onMessage);
	window.addEventListener("popstate", onPopState);
	window.addEventListener("hashchange", onHashChange);
	announce();
	return () => {
		window.removeEventListener("message", onMessage);
		window.removeEventListener("popstate", onPopState);
		window.removeEventListener("hashchange", onHashChange);
		window.history.pushState = originalPushState;
		window.history.replaceState = originalReplaceState;
	};
}
/** Collect static path patterns from a TanStack route tree (best-effort). */
function collectRoutePathsFromTree(routeTree) {
	const paths = /* @__PURE__ */ new Set();
	const walk = (node) => {
		if (!node || typeof node !== "object") return;
		const record = node;
		const full = typeof record.fullPath === "string" ? record.fullPath : typeof record.path === "string" ? record.path : null;
		if (full !== null && full !== "") paths.add(full.startsWith("/") ? full : `/${full}`);
		else if (full === "") paths.add("/");
		const children = record.children;
		if (Array.isArray(children)) for (const child of children) walk(child);
		else if (children && typeof children === "object") for (const child of Object.values(children)) walk(child);
	};
	walk(routeTree);
	return [...paths];
}
/**
* Mount once in `__root.tsx` so the Grok preview chrome can drive navigation
* (and later receive registered routes). Noops when the app is not embedded.
*/
function PreviewHostBridge() {
	const router = useRouter();
	(0, import_react.useEffect)(() => {
		return installPreviewHostBridge({
			navigate: (path) => {
				router.history.push(path);
			},
			getRoutePaths: () => collectRoutePathsFromTree(router.routeTree)
		});
	}, [router]);
	return null;
}
var WRITE_NAV = [
	{
		to: "/",
		label: "خانه"
	},
	{
		to: "/desk",
		label: "میز ویرایش"
	},
	{
		to: "/registers",
		label: "رجیستر"
	},
	{
		to: "/patterns",
		label: "الگوها"
	},
	{
		to: "/algorithm",
		label: "الگوریتم"
	},
	{
		to: "/bible",
		label: "کتابچه"
	},
	{
		to: "/corpus",
		label: "پیکره نگارش"
	},
	{
		to: "/ada",
		label: "حافظه Ada"
	},
	{
		to: "/tools",
		label: "ابزارها"
	}
];
var FACTORY_NAV = [
	{
		to: "/factory",
		label: "داشبورد"
	},
	{
		to: "/factory/corpus",
		label: "پیکره سئو"
	},
	{
		to: "/factory/notebook",
		label: "دفتر تجربه"
	},
	{
		to: "/factory/conflicts",
		label: "تعارض"
	},
	{
		to: "/factory/queue",
		label: "صف"
	},
	{
		to: "/factory/trust",
		label: "اعتماد"
	},
	{
		to: "/factory/pages",
		label: "صفحات"
	},
	{
		to: "/factory/ux",
		label: "تجربه"
	},
	{
		to: "/factory/intel",
		label: "پژوهش"
	},
	{
		to: "/factory/os",
		label: "وضعیت"
	}
];
var TOOLS_NAV = [
	{
		to: "/tools",
		label: "همه ابزارها"
	},
	{
		to: "/tools/stat-test",
		label: "انتخاب آزمون"
	},
	{
		to: "/tools/feasibility",
		label: "امکان سنجی"
	},
	{
		to: "/tools/questionnaire",
		label: "پرسشنامه"
	},
	{
		to: "/tools/defence",
		label: "آمادگی دفاع"
	}
];
function AppShell({ children }) {
	const pathname = useRouterState({ select: (s) => s.location.pathname });
	const factory = pathname.startsWith("/factory");
	const tools = pathname.startsWith("/tools");
	const nav = factory ? FACTORY_NAV : tools ? TOOLS_NAV : WRITE_NAV;
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
		className: "min-h-dvh",
		children: [
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("a", {
				href: "#main",
				className: "skip-link",
				children: "رفتن به محتوا"
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("header", {
				className: "sticky top-0 z-20 border-b border-rule/80 bg-paper/90 backdrop-blur-sm",
				children: /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
					className: "mx-auto flex max-w-6xl flex-col gap-3 px-4 py-3 sm:px-6",
					children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
						className: "flex items-center justify-between gap-3",
						children: [/* @__PURE__ */ (0, import_jsx_runtime.jsxs)(Link, {
							to: "/",
							className: "flex items-center gap-3",
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
								className: "flex size-9 items-center justify-center rounded-[10px] bg-slate text-slate-fg",
								children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(NibMark, {})
							}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("span", {
								className: "leading-tight",
								children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
									className: "block font-display text-lg font-semibold tracking-tight",
									children: "Qalam"
								}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
									className: "block text-xs text-ink-muted",
									children: factory ? "حافظه سئو" : tools ? "ابزار تصمیم" : "کارگاه نگارش"
								})]
							})]
						}), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("div", {
							className: "flex rounded-full bg-paper-sunken p-1",
							children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Link, {
								to: "/",
								className: cn("h-10 rounded-full px-3 text-sm leading-10", !factory ? "bg-slate text-slate-fg" : "text-ink-muted"),
								children: "نگارش"
							}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Link, {
								to: "/factory",
								className: cn("h-10 rounded-full px-3 text-sm leading-10", factory ? "bg-slate text-slate-fg" : "text-ink-muted"),
								children: "کارخانه"
							})]
						})]
					}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("nav", {
						className: "-mx-4 flex gap-1 overflow-x-auto px-4 pb-1 sm:mx-0 sm:px-0",
						"aria-label": "اصلی",
						children: nav.map((item) => {
							const active = item.to === "/" || item.to === "/factory" || item.to === "/tools" ? pathname === item.to || pathname === `${item.to}/` : pathname.startsWith(item.to);
							return /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Link, {
								to: item.to,
								className: cn("h-11 shrink-0 rounded-full px-3 text-sm leading-[2.75rem] transition-colors duration-150", active ? "bg-slate text-slate-fg" : "text-ink-muted hover:bg-paper-sunken hover:text-ink"),
								children: item.label
							}, item.to);
						})
					})]
				})
			}),
			/* @__PURE__ */ (0, import_jsx_runtime.jsx)("div", {
				id: "main",
				className: "mx-auto max-w-6xl px-4 py-8 sm:px-6 sm:py-10",
				children
			})
		]
	});
}
function NibMark() {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("svg", {
		viewBox: "0 0 24 24",
		className: "size-5",
		"aria-hidden": "true",
		fill: "none",
		stroke: "currentColor",
		strokeWidth: "1.8",
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("path", {
			d: "M6 19c3.4-1 6-5.2 7-9.4.3-1.4 1.8-2.1 3.1-1.7 1.1.3 1.9 1.5 1.7 2.7-.5 3.8-3.4 8-8.5 9.4",
			strokeLinecap: "round"
		}), /* @__PURE__ */ (0, import_jsx_runtime.jsx)("path", {
			d: "M16.6 6.2L18.8 3.4",
			strokeLinecap: "round"
		})]
	});
}
var styles_default = "/assets/styles-8QgfOrWu.css";
var APP_NAME = "Qalam — کارگاه نگارش";
var Route$27 = createRootRoute({
	head: () => ({
		meta: [
			{ charSet: "utf-8" },
			{
				name: "viewport",
				content: "width=device-width, initial-scale=1"
			},
			{ title: APP_NAME },
			{
				name: "description",
				content: "کارگاه نگارش فارسی ایرانی: فکر به فارسی، رجیستر کامل از لندینگ تا پایان نامه، و حافظه قطعی Ada. بدون تقلید صدا و بدون حقه آشکارساز."
			},
			{
				name: "theme-color",
				content: "#F6F1E8"
			}
		],
		links: [
			{
				rel: "icon",
				type: "image/svg+xml",
				href: "/favicon.svg"
			},
			{
				rel: "stylesheet",
				href: styles_default
			},
			{
				rel: "manifest",
				href: "/__grok/manifest.webmanifest"
			},
			{
				rel: "apple-touch-icon",
				href: "/__grok/icon-180.png"
			},
			{
				rel: "preconnect",
				href: "https://fonts.googleapis.com"
			},
			{
				rel: "preconnect",
				href: "https://fonts.gstatic.com",
				crossOrigin: "anonymous"
			},
			{
				rel: "stylesheet",
				href: "https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=Newsreader:opsz,wght@6..72,500;6..72,600;6..72,700&family=Vazirmatn:wght@400;500;600;700&display=swap"
			}
		]
	}),
	component: () => /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("html", {
		lang: "fa",
		dir: "rtl",
		className: "antialiased",
		suppressHydrationWarning: true,
		children: [/* @__PURE__ */ (0, import_jsx_runtime.jsx)("head", { children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(HeadContent, {}) }), /* @__PURE__ */ (0, import_jsx_runtime.jsxs)("body", {
			className: "min-h-dvh bg-paper text-ink",
			children: [
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)(PreviewHostBridge, {}),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)(AuthProvider, { children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(AppShell, { children: /* @__PURE__ */ (0, import_jsx_runtime.jsx)(Outlet, {}) }) }),
				/* @__PURE__ */ (0, import_jsx_runtime.jsx)(Scripts, {})
			]
		})]
	})
});
var $$splitComponentImporter$26 = () => import("./routes-B8tjlsca.mjs");
var Route$26 = createFileRoute("/")({ component: lazyRouteComponent($$splitComponentImporter$26, "component") });
var $$splitComponentImporter$25 = () => import("./ada-BoKCDgFO.mjs");
var Route$25 = createFileRoute("/ada")({ component: lazyRouteComponent($$splitComponentImporter$25, "component") });
var $$splitComponentImporter$24 = () => import("./algorithm-h5LyVgnW.mjs");
var Route$24 = createFileRoute("/algorithm")({ component: lazyRouteComponent($$splitComponentImporter$24, "component") });
var $$splitComponentImporter$23 = () => import("./bible-ZnwwsqvL.mjs");
var Route$23 = createFileRoute("/bible")({ component: lazyRouteComponent($$splitComponentImporter$23, "component") });
var $$splitComponentImporter$22 = () => import("./corpus-BqgzAnXQ.mjs");
var Route$22 = createFileRoute("/corpus")({ component: lazyRouteComponent($$splitComponentImporter$22, "component") });
var $$splitComponentImporter$21 = () => import("./desk-BiHZK64h.mjs");
var Route$21 = createFileRoute("/desk")({
	validateSearch: (s) => ({ register: typeof s.register === "string" ? s.register : void 0 }),
	component: lazyRouteComponent($$splitComponentImporter$21, "component")
});
var $$splitComponentImporter$20 = () => import("./factory-IRnA2oBS.mjs");
var Route$20 = createFileRoute("/factory")({ component: lazyRouteComponent($$splitComponentImporter$20, "component") });
var $$splitComponentImporter$19 = () => import("./patterns-CVO_fYJ_.mjs");
var Route$19 = createFileRoute("/patterns")({ component: lazyRouteComponent($$splitComponentImporter$19, "component") });
var $$splitComponentImporter$18 = () => import("./registers-DYdJTRHF.mjs");
var Route$18 = createFileRoute("/registers")({ component: lazyRouteComponent($$splitComponentImporter$18, "component") });
var $$splitComponentImporter$17 = () => import("./tools-Osxu1B4W.mjs");
var Route$17 = createFileRoute("/tools")({ component: lazyRouteComponent($$splitComponentImporter$17, "component") });
var $$splitComponentImporter$16 = () => import("./factory-1wAnzTQu.mjs");
var Route$16 = createFileRoute("/factory/")({ component: lazyRouteComponent($$splitComponentImporter$16, "component") });
var $$splitComponentImporter$15 = () => import("./briefing-DhMqKEq_.mjs");
var Route$15 = createFileRoute("/factory/briefing")({ component: lazyRouteComponent($$splitComponentImporter$15, "component") });
var $$splitComponentImporter$14 = () => import("./conflicts-F9pb1K9x.mjs");
var Route$14 = createFileRoute("/factory/conflicts")({ component: lazyRouteComponent($$splitComponentImporter$14, "component") });
var $$splitComponentImporter$13 = () => import("./corpus-D6S89Dmz.mjs");
var Route$13 = createFileRoute("/factory/corpus")({ component: lazyRouteComponent($$splitComponentImporter$13, "component") });
var $$splitComponentImporter$12 = () => import("./intake-CL5W2yuE.mjs");
var Route$12 = createFileRoute("/factory/intake")({ component: lazyRouteComponent($$splitComponentImporter$12, "component") });
var $$splitComponentImporter$11 = () => import("./intel-DJu6C_QC.mjs");
var Route$11 = createFileRoute("/factory/intel")({ component: lazyRouteComponent($$splitComponentImporter$11, "component") });
var $$splitComponentImporter$10 = () => import("./notebook-Br1R8kMQ.mjs");
var Route$10 = createFileRoute("/factory/notebook")({ component: lazyRouteComponent($$splitComponentImporter$10, "component") });
var $$splitComponentImporter$9 = () => import("./os-GdnMKvFU.mjs");
var Route$9 = createFileRoute("/factory/os")({ component: lazyRouteComponent($$splitComponentImporter$9, "component") });
var $$splitComponentImporter$8 = () => import("./pages-Cq5fe6Ww.mjs");
var Route$8 = createFileRoute("/factory/pages")({ component: lazyRouteComponent($$splitComponentImporter$8, "component") });
var $$splitComponentImporter$7 = () => import("./queue-CxSzwuYk.mjs");
var Route$7 = createFileRoute("/factory/queue")({ component: lazyRouteComponent($$splitComponentImporter$7, "component") });
var $$splitComponentImporter$6 = () => import("./trust-BsJ5rXKf.mjs");
var Route$6 = createFileRoute("/factory/trust")({ component: lazyRouteComponent($$splitComponentImporter$6, "component") });
var $$splitComponentImporter$5 = () => import("./ux-CkyrYxr7.mjs");
var Route$5 = createFileRoute("/factory/ux")({ component: lazyRouteComponent($$splitComponentImporter$5, "component") });
var $$splitComponentImporter$4 = () => import("./tools-DjcfEdZN.mjs");
var Route$4 = createFileRoute("/tools/")({ component: lazyRouteComponent($$splitComponentImporter$4, "component") });
var $$splitComponentImporter$3 = () => import("./defence-BSsElGaQ.mjs");
var Route$3 = createFileRoute("/tools/defence")({ component: lazyRouteComponent($$splitComponentImporter$3, "component") });
var $$splitComponentImporter$2 = () => import("./feasibility-ZqmoFbvc.mjs");
var Route$2 = createFileRoute("/tools/feasibility")({ component: lazyRouteComponent($$splitComponentImporter$2, "component") });
var $$splitComponentImporter$1 = () => import("./questionnaire-B1aZWQ-t.mjs");
var Route$1 = createFileRoute("/tools/questionnaire")({ component: lazyRouteComponent($$splitComponentImporter$1, "component") });
var $$splitComponentImporter = () => import("./stat-test-DZ3zcOOc.mjs");
var Route = createFileRoute("/tools/stat-test")({ component: lazyRouteComponent($$splitComponentImporter, "component") });
var IndexRoute = Route$26.update({
	id: "/",
	path: "/",
	getParentRoute: () => Route$27
});
var AdaRoute = Route$25.update({
	id: "/ada",
	path: "/ada",
	getParentRoute: () => Route$27
});
var AlgorithmRoute = Route$24.update({
	id: "/algorithm",
	path: "/algorithm",
	getParentRoute: () => Route$27
});
var BibleRoute = Route$23.update({
	id: "/bible",
	path: "/bible",
	getParentRoute: () => Route$27
});
var CorpusRoute = Route$22.update({
	id: "/corpus",
	path: "/corpus",
	getParentRoute: () => Route$27
});
var DeskRoute = Route$21.update({
	id: "/desk",
	path: "/desk",
	getParentRoute: () => Route$27
});
var FactoryRoute = Route$20.update({
	id: "/factory",
	path: "/factory",
	getParentRoute: () => Route$27
});
var PatternsRoute = Route$19.update({
	id: "/patterns",
	path: "/patterns",
	getParentRoute: () => Route$27
});
var RegistersRoute = Route$18.update({
	id: "/registers",
	path: "/registers",
	getParentRoute: () => Route$27
});
var ToolsRoute = Route$17.update({
	id: "/tools",
	path: "/tools",
	getParentRoute: () => Route$27
});
var FactoryIndexRoute = Route$16.update({
	id: "/",
	path: "/",
	getParentRoute: () => FactoryRoute
});
var FactoryBriefingRoute = Route$15.update({
	id: "/briefing",
	path: "/briefing",
	getParentRoute: () => FactoryRoute
});
var FactoryConflictsRoute = Route$14.update({
	id: "/conflicts",
	path: "/conflicts",
	getParentRoute: () => FactoryRoute
});
var FactoryCorpusRoute = Route$13.update({
	id: "/corpus",
	path: "/corpus",
	getParentRoute: () => FactoryRoute
});
var FactoryIntakeRoute = Route$12.update({
	id: "/intake",
	path: "/intake",
	getParentRoute: () => FactoryRoute
});
var FactoryIntelRoute = Route$11.update({
	id: "/intel",
	path: "/intel",
	getParentRoute: () => FactoryRoute
});
var FactoryNotebookRoute = Route$10.update({
	id: "/notebook",
	path: "/notebook",
	getParentRoute: () => FactoryRoute
});
var FactoryOsRoute = Route$9.update({
	id: "/os",
	path: "/os",
	getParentRoute: () => FactoryRoute
});
var FactoryPagesRoute = Route$8.update({
	id: "/pages",
	path: "/pages",
	getParentRoute: () => FactoryRoute
});
var FactoryQueueRoute = Route$7.update({
	id: "/queue",
	path: "/queue",
	getParentRoute: () => FactoryRoute
});
var FactoryTrustRoute = Route$6.update({
	id: "/trust",
	path: "/trust",
	getParentRoute: () => FactoryRoute
});
var FactoryUxRoute = Route$5.update({
	id: "/ux",
	path: "/ux",
	getParentRoute: () => FactoryRoute
});
var ToolsIndexRoute = Route$4.update({
	id: "/",
	path: "/",
	getParentRoute: () => ToolsRoute
});
var ToolsDefenceRoute = Route$3.update({
	id: "/defence",
	path: "/defence",
	getParentRoute: () => ToolsRoute
});
var ToolsFeasibilityRoute = Route$2.update({
	id: "/feasibility",
	path: "/feasibility",
	getParentRoute: () => ToolsRoute
});
var ToolsQuestionnaireRoute = Route$1.update({
	id: "/questionnaire",
	path: "/questionnaire",
	getParentRoute: () => ToolsRoute
});
var ToolsStatTestRoute = Route.update({
	id: "/stat-test",
	path: "/stat-test",
	getParentRoute: () => ToolsRoute
});
var FactoryRouteChildren = {
	FactoryBriefingRoute,
	FactoryConflictsRoute,
	FactoryCorpusRoute,
	FactoryIntakeRoute,
	FactoryIntelRoute,
	FactoryNotebookRoute,
	FactoryOsRoute,
	FactoryPagesRoute,
	FactoryQueueRoute,
	FactoryTrustRoute,
	FactoryUxRoute,
	FactoryIndexRoute
};
var FactoryRouteWithChildren = FactoryRoute._addFileChildren(FactoryRouteChildren);
var ToolsRouteChildren = {
	ToolsDefenceRoute,
	ToolsFeasibilityRoute,
	ToolsQuestionnaireRoute,
	ToolsStatTestRoute,
	ToolsIndexRoute
};
var rootRouteChildren = {
	IndexRoute,
	AdaRoute,
	AlgorithmRoute,
	BibleRoute,
	CorpusRoute,
	DeskRoute,
	FactoryRoute: FactoryRouteWithChildren,
	PatternsRoute,
	RegistersRoute,
	ToolsRoute: ToolsRoute._addFileChildren(ToolsRouteChildren)
};
var routeTree = Route$27._addFileChildren(rootRouteChildren)._addFileTypes();
var router_exports = /* @__PURE__ */ __exportAll({ getRouter: () => getRouter });
function getRouter() {
	return createRouter({
		routeTree,
		defaultErrorComponent: AppErrorComponent,
		defaultNotFoundComponent: NotFound
	});
}
//#endregion
export { cn as i, Route$21 as n, Button as r, router_exports as t };
