import { Link, useRouterState } from "@tanstack/react-router";
import type { ReactNode } from "react";
import { cn } from "@/lib/utils";

const WRITE_NAV = [
  { to: "/", label: "خانه" },
  { to: "/desk", label: "میز ویرایش" },
  { to: "/registers", label: "رجیستر" },
  { to: "/patterns", label: "الگوها" },
  { to: "/algorithm", label: "الگوریتم" },
  { to: "/bible", label: "کتابچه" },
  { to: "/corpus", label: "پیکره نگارش" },
  { to: "/ada", label: "حافظه Ada" },
  { to: "/tools", label: "ابزارها" },
] as const;

const FACTORY_NAV = [
  { to: "/factory", label: "داشبورد" },
  { to: "/factory/corpus", label: "پیکره سئو" },
  { to: "/factory/notebook", label: "دفتر تجربه" },
  { to: "/factory/conflicts", label: "تعارض" },
  { to: "/factory/queue", label: "صف" },
  { to: "/factory/trust", label: "اعتماد" },
  { to: "/factory/pages", label: "صفحات" },
  { to: "/factory/ux", label: "تجربه" },
  { to: "/factory/intel", label: "پژوهش" },
  { to: "/factory/os", label: "وضعیت" },
] as const;

const TOOLS_NAV = [
  { to: "/tools", label: "همه ابزارها" },
  { to: "/tools/stat-test", label: "انتخاب آزمون" },
  { to: "/tools/feasibility", label: "امکان سنجی" },
  { to: "/tools/questionnaire", label: "پرسشنامه" },
  { to: "/tools/defence", label: "آمادگی دفاع" },
] as const;

export function AppShell({ children }: { children: ReactNode }) {
  const pathname = useRouterState({ select: (s) => s.location.pathname });
  const factory = pathname.startsWith("/factory");
  const tools = pathname.startsWith("/tools");
  const nav = factory ? FACTORY_NAV : tools ? TOOLS_NAV : WRITE_NAV;

  return (
    <div className="min-h-dvh">
      <a href="#main" className="skip-link">
        رفتن به محتوا
      </a>
      <header className="sticky top-0 z-20 border-b border-rule/80 bg-paper/90 backdrop-blur-sm">
        <div className="mx-auto flex max-w-6xl flex-col gap-3 px-4 py-3 sm:px-6">
          <div className="flex items-center justify-between gap-3">
            <Link to="/" className="flex items-center gap-3">
              <span className="flex size-9 items-center justify-center rounded-[10px] bg-slate text-slate-fg">
                <NibMark />
              </span>
              <span className="leading-tight">
                <span className="block font-display text-lg font-semibold tracking-tight">Qalam</span>
                <span className="block text-xs text-ink-muted">
                  {factory ? "حافظه سئو" : tools ? "ابزار تصمیم" : "کارگاه نگارش"}
                </span>
              </span>
            </Link>
            <div className="flex rounded-full bg-paper-sunken p-1">
              <Link
                to="/"
                className={cn(
                  "h-10 rounded-full px-3 text-sm leading-10",
                  !factory ? "bg-slate text-slate-fg" : "text-ink-muted",
                )}
              >
                نگارش
              </Link>
              <Link
                to="/factory"
                className={cn(
                  "h-10 rounded-full px-3 text-sm leading-10",
                  factory ? "bg-slate text-slate-fg" : "text-ink-muted",
                )}
              >
                کارخانه
              </Link>
            </div>
          </div>
          <nav className="-mx-4 flex gap-1 overflow-x-auto px-4 pb-1 sm:mx-0 sm:px-0" aria-label="اصلی">
            {nav.map((item) => {
              const active =
                item.to === "/" || item.to === "/factory" || item.to === "/tools"
                  ? pathname === item.to || pathname === `${item.to}/`
                  : pathname.startsWith(item.to);
              return (
                <Link
                  key={item.to}
                  to={item.to}
                  className={cn(
                    "h-11 shrink-0 rounded-full px-3 text-sm leading-[2.75rem] transition-colors duration-150",
                    active ? "bg-slate text-slate-fg" : "text-ink-muted hover:bg-paper-sunken hover:text-ink",
                  )}
                >
                  {item.label}
                </Link>
              );
            })}
          </nav>
        </div>
      </header>
      <div id="main" className="mx-auto max-w-6xl px-4 py-8 sm:px-6 sm:py-10">
        {children}
      </div>
    </div>
  );
}

function NibMark() {
  return (
    <svg viewBox="0 0 24 24" className="size-5" aria-hidden="true" fill="none" stroke="currentColor" strokeWidth="1.8">
      <path d="M6 19c3.4-1 6-5.2 7-9.4.3-1.4 1.8-2.1 3.1-1.7 1.1.3 1.9 1.5 1.7 2.7-.5 3.8-3.4 8-8.5 9.4" strokeLinecap="round" />
      <path d="M16.6 6.2L18.8 3.4" strokeLinecap="round" />
    </svg>
  );
}
