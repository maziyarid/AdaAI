import { createFileRoute, Link } from "@tanstack/react-router";
import { Badge } from "@/components/ui/badge";

export const Route = createFileRoute("/tools/")({ component: ToolsHub });

const DEMOS = [
  { to: "/tools/stat-test" as const, name: "انتخاب آزمون آماری", job: "کدام آزمون را باید در نظر بگیرم؟" },
  { to: "/tools/feasibility" as const, name: "امکان سنجی موضوع", job: "آیا این موضوع در زمان من شدنی است؟" },
  { to: "/tools/questionnaire" as const, name: "غربال پرسشنامه", job: "چه چیزی در پرسشنامه ام غلط است؟" },
  { to: "/tools/defence" as const, name: "آمادگی دفاع", job: "قبل از دفاع چه چیزی کم است؟" },
];

function ToolsHub() {
  return (
    <main className="flex flex-col gap-8">
      <header className="max-w-2xl">
        <Badge tone="slate">ابزار تصمیم</Badge>
        <h1 className="mt-3 font-display text-3xl font-semibold sm:text-4xl">کار را تمام کنید، ویجت نسازید.</h1>
        <p className="mt-3 leading-7 text-ink-muted">
          هر ابزار یک کار کاربر دارد، روش و حد دارد، و متن خزیدنی زیر فرم. جایگزین مشاور نیست. تا بازبین منصوب نشود نام فرد
          نمی گذاریم.
        </p>
      </header>
      <div className="grid gap-3 md:grid-cols-2">
        {DEMOS.map((a) => (
          <Link
            key={a.to}
            to={a.to}
            className="rounded-[24px] bg-paper-elevated p-5 shadow-[var(--shadow-border)] transition-shadow duration-150 hover:shadow-[var(--shadow-border-hover)]"
          >
            <h2 className="font-display text-xl font-semibold">{a.name}</h2>
            <p className="mt-2 text-sm leading-7 text-ink-muted">{a.job}</p>
          </Link>
        ))}
      </div>
    </main>
  );
}
