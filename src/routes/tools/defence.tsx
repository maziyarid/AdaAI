import { createFileRoute } from "@tanstack/react-router";
import { useMemo, useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { UsefulFeedback } from "@/components/useful-feedback";
import { DEFENCE_SECTIONS, defenceText } from "@/lib/tools/defence";

export const Route = createFileRoute("/tools/defence")({ component: DefencePage });

function DefencePage() {
  const [checked, setChecked] = useState<Record<string, boolean>>({});
  const total = DEFENCE_SECTIONS.reduce((n, s) => n + s.items.length, 0);
  const done = Object.values(checked).filter(Boolean).length;
  const text = useMemo(() => defenceText(checked), [checked]);

  function saveFile() {
    const blob = new Blob([text], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "defence-checklist.txt";
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <main className="flex flex-col gap-10">
      <header className="max-w-2xl">
        <Badge tone="slate">چک لیست · قابل ذخیره</Badge>
        <h1 className="mt-3 font-display text-3xl font-semibold sm:text-4xl">قبل از دفاع چه چیزی کم است؟</h1>
        <p className="mt-3 leading-7 text-ink-muted">
          فهرست عمومی مسیر تا دفاع. آیین نامه دانشگاه شما ممکن است موارد اضافه بخواهد. داده دانشجو اینجا ذخیره نمی شود.
        </p>
        <p className="mt-2 text-sm text-ink-subtle" aria-live="polite">
          {done} از {total} مورد علامت خورده است.
        </p>
      </header>

      {DEFENCE_SECTIONS.map((section) => (
        <section key={section.id} className="rounded-[24px] bg-paper-elevated p-5 shadow-[var(--shadow-border)]">
          <h2 className="font-display text-xl font-semibold">{section.title}</h2>
          <ul className="mt-3 flex flex-col gap-2">
            {section.items.map((item, i) => {
              const key = `${section.id}-${i}`;
              return (
                <li key={key}>
                  <label className="flex min-h-11 cursor-pointer items-start gap-3 rounded-[12px] px-1 py-1 hover:bg-paper-sunken/70">
                    <input
                      type="checkbox"
                      className="mt-1 size-4 accent-slate"
                      checked={Boolean(checked[key])}
                      onChange={(e) => setChecked((s) => ({ ...s, [key]: e.target.checked }))}
                    />
                    <span className="text-sm leading-6">{item}</span>
                  </label>
                </li>
              );
            })}
          </ul>
        </section>
      ))}

      <div>
        <Button onClick={saveFile}>فهرست را ذخیره کنید</Button>
      </div>

      <UsefulFeedback page="/tools/defence" />

      <section>
        <h2 className="font-display text-xl font-semibold">نسخه متنی</h2>
        <pre className="mt-3 overflow-x-auto whitespace-pre-wrap rounded-[16px] bg-paper-sunken/70 p-4 text-sm leading-7">
          {text}
        </pre>
      </section>
    </main>
  );
}
