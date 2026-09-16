import { b as require_jsx_runtime } from "../_libs/@tanstack/react-router+[...].mjs";
import { i as cn } from "./router-IX03nS2D.mjs";
//#region node_modules/.nitro/vite/services/ssr/assets/badge-BctOT3LY.js
var import_jsx_runtime = require_jsx_runtime();
function Badge({ className, tone = "ink", ...props }) {
	return /* @__PURE__ */ (0, import_jsx_runtime.jsx)("span", {
		className: cn("inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium", {
			ink: "bg-paper-sunken text-ink-muted",
			slate: "bg-slate/10 text-slate",
			mark: "bg-mark/10 text-mark",
			ok: "bg-ok/10 text-ok",
			warn: "bg-warn/12 text-warn"
		}[tone], className),
		...props
	});
}
//#endregion
export { Badge as t };
