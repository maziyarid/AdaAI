import { createFileRoute } from "@tanstack/react-router";
import { useMemo, useState, type ReactNode } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { UsefulFeedback } from "@/components/useful-feedback";
import {
  DATA_OPTS,
  ETHICS_OPTS,
  FALLBACK_ROWS,
  METHOD_OPTS,
  SUPER_OPTS,
  TIME_OPTS,
  screenFeasibility,
  type FeasInput,
} from "@/lib/tools/feasibility";

export const Route = createFileRoute("/tools/feasibility")({ component: FeasibilityPage });

function FeasibilityPage() {
  const [input, setInput] = useState<FeasInput>({
    data: "",
    method: "",
    time: "",
    ethics: "",
    supervisor: "",
  });
  const [submitted, setSubmitted] = useState(false);
  const flags = useMemo(() => (submitted ? screenFeasibility(input) : null), [submitted, input]);
  const missing = submitted && !flags;

  return (
    <main className="flex flex-col gap-10">
      <header className="max-w-2xl">
        <Badge tone="slate">غربال · نه نمره امکان</Badge>
        <h1 className="mt-3 font-display text-3xl font-semibold sm:text-4xl">آیا این موضوع در زمان من شدنی است؟</h1>
        <p className="mt-3 leading-7 text-ink-muted">
          پرچم خطر است. درصد امکان ساخته نمی شود. جای استاد راهنما و آیین نامه دانشگاه را نمی گیرد.
        </p>
      </header>

      <form
        className="flex flex-col gap-6"
        onSubmit={(e) => {
          e.preventDefault();
          setSubmitted(true);
        }}
      >
        <Fieldset legend="دسترسی به داده">
          {DATA_OPTS.map((g) => (
            <Radio
              key={g.id}
              name="data"
              checked={input.data === g.id}
              onChange={() => {
                setInput((s) => ({ ...s, data: g.id }));
                setSubmitted(false);
              }}
              label={g.label}
            />
          ))}
        </Fieldset>
        <Fieldset legend="مهارت روش">
          {METHOD_OPTS.map((g) => (
            <Radio
              key={g.id}
              name="method"
              checked={input.method === g.id}
              onChange={() => {
                setInput((s) => ({ ...s, method: g.id }));
                setSubmitted(false);
              }}
              label={g.label}
            />
          ))}
        </Fieldset>
        <Fieldset legend="زمان تا دفاع">
          {TIME_OPTS.map((g) => (
            <Radio
              key={g.id}
              name="time"
              checked={input.time === g.id}
              onChange={() => {
                setInput((s) => ({ ...s, time: g.id }));
                setSubmitted(false);
              }}
              label={g.label}
            />
          ))}
        </Fieldset>
        <Fieldset legend="اخلاق پژوهش">
          {ETHICS_OPTS.map((g) => (
            <Radio
              key={g.id}
              name="ethics"
              checked={input.ethics === g.id}
              onChange={() => {
                setInput((s) => ({ ...s, ethics: g.id }));
                setSubmitted(false);
              }}
              label={g.label}
            />
          ))}
        </Fieldset>
        <Fieldset legend="همراهی استاد">
          {SUPER_OPTS.map((g) => (
            <Radio
              key={g.id}
              name="supervisor"
              checked={input.supervisor === g.id}
              onChange={() => {
                setInput((s) => ({ ...s, supervisor: g.id }));
                setSubmitted(false);
              }}
              label={g.label}
            />
          ))}
        </Fieldset>
        {missing ? (
          <p className="text-sm text-mark" role="alert">
            هر پنج پرسش را پاسخ دهید.
          </p>
        ) : null}
        <div>
          <Button type="submit">پرچم ها را ببینید</Button>
        </div>
      </form>

      {flags ? (
        <section className="flex flex-col gap-3" aria-live="polite">
          <h2 className="font-display text-xl font-semibold">نتیجه غربال</h2>
          {flags.map((f) => (
            <article
              key={f.title}
              className="rounded-[20px] bg-paper-elevated p-4 shadow-[var(--shadow-border)]"
            >
              <Badge tone={f.level === "stop" ? "mark" : f.level === "risk" ? "warn" : "ok"}>
                {f.level === "stop" ? "ایست" : f.level === "risk" ? "خطر" : "مانع آشکار نیست"}
              </Badge>
              <h3 className="mt-2 font-medium">{f.title}</h3>
              <p className="mt-1 text-sm leading-7 text-ink-muted">{f.detail}</p>
              <p className="mt-2 text-sm leading-7">از استاد بپرسید: {f.ask}</p>
            </article>
          ))}
        </section>
      ) : null}

      <UsefulFeedback page="/tools/feasibility" />

      <section>
        <h2 className="font-display text-2xl font-semibold">همان غربال، بدون فرم</h2>
        <div className="mt-4 overflow-x-auto">
          <table className="w-full min-w-[36rem] border-separate border-spacing-0 text-sm">
            <caption className="mb-3 text-start text-ink-subtle">پرچم های رایج امکان سنجی</caption>
            <thead>
              <tr>
                {["وضعیت", "کار", "چرا"].map((h) => (
                  <th key={h} className="border-b border-rule px-3 py-2 text-start font-medium">
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {FALLBACK_ROWS.map((row) => (
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

function Fieldset({ legend, children }: { legend: string; children: ReactNode }) {
  return (
    <fieldset className="rounded-[20px] bg-paper-elevated p-4 shadow-[var(--shadow-border)]">
      <legend className="px-1 text-sm font-medium">{legend}</legend>
      <div className="mt-3 flex flex-col gap-2">{children}</div>
    </fieldset>
  );
}

function Radio({
  name,
  checked,
  onChange,
  label,
}: {
  name: string;
  checked: boolean;
  onChange: () => void;
  label: string;
}) {
  return (
    <label className="flex min-h-11 cursor-pointer items-start gap-3 rounded-[12px] px-1 py-1 hover:bg-paper-sunken/70">
      <input type="radio" name={name} checked={checked} onChange={onChange} className="mt-1 accent-slate" />
      <span className="text-sm leading-6">{label}</span>
    </label>
  );
}
