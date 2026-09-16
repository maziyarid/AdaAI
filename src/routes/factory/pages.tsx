import { createFileRoute } from "@tanstack/react-router";
import { useMemo, useState } from "react";
import { Badge } from "@/components/ui/badge";
import { PAGE_AUDITS } from "@/lib/seo/data";
import type { PageDecision, PageRole } from "@/lib/seo/types";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/factory/pages")({ component: PagesPage });

const ROLE_LABEL: Record<PageRole, string> = {
  HOME: "خانه",
  SERVICE: "خدمات",
  RESEARCH_GUIDE: "راهنما",
  TOOL: "ابزار",
  DOWNLOAD: "دانلود",
  HUB: "هاب",
  POLICY: "سیاست",
  AI_WORKSPACE: "فضای هوش مصنوعی",
  FORM: "فرم",
};

const ACTION_TONE: Record<PageDecision, "ok" | "warn" | "mark" | "slate"> = {
  KEEP: "ok",
  SURGICAL_UPDATE: "warn",
  EVIDENCE_REFRESH: "warn",
  UX_REWRITE: "warn",
  ADD_FIRST_PARTY_VALUE: "slate",
  ADD_INTERACTIVE_ASSET: "slate",
  ADD_MEDIA: "slate",
  MERGE: "mark",
  REMOVE: "mark",
  NEW_PAGE: "slate",
};

function PagesPage() {
  const [role, setRole] = useState<PageRole | "ALL">("ALL");
  const items = useMemo(
    () => PAGE_AUDITS.filter((p) => (role === "ALL" ? true : p.role === role)),
    [role],
  );
  const roles = Array.from(new Set(PAGE_AUDITS.map((p) => p.role)));

  return (
    <main className="flex flex-col gap-8">
      <header className="max-w-2xl">
        <Badge tone="slate">ممیزی سودمندی · بدون نمره واحد</Badge>
        <h1 className="mt-3 font-display text-3xl font-semibold sm:text-4xl">هر صفحه یک کار دارد.</h1>
        <p className="mt-3 leading-7 text-ink-muted">
          پیش فرض حفظ محتوای مفید است. نشانی تازه از این ممیزی درنمی آید مگر کار کاربر مالک نداشته باشد.
        </p>
      </header>
      <div className="flex gap-2 overflow-x-auto pb-1">
        <Chip on={role === "ALL"} onClick={() => setRole("ALL")}>
          همه
        </Chip>
        {roles.map((r) => (
          <Chip key={r} on={role === r} onClick={() => setRole(r)}>
            {ROLE_LABEL[r]}
          </Chip>
        ))}
      </div>
      <p className="text-sm text-ink-subtle">{items.length} صفحه</p>
      <div className="flex flex-col gap-4">
        {items.map((p) => (
          <article key={p.id} className="rounded-[24px] bg-paper-elevated p-5 shadow-[var(--shadow-border)]">
            <div className="flex flex-wrap items-center gap-2">
              <span className="font-mono text-xs text-ink-subtle">{p.id}</span>
              <Badge>{ROLE_LABEL[p.role]}</Badge>
              <Badge tone={ACTION_TONE[p.action] ?? "slate"}>{p.action}</Badge>
              <Badge tone={p.priority === "P0" ? "mark" : "ink"}>{p.priority}</Badge>
            </div>
            <h2 className="mt-3 font-display text-xl font-semibold">{p.title}</h2>
            <p className="mt-1 text-sm text-ink-subtle">{p.url}</p>
            <p className="mt-3 leading-7">
              <span className="text-xs text-ink-subtle">کار کاربر · </span>
              {p.userJob}
            </p>
            <p className="mt-2 text-sm leading-7 text-ink-muted">{p.originalValue}</p>
            <dl className="mt-4 grid gap-2 text-sm sm:grid-cols-3">
              <Row k="چه کسی" v={p.who} />
              <Row k="چگونه" v={p.how} />
              <Row k="چرا" v={p.why} />
              <Row k="اتمام کار" v={p.taskCompletion} />
              <Row k="شاهد" v={p.evidenceQuality} />
              <Row k="وضعیت" v={p.status} />
            </dl>
            <p className="mt-3 text-sm leading-6 text-ink-muted">شکاف اصلی: {p.mainGap}</p>
          </article>
        ))}
      </div>
    </main>
  );
}

function Chip({ on, onClick, children }: { on: boolean; onClick: () => void; children: string }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        "h-11 shrink-0 rounded-full px-4 text-sm",
        on ? "bg-slate text-slate-fg" : "bg-paper-elevated text-ink-muted shadow-[var(--shadow-border)]",
      )}
    >
      {children}
    </button>
  );
}

function Row({ k, v }: { k: string; v: string }) {
  return (
    <div>
      <dt className="text-xs text-ink-subtle">{k}</dt>
      <dd className="mt-0.5 text-ink-muted">{v}</dd>
    </div>
  );
}
