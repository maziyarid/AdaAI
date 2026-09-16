import { createFileRoute } from "@tanstack/react-router";
import { useMemo, useState, type ReactNode } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { UsefulFeedback } from "@/components/useful-feedback";
import {
  GOALS,
  INDEPENDENCE,
  PARAMETRIC,
  SCALES,
  TREE_ROWS,
  advise,
  type StatInput,
} from "@/lib/tools/stat-test";

export const Route = createFileRoute("/tools/stat-test")({ component: StatTestPage });

function StatTestPage() {
  const [input, setInput] = useState<StatInput>({
    goal: "",
    scale: "",
    independence: "",
    parametric: "",
  });
  const [submitted, setSubmitted] = useState(false);
  const result = useMemo(() => (submitted ? advise(input) : null), [submitted, input]);
  const missing = !input.goal;

  return (
    <main className="flex flex-col gap-10">
      <header className="max-w-2xl">
        <Badge tone="slate">ابزار تصمیم · نه تحلیل نهایی</Badge>
        <h1 className="mt-3 font-display text-3xl font-semibold sm:text-4xl">کدام آزمون آماری را باید در نظر بگیرم؟</h1>
        <p className="mt-3 leading-7 text-ink-muted">
          این غربال آموزشی است. جای طرح پژوهش، حجم نمونه، و تفسیر استاد را نمی گیرد. نرم افزار روش نیست. بازبین آمار هنوز
          منصوب نشده است.
        </p>
      </header>

      <form
        className="flex flex-col gap-8"
        onSubmit={(e) => {
          e.preventDefault();
          setSubmitted(true);
        }}
      >
        <Fieldset legend="هدف تحلیل چیست؟">
          {GOALS.map((g) => (
            <Radio
              key={g.id}
              name="goal"
              checked={input.goal === g.id}
              onChange={() => {
                setInput((s) => ({ ...s, goal: g.id }));
                setSubmitted(false);
              }}
              label={g.label}
            />
          ))}
        </Fieldset>
        {input.goal && input.goal !== "unsure" && input.goal !== "categorical" && input.goal !== "prediction" ? (
          <Fieldset legend="مقیاس متغیر وابسته">
            {SCALES.map((g) => (
              <Radio
                key={g.id}
                name="scale"
                checked={input.scale === g.id}
                onChange={() => {
                  setInput((s) => ({ ...s, scale: g.id }));
                  setSubmitted(false);
                }}
                label={g.label}
              />
            ))}
          </Fieldset>
        ) : null}
        {input.goal === "compare2" || input.goal === "compareK" ? (
          <Fieldset legend="آیا مشاهده ها مستقل اند؟">
            {INDEPENDENCE.map((g) => (
              <Radio
                key={g.id}
                name="independence"
                checked={input.independence === g.id}
                onChange={() => {
                  setInput((s) => ({ ...s, independence: g.id }));
                  setSubmitted(false);
                }}
                label={g.label}
              />
            ))}
          </Fieldset>
        ) : null}
        {input.goal && input.goal !== "unsure" && input.goal !== "categorical" ? (
          <Fieldset legend="مفروضات پارامتری">
            {PARAMETRIC.map((g) => (
              <Radio
                key={g.id}
                name="parametric"
                checked={input.parametric === g.id}
                onChange={() => {
                  setInput((s) => ({ ...s, parametric: g.id }));
                  setSubmitted(false);
                }}
                label={g.label}
              />
            ))}
          </Fieldset>
        ) : null}

        {submitted && missing ? (
          <p className="text-sm text-mark" role="alert">
            هدف تحلیل را انتخاب کنید.
          </p>
        ) : null}

        <div>
          <Button type="submit">پیشنهاد آزمون را ببینید</Button>
        </div>
      </form>

      {result ? (
        <section className="rounded-[24px] bg-paper-elevated p-5 shadow-[var(--shadow-border)]" aria-live="polite">
          <h2 className="font-display text-xl font-semibold">پیشنهاد غربال</h2>
          <dl className="mt-4 flex flex-col gap-3 text-sm leading-7">
            <div>
              <dt className="text-xs text-ink-subtle">نامزد</dt>
              <dd>{result.candidates}</dd>
            </div>
            <div>
              <dt className="text-xs text-ink-subtle">مفروضات</dt>
              <dd className="text-ink-muted">{result.assumptions}</dd>
            </div>
            <div>
              <dt className="text-xs text-ink-subtle">این کار را نکنید</dt>
              <dd className="text-ink-muted">{result.notThis}</dd>
            </div>
            <div>
              <dt className="text-xs text-ink-subtle">گام بعدی</dt>
              <dd>{result.next}</dd>
            </div>
            <div>
              <dt className="text-xs text-ink-subtle">حد</dt>
              <dd className="text-ink-muted">{result.hedge}</dd>
            </div>
          </dl>
        </section>
      ) : null}

      <UsefulFeedback page="/tools/stat-test" />

      <section>
        <h2 className="font-display text-2xl font-semibold">همان درخت، بدون فرم</h2>
        <p className="mt-2 max-w-2xl text-sm leading-6 text-ink-muted">
          اگر اسکریپت خاموش باشد این جدول کافی است. آستانه جادویی تجویز نمی شود.
        </p>
        <div className="mt-4 overflow-x-auto">
          <table className="w-full min-w-[36rem] border-separate border-spacing-0 text-sm">
            <caption className="mb-3 text-start text-ink-subtle">غربال آزمون های پایه</caption>
            <thead>
              <tr>
                {["وضعیت", "نامزد", "فرض"].map((h) => (
                  <th key={h} className="border-b border-rule px-3 py-2 text-start font-medium">
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {TREE_ROWS.map((row) => (
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
    <label className="flex min-h-11 cursor-pointer items-center gap-3 rounded-[12px] px-2 hover:bg-paper-sunken/80">
      <input type="radio" name={name} checked={checked} onChange={onChange} className="size-4 accent-slate" />
      <span className="text-sm leading-6">{label}</span>
    </label>
  );
}
