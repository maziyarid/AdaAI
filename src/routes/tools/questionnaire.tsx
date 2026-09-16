import { createFileRoute } from "@tanstack/react-router";
import { useMemo, useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { UsefulFeedback } from "@/components/useful-feedback";
import { Q_FALLBACK, Q_ITEMS, screenQuestionnaire, type QAnswer } from "@/lib/tools/questionnaire";

export const Route = createFileRoute("/tools/questionnaire")({ component: QuestionnairePage });

function QuestionnairePage() {
  const [answers, setAnswers] = useState<Record<string, QAnswer | "">>(
    Object.fromEntries(Q_ITEMS.map((i) => [i.id, ""])) as Record<string, QAnswer | "">,
  );
  const [submitted, setSubmitted] = useState(false);
  const flags = useMemo(() => (submitted ? screenQuestionnaire(answers) : null), [submitted, answers]);
  const missing = submitted && !flags;

  return (
    <main className="flex flex-col gap-10">
      <header className="max-w-2xl">
        <Badge tone="slate">غربال · نه نمره روایی</Badge>
        <h1 className="mt-3 font-display text-3xl font-semibold sm:text-4xl">چه چیزی در پرسشنامه ام غلط است؟</h1>
        <p className="mt-3 leading-7 text-ink-muted">
          نقص های رایج قبل از نمونه اصلی. روایی سازه، تحلیل عاملی، و هنجاریابی را نمی فروشد.
        </p>
      </header>

      <form
        className="flex flex-col gap-6"
        onSubmit={(e) => {
          e.preventDefault();
          setSubmitted(true);
        }}
      >
        {Q_ITEMS.map((item) => (
          <fieldset key={item.id} className="rounded-[20px] bg-paper-elevated p-4 shadow-[var(--shadow-border)]">
            <legend className="px-1 text-sm font-medium">{item.prompt}</legend>
            <p className="mt-2 text-xs leading-6 text-ink-subtle">{item.hint}</p>
            <div className="mt-3 flex flex-wrap gap-2">
              {(
                [
                  ["yes", "بله"],
                  ["no", "خیر"],
                  ["unsure", "نمی دانم"],
                ] as const
              ).map(([id, label]) => (
                <label
                  key={id}
                  className="flex h-11 cursor-pointer items-center gap-2 rounded-full bg-paper-sunken px-4 text-sm"
                >
                  <input
                    type="radio"
                    name={item.id}
                    checked={answers[item.id] === id}
                    onChange={() => {
                      setAnswers((s) => ({ ...s, [item.id]: id }));
                      setSubmitted(false);
                    }}
                    className="accent-slate"
                  />
                  {label}
                </label>
              ))}
            </div>
          </fieldset>
        ))}
        {missing ? (
          <p className="text-sm text-mark" role="alert">
            به هر هشت پرسش پاسخ دهید.
          </p>
        ) : null}
        <div>
          <Button type="submit">غربال را ببینید</Button>
        </div>
      </form>

      {flags ? (
        <section className="flex flex-col gap-3" aria-live="polite">
          <h2 className="font-display text-xl font-semibold">نتیجه غربال</h2>
          {flags.map((f) => (
            <article key={f.id} className="rounded-[20px] bg-paper-elevated p-4 shadow-[var(--shadow-border)]">
              <Badge tone={f.level === "stop" ? "mark" : f.level === "risk" ? "warn" : "ok"}>
                {f.level === "stop" ? "ایست" : f.level === "risk" ? "خطر" : "مانع آشکار نیست"}
              </Badge>
              <h3 className="mt-2 font-medium">{f.title}</h3>
              <p className="mt-1 text-sm leading-7 text-ink-muted">{f.detail}</p>
            </article>
          ))}
        </section>
      ) : null}

      <UsefulFeedback page="/tools/questionnaire" />

      <section>
        <h2 className="font-display text-2xl font-semibold">همان پرسش ها، بدون فرم</h2>
        <div className="mt-4 overflow-x-auto">
          <table className="w-full min-w-[32rem] border-separate border-spacing-0 text-sm">
            <caption className="mb-3 text-start text-ink-subtle">غربال پرسشنامه</caption>
            <thead>
              <tr>
                {["پرسش", "چرا"].map((h) => (
                  <th key={h} className="border-b border-rule px-3 py-2 text-start font-medium">
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {Q_FALLBACK.map((row) => (
                <tr key={row[0]}>
                  {row.map((cell) => (
                    <td key={cell} className="border-b border-rule/70 px-3 py-2 align-top leading-6 text-ink-muted">
                      {cell}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </main>
  );
}
