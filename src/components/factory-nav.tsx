import { Link, useRouterState } from "@tanstack/react-router";
import { cn } from "@/lib/utils";

const ITEMS = [
  { to: "/factory", label: "داشبورد", exact: true },
  { to: "/factory/corpus", label: "پیکره میدانی" },
  { to: "/factory/notebook", label: "دفتر تجربه" },
  { to: "/factory/conflicts", label: "تعارض ها" },
  { to: "/factory/queue", label: "صف و آزمایش" },
] as const;

export function FactoryNav() {
  const pathname = useRouterState({ select: (s) => s.location.pathname });
  return (
    <nav className="-mx-1 flex gap-1 overflow-x-auto pb-1" aria-label="کارخانه">
      {ITEMS.map((item) => {
        const active = "exact" in item && item.exact ? pathname === item.to : pathname.startsWith(item.to);
        return (
          <Link
            key={item.to}
            to={item.to}
            className={cn(
              "h-11 shrink-0 rounded-full px-4 text-sm leading-[2.75rem] transition-colors duration-150",
              active ? "bg-slate text-slate-fg" : "text-ink-muted hover:bg-paper-sunken hover:text-ink",
            )}
          >
            {item.label}
          </Link>
        );
      })}
    </nav>
  );
}
