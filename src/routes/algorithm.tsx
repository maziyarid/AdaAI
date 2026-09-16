import { createFileRoute, Link } from "@tanstack/react-router";
import { ALGORITHM } from "@/lib/content";
import { Button } from "@/components/ui/button";

export const Route = createFileRoute("/algorithm")({ component: AlgorithmPage });

function AlgorithmPage() {
  return (
    <main className="flex flex-col gap-8">
      <header className="max-w-2xl">
        <h1 className="font-display text-3xl font-semibold sm:text-4xl">الگوریتم نگارش</h1>
        <p className="mt-3 leading-7 text-ink-muted">
          هفده گام قابل اجرا. اگر مصنوع اجازه ندهد، گام را رد کنید — نه اینکه قالبی روی فکر بگذارید.
        </p>
        <Link to="/desk" className="mt-4 inline-block">
          <Button>روی یک پیش نویس پیاده کنید</Button>
        </Link>
      </header>
      <ol className="grid gap-3 sm:grid-cols-2">
        {ALGORITHM.map((step) => (
          <li key={step.n} className="rounded-[20px] bg-paper-elevated p-4 shadow-[var(--shadow-border)]">
            <p className="font-mono text-xs tabular-nums text-ink-subtle">{String(step.n).padStart(2, "0")}</p>
            <h2 className="mt-1 font-display text-lg font-semibold">{step.t}</h2>
            <p className="mt-2 text-sm leading-7 text-ink-muted">{step.d}</p>
          </li>
        ))}
      </ol>
    </main>
  );
}
