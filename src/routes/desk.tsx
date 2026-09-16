import { createFileRoute } from "@tanstack/react-router";
import { useMemo, useState } from "react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
import {
  SAMPLE_DRAFTS,
  isSampleDraft,
  scan,
  scoreLabel,
  type Finding,
  type RegisterId,
  type Severity,
} from "@/lib/editorial";
import { REGISTERS } from "@/lib/content";
import { cn } from "@/lib/utils";

type DeskSearch = { register?: string };

export const Route = createFileRoute("/desk")({
  validateSearch: (s: Record<string, unknown>): DeskSearch => ({
    register: typeof s.register === "string" ? s.register : undefined,
  }),
  component: Desk,
});

const SEV: Record<Severity, { label: string; tone: "mark" | "warn" | "ink" | "ok" }> = {
  block: { label: "مسدود", tone: "mark" },
  high: { label: "بالا", tone: "warn" },
  medium: { label: "میانه", tone: "ink" },
  note: { label: "یادداشت", tone: "ok" },
};

function isRegister(v: string | undefined): v is RegisterId {
  return REGISTERS.some((r) => r.id === v);
}

function Desk() {
  const search = Route.useSearch();
  const initial = isRegister(search.register) ? search.register : "RESEARCH_GUIDE";
  const [register, setRegister] = useState<RegisterId>(initial);
  const [text, setText] = useState(SAMPLE_DRAFTS[initial]);
  const [ran, setRan] = useState(true);

  const findings = useMemo(() => (ran ? scan(text, register) : []), [ran, text, register]);
  const score = scoreLabel(findings);

  return (
    <main className="flex flex-col gap-8">
      <header className="flex flex-col gap-3">
        <p className="text-sm text-ink-subtle">عبور ویرایشی فارسی</p>
        <h1 className="font-display text-3xl font-semibold sm:text-4xl">میز ویرایش</h1>
        <p className="max-w-2xl leading-7 text-ink-muted">
          متن را در رجیستر مقصد بسنجید. ابزار سبک را تعمیر می کند، نه ادعا را. حقه آشکارساز پیشنهاد نمی شود.
        </p>
      </header>

      <div className="flex flex-col gap-2">
        <p className="text-sm text-ink-muted">رجیستر مقصد</p>
        <div className="flex gap-2 overflow-x-auto pb-1">
          {REGISTERS.map((r) => (
            <button
              key={r.id}
              type="button"
              onClick={() => {
                setRegister(r.id);
                setText((prev) => (isSampleDraft(prev) || !prev.trim() ? SAMPLE_DRAFTS[r.id] : prev));
                setRan(true);
              }}
              className={cn(
                "h-11 shrink-0 rounded-full px-4 text-sm transition-colors duration-150",
                register === r.id ? "bg-slate text-slate-fg" : "bg-paper-elevated text-ink-muted shadow-[var(--shadow-border)]",
              )}
            >
              {r.name}
            </button>
          ))}
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
        <section className="flex flex-col gap-3">
          <Textarea
            dir="rtl"
            value={text}
            onChange={(e) => {
              setText(e.target.value);
              setRan(true);
            }}
            aria-label="پیش نویس فارسی"
            className="min-h-[320px]"
          />
          <div className="flex flex-wrap gap-2">
            <Button onClick={() => setRan(true)}>سنجش</Button>
            <Button variant="secondary" onClick={() => setText(SAMPLE_DRAFTS[register])}>
              نمونه ضعیف
            </Button>
            <Button variant="ghost" onClick={() => setText("")}>
              پاک کردن
            </Button>
          </div>
        </section>

        <section className="flex flex-col gap-4 rounded-[24px] bg-paper-elevated p-5 shadow-[var(--shadow-border)]">
          <div className="flex items-center justify-between gap-3">
            <h2 className="font-display text-xl font-semibold">تشخیص</h2>
            <Badge tone={score.tone}>{score.label}</Badge>
          </div>
          {findings.length === 0 ? (
            <p className="leading-7 text-ink-muted">
              نشانه قالبی آشکاری دیده نشد. هنوز باید پرسید: این بند چه چیز تازه ای اضافه می کند؟
            </p>
          ) : (
            <ul className="flex flex-col gap-3">
              {findings.map((f) => (
                <FindingCard key={f.id + f.evidence} finding={f} />
              ))}
            </ul>
          )}
        </section>
      </div>
    </main>
  );
}

function FindingCard({ finding }: { finding: Finding }) {
  const sev = SEV[finding.severity];
  return (
    <li className="rounded-[16px] bg-paper p-4">
      <div className="flex items-center justify-between gap-2">
        <p className="font-medium">{finding.title}</p>
        <Badge tone={sev.tone}>{sev.label}</Badge>
      </div>
      <p className="mt-2 font-mono text-xs text-mark" dir="rtl">
        «{finding.evidence}»
      </p>
      <p className="mt-2 text-sm leading-6 text-ink-muted">{finding.diagnosis}</p>
      <p className="mt-1 text-sm leading-6">{finding.repair}</p>
    </li>
  );
}
