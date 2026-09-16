import { createFileRoute } from "@tanstack/react-router";
import { useMemo, useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ORIGINAL_VALUE_KINDS } from "@/lib/seo/data";

export const Route = createFileRoute("/factory/intake")({ component: IntakePage });

const KINDS = [
  { id: "FIRST_PARTY_OBSERVATION", label: "مشاهده دست اول" },
  { id: "FIRST_PARTY_DATA", label: "داده دست اول" },
  { id: "FIRST_PARTY_EXPERIMENT", label: "آزمایش دست اول" },
  { id: "EDITORIAL_INTERPRETATION", label: "تفسیر تحریریه" },
  { id: "ANECDOTE", label: "حکایت" },
] as const;

type Note = {
  kind: string;
  topic: string;
  observation: string;
  cannotPromoteTo: string;
  at: string;
};

function loadNotes(): Note[] {
  try {
    return JSON.parse(localStorage.getItem("qalam-experience-intake") || "[]") as Note[];
  } catch {
    return [];
  }
}

function IntakePage() {
  const [kind, setKind] = useState<string>("FIRST_PARTY_OBSERVATION");
  const [topic, setTopic] = useState("");
  const [observation, setObservation] = useState("");
  const [cannot, setCannot] = useState("");
  const [notes, setNotes] = useState<Note[]>(() => (typeof window === "undefined" ? [] : loadNotes()));
  const [values, setValues] = useState<string[]>([]);
  const [intent, setIntent] = useState("");
  const [gate, setGate] = useState<string | null>(null);

  const ready = topic.trim() && observation.trim() && cannot.trim();

  const gateOk = useMemo(() => values.length > 0 && intent.trim().length > 8, [values, intent]);

  function saveNote() {
    if (!ready) return;
    const next: Note = {
      kind,
      topic: topic.trim(),
      observation: observation.trim(),
      cannotPromoteTo: cannot.trim(),
      at: new Date().toISOString(),
    };
    const all = [...notes, next].slice(-40);
    setNotes(all);
    try {
      localStorage.setItem("qalam-experience-intake", JSON.stringify(all));
    } catch {
      /* quota */
    }
    setTopic("");
    setObservation("");
    setCannot("");
  }

  function runGate() {
    if (!gateOk) {
      setGate("نشانی تازه بدون ارزش افزوده نام برده و نیت مشخص تصویب نمی شود.");
      return;
    }
    setGate(
      "این فقط غربال کارخانه است. اگر مالک کانونی برای همین نیت هست، همان را تازه کنید. حکایت تلگرام هنوز صفحه نیست.",
    );
  }

  return (
    <main className="flex flex-col gap-10">
      <header className="max-w-2xl">
        <Badge tone="slate">تجربه دست اول · محرمانه بماند</Badge>
        <h1 className="mt-3 font-display text-3xl font-semibold sm:text-4xl">حکایت قانون سایت نمی شود.</h1>
        <p className="mt-3 leading-7 text-ink-muted">
          پرونده دانشجو اینجا ننویسید. مشاهده را طبقه بندی کنید. داده فقط روی همین دستگاه می ماند؛ سیگنال محصول است نه فاکتور
          گوگل.
        </p>
      </header>

      <section className="rounded-[24px] bg-paper-elevated p-5 shadow-[var(--shadow-border)]">
        <h2 className="font-display text-xl font-semibold">یادداشت تجربه</h2>
        <fieldset className="mt-4">
          <legend className="text-sm font-medium">طبقه</legend>
          <div className="mt-2 flex flex-col gap-2">
            {KINDS.map((k) => (
              <label key={k.id} className="flex min-h-11 items-center gap-2 text-sm">
                <input
                  type="radio"
                  name="kind"
                  checked={kind === k.id}
                  onChange={() => setKind(k.id)}
                  className="accent-slate"
                />
                {k.label}
              </label>
            ))}
          </div>
        </fieldset>
        <label className="mt-4 block text-sm">
          موضوع
          <input
            className="mt-1 h-11 w-full rounded-[12px] bg-paper-sunken px-3"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
          />
        </label>
        <label className="mt-3 block text-sm">
          مشاهده
          <textarea
            className="mt-1 min-h-28 w-full rounded-[12px] bg-paper-sunken p-3"
            value={observation}
            onChange={(e) => setObservation(e.target.value)}
          />
        </label>
        <label className="mt-3 block text-sm">
          به چه قانونی ارتقا داده نشود
          <input
            className="mt-1 h-11 w-full rounded-[12px] bg-paper-sunken px-3"
            value={cannot}
            onChange={(e) => setCannot(e.target.value)}
          />
        </label>
        <div className="mt-4">
          <Button onClick={saveNote} disabled={!ready}>
            یادداشت را نگه دارید
          </Button>
        </div>
      </section>

      <section>
        <h2 className="font-display text-xl font-semibold">یادداشت های همین دستگاه</h2>
        {notes.length === 0 ? (
          <p className="mt-3 text-sm text-ink-muted">هنوز یادداشتی نیست.</p>
        ) : (
          <ul className="mt-3 flex flex-col gap-2">
            {notes
              .slice()
              .reverse()
              .map((n, i) => (
                <li key={`${n.at}-${i}`} className="rounded-[16px] bg-paper-sunken/70 p-4 text-sm leading-6">
                  <Badge>{n.kind}</Badge>
                  <p className="mt-2 font-medium">{n.topic}</p>
                  <p className="text-ink-muted">{n.observation}</p>
                  <p className="mt-1 text-xs text-ink-subtle">ارتقا نه: {n.cannotPromoteTo}</p>
                </li>
              ))}
          </ul>
        )}
      </section>

      <section className="rounded-[24px] bg-paper-elevated p-5 shadow-[var(--shadow-border)]">
        <h2 className="font-display text-xl font-semibold">درگاه ارزش افزوده برای نشانی تازه</h2>
        <p className="mt-2 text-sm leading-6 text-ink-muted">
          خلاصه وب کافی نیست. حداقل یک دلیل واقعی. حجم جستجو دلیل وجود صفحه نیست.
        </p>
        <label className="mt-4 block text-sm">
          نیت کاربر به یک جمله
          <input
            className="mt-1 h-11 w-full rounded-[12px] bg-paper-sunken px-3"
            value={intent}
            onChange={(e) => setIntent(e.target.value)}
          />
        </label>
        <fieldset className="mt-4">
          <legend className="text-sm font-medium">ارزش اصلی (حداقل یکی)</legend>
          <div className="mt-2 grid gap-2 sm:grid-cols-2">
            {ORIGINAL_VALUE_KINDS.map((v) => (
              <label key={v.id} className="flex min-h-11 items-center gap-2 text-sm">
                <input
                  type="checkbox"
                  className="accent-slate"
                  checked={values.includes(v.id)}
                  onChange={() =>
                    setValues((s) => (s.includes(v.id) ? s.filter((x) => x !== v.id) : [...s, v.id]))
                  }
                />
                {v.label}
              </label>
            ))}
          </div>
        </fieldset>
        <div className="mt-4">
          <Button onClick={runGate}>غربال نشانی تازه</Button>
        </div>
        {gate ? (
          <p className="mt-3 text-sm leading-7" role="status">
            {gate}
          </p>
        ) : null}
      </section>
    </main>
  );
}
