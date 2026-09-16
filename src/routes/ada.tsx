import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import {
  adaAuthorize,
  adaBootstrap,
  adaListMemory,
  adaQuarantine,
  adaValidateReceipt,
} from "@/lib/ada/server";
import type { AdaMemory, AdaReceipt } from "@/lib/ada/types";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/ada")({ component: AdaPage });

const AGENTS = [
  { id: "qalam-desk", label: "qalam-desk" },
  { id: "mistral-shadow", label: "mistral-shadow" },
] as const;

const TASKS = [
  { id: "web_content", label: "web_content" },
  { id: "academic_content", label: "academic_content" },
  { id: "landing_product", label: "landing_product" },
  { id: "editorial", label: "editorial" },
] as const;

type ListOut = Awaited<ReturnType<typeof adaListMemory>>;
type AuthOut = Awaited<ReturnType<typeof adaAuthorize>>;

function AdaPage() {
  const [agent, setAgent] = useState<(typeof AGENTS)[number]["id"]>("qalam-desk");
  const [task, setTask] = useState<(typeof TASKS)[number]["id"]>("web_content");
  const [busy, setBusy] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [list, setList] = useState<ListOut | null>(null);
  const [receipt, setReceipt] = useState<AdaReceipt | null>(null);
  const [validation, setValidation] = useState<{ valid: boolean; reason: string } | null>(null);
  const [auth, setAuth] = useState<Array<{ tool: string } & AuthOut>>([]);
  const [quarantineText, setQuarantineText] = useState(
    "چطور تو سه سوت پیشینه ات را بنویسی!؟ ۱۲ راز طلایی پژوهشگران برتر 👇",
  );
  const [quarantine, setQuarantine] = useState<{ id: string; quarantine_status: string } | null>(null);

  async function refreshList() {
    const out = await adaListMemory();
    setList(out);
  }

  useEffect(() => {
    let cancelled = false;
    (async () => {
      setBusy("list");
      try {
        const out = await adaListMemory();
        if (!cancelled) setList(out);
      } catch (e) {
        if (!cancelled) setError(e instanceof Error ? e.message : "بارگذاری حافظه ناموفق بود.");
      } finally {
        if (!cancelled) setBusy(null);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  async function onBootstrap() {
    setBusy("boot");
    setError(null);
    setValidation(null);
    setAuth([]);
    try {
      const out = await adaBootstrap({
        data: {
          agent_id: agent,
          task_type: task,
          project_id: "qalam",
          site_id: "teznevise.ir",
        },
      });
      setReceipt(out);
      await refreshList();
    } catch (e) {
      setError(e instanceof Error ? e.message : "bootstrap ناموفق بود.");
    } finally {
      setBusy(null);
    }
  }

  async function onValidate() {
    if (!receipt) return;
    setBusy("validate");
    setError(null);
    try {
      const out = await adaValidateReceipt({ data: { receipt_id: receipt.receipt_id } });
      setValidation(out);
    } catch (e) {
      setError(e instanceof Error ? e.message : "اعتبارسنجی ناموفق بود.");
    } finally {
      setBusy(null);
    }
  }

  async function onAuthorize(tool_name: string) {
    setBusy(`auth:${tool_name}`);
    setError(null);
    try {
      const out = await adaAuthorize({
        data: {
          agent_id: agent,
          task_type: task,
          tool_name,
          receipt_id: receipt?.receipt_id,
          site_id: "teznevise.ir",
        },
      });
      setAuth((prev) => [{ tool: tool_name, ...out }, ...prev.filter((a) => a.tool !== tool_name)]);
    } catch (e) {
      setError(e instanceof Error ? e.message : "مجوز ناموفق بود.");
    } finally {
      setBusy(null);
    }
  }

  async function onQuarantine() {
    setBusy("quarantine");
    setError(null);
    try {
      const out = await adaQuarantine({
        data: {
          source_kind: "telegram_public",
          content_text: quarantineText,
          source_uri: "t.me/s/example",
        },
      });
      setQuarantine(out);
    } catch (e) {
      setError(e instanceof Error ? e.message : "قرنطینه ناموفق بود.");
    } finally {
      setBusy(null);
    }
  }

  const memories = receipt?.mandatory_memory ?? list?.memories ?? [];
  const iranian = memories.find((m) => m.canonical_key === "writing.iranian-not-dari");

  return (
    <main className="flex flex-col gap-10">
      <header className="max-w-2xl">
        <Badge tone="slate">Ada Context Core · v0.2</Badge>
        <h1 className="mt-3 font-display text-3xl font-semibold sm:text-4xl">حافظه قطعی، نه شباهت.</h1>
        <p className="mt-3 leading-7 text-ink-muted">
          قبل از نگارش پیامددار، عامل باید بسته زمینه را با دامنه دقیق بار کند. جستجوی معنایی این لایه را عوض نمی کند.
          پایگاه آماده است؛ ورود حساب نیست؛ ردیف ها مالک شخصی ندارند.
        </p>
      </header>

      <section className="grid gap-3 sm:grid-cols-3">
        {[
          { t: "P0/P1 دامنه دار", d: "global، پروژه، سایت، نوع کار، عامل — نه embedding." },
          { t: "رسید امضاشده", d: "HMAC در پیش نمایش. نسخه دامنه کهنه کار را می بندد." },
          { t: "اسکرپ قرنطینه", d: "UNTRUSTED_EXTERNAL تا بازبینی. سیاست نمی شود." },
        ].map((c) => (
          <article key={c.t} className="rounded-[20px] bg-paper-elevated p-4 shadow-[var(--shadow-border)]">
            <h2 className="font-display text-lg font-semibold">{c.t}</h2>
            <p className="mt-2 text-sm leading-6 text-ink-muted">{c.d}</p>
          </article>
        ))}
      </section>

      {error ? (
        <p className="rounded-[16px] bg-mark/10 px-4 py-3 text-sm leading-6 text-mark" role="alert">
          {error}
        </p>
      ) : null}

      {list?.preview_hmac || receipt?.preview_hmac ? (
        <p className="rounded-[16px] bg-warn/12 px-4 py-3 text-sm leading-6 text-warn">
          کلید HMAC پیش نمایش است و برای تولید نیست. کلید واقعی در محیط جدا می ماند؛ اینجا فایل .env نوشته نمی شود.
        </p>
      ) : null}

      <section className="rounded-[24px] bg-paper-elevated p-5 shadow-[var(--shadow-border)] sm:p-6">
        <h2 className="font-display text-xl font-semibold">bootstrap</h2>
        <p className="mt-2 max-w-2xl text-sm leading-7 text-ink-muted">
          عامل و نوع کار را انتخاب کنید. حافظه اجباری همان دامنه برمی گردد، همراه رسید و وضعیت پروژه qalam/main.
        </p>
        <div className="mt-4 flex flex-col gap-4">
          <fieldset className="flex flex-col gap-2">
            <legend className="text-sm text-ink-muted">عامل</legend>
            <div className="flex flex-wrap gap-2">
              {AGENTS.map((a) => (
                <button
                  key={a.id}
                  type="button"
                  onClick={() => setAgent(a.id)}
                  className={cn(
                    "h-11 rounded-full px-4 text-sm",
                    agent === a.id ? "bg-slate text-slate-fg" : "bg-paper-sunken text-ink-muted",
                  )}
                >
                  {a.label}
                </button>
              ))}
            </div>
          </fieldset>
          <fieldset className="flex flex-col gap-2">
            <legend className="text-sm text-ink-muted">نوع کار</legend>
            <div className="flex flex-wrap gap-2">
              {TASKS.map((t) => (
                <button
                  key={t.id}
                  type="button"
                  onClick={() => setTask(t.id)}
                  className={cn(
                    "h-11 rounded-full px-4 text-sm",
                    task === t.id ? "bg-slate text-slate-fg" : "bg-paper-sunken text-ink-muted",
                  )}
                >
                  {t.label}
                </button>
              ))}
            </div>
          </fieldset>
          <div className="flex flex-wrap gap-2">
            <Button onClick={onBootstrap} disabled={busy !== null}>
              {busy === "boot" ? "در حال بارگذاری…" : "بسته زمینه"}
            </Button>
            <Button variant="secondary" onClick={onValidate} disabled={!receipt || busy !== null}>
              اعتبار رسید
            </Button>
          </div>
        </div>

        {receipt ? (
          <dl className="mt-5 grid gap-3 sm:grid-cols-2">
            <Item k="شناسه رسید" v={receipt.receipt_id} mono />
            <Item k="انقضا" v={receipt.expires_at} />
            <Item k="آزادسازی قلم" v={receipt.qalam_release ?? "—"} />
            <Item k="گذرنامه" v={receipt.passport?.agent_id ?? "ندارد"} />
            <Item k="وضعیت پروژه" v={receipt.project_state?.verified_status ?? "—"} />
            <Item k="حافظه اجباری" v={String(receipt.mandatory_memory.length)} />
          </dl>
        ) : null}

        {validation ? (
          <p className="mt-4 text-sm">
            اعتبار رسید:{" "}
            <Badge tone={validation.valid ? "ok" : "mark"}>{validation.valid ? "معتبر" : validation.reason}</Badge>
          </p>
        ) : null}

        {iranian ? (
          <article className="mt-5 rounded-[16px] bg-ok/10 p-4">
            <p className="text-xs text-ok">P0 الزامی · {iranian.canonical_key}</p>
            <h3 className="mt-1 font-display text-lg font-semibold">{iranian.title}</h3>
            <p className="mt-2 text-sm leading-7">{iranian.content}</p>
          </article>
        ) : null}
      </section>

      <section>
        <h2 className="font-display text-2xl font-semibold">حافظه اجباری این بسته</h2>
        <p className="mt-2 max-w-2xl text-sm leading-7 text-ink-muted">
          اگر بسته هنوز ساخته نشده، فهرست فعال کل پایگاه دیده می شود. کلید writing.iranian-not-dari باید در کارهای جهانی باشد.
        </p>
        <ul className="mt-4 flex flex-col gap-3">
          {memories.length === 0 && busy === "list" ? (
            <li className="text-sm text-ink-muted">در حال خواندن جدول ها…</li>
          ) : (
            memories.map((m) => <MemoryCard key={m.id} memory={m} highlight={Boolean(receipt)} />)
          )}
        </ul>
      </section>

      <section className="rounded-[24px] bg-paper-elevated p-5 shadow-[var(--shadow-border)] sm:p-6">
        <h2 className="font-display text-xl font-semibold">مجوز ابزار</h2>
        <p className="mt-2 text-sm leading-7 text-ink-muted">
          qalam-desk فقط خواندن دارد. انتشار باید رد یا به تصویب برود. مدل پیشنهاد می دهد؛ این لایه تصمیم می گیرد.
        </p>
        <div className="mt-4 flex flex-wrap gap-2">
          <Button variant="secondary" onClick={() => onAuthorize("ada_memory_read")} disabled={busy !== null}>
            ada_memory_read
          </Button>
          <Button variant="secondary" onClick={() => onAuthorize("wp_read")} disabled={busy !== null}>
            wp_read
          </Button>
          <Button variant="ghost" onClick={() => onAuthorize("wp_publish")} disabled={busy !== null}>
            wp_publish
          </Button>
        </div>
        {auth.length ? (
          <ul className="mt-4 flex flex-col gap-2">
            {auth.map((a) => (
              <li key={a.tool} className="flex flex-wrap items-center gap-2 text-sm">
                <span className="font-mono text-xs">{a.tool}</span>
                <Badge tone={a.decision === "ALLOW" ? "ok" : a.decision === "ESCALATE" ? "warn" : "mark"}>
                  {a.decision}
                </Badge>
                <span className="text-ink-muted">{a.reason}</span>
              </li>
            ))}
          </ul>
        ) : null}
      </section>

      <section className="rounded-[24px] bg-paper-sunken/70 p-5 sm:p-6">
        <h2 className="font-display text-xl font-semibold">قرنطینه ورودی بیرونی</h2>
        <p className="mt-2 text-sm leading-7 text-ink-muted">
          متن تلگرام یا خبر صنعت خودش سیاست نگارش نمی شود. اینجا فقط قرنطینه می شود.
        </p>
        <Textarea
          dir="rtl"
          className="mt-3 min-h-[120px]"
          value={quarantineText}
          onChange={(e) => setQuarantineText(e.target.value)}
          aria-label="متن مشکوک برای قرنطینه"
        />
        <div className="mt-3">
          <Button variant="secondary" onClick={onQuarantine} disabled={busy !== null || !quarantineText.trim()}>
            قرنطینه کن
          </Button>
        </div>
        {quarantine ? (
          <p className="mt-3 text-sm">
            <Badge tone="warn">{quarantine.quarantine_status}</Badge>{" "}
            <span className="font-mono text-xs text-ink-subtle">{quarantine.id}</span>
          </p>
        ) : null}
      </section>

      {list ? (
        <section className="grid gap-4 lg:grid-cols-2">
          <article className="rounded-[24px] bg-paper-elevated p-5 shadow-[var(--shadow-border)]">
            <h2 className="font-display text-xl font-semibold">ابزارها</h2>
            <ul className="mt-3 flex flex-col gap-2 text-sm">
              {list.tools.map((t) => (
                <li key={t.tool_name} className="flex flex-wrap items-center justify-between gap-2">
                  <span className="font-mono text-xs">{t.tool_name}</span>
                  <span className="text-ink-muted">
                    {t.side_effect_class} · {t.default_decision}
                  </span>
                </li>
              ))}
            </ul>
          </article>
          <article className="rounded-[24px] bg-paper-elevated p-5 shadow-[var(--shadow-border)]">
            <h2 className="font-display text-xl font-semibold">گذرنامه و وضعیت</h2>
            <ul className="mt-3 flex flex-col gap-2 text-sm">
              {list.passports.map((p) => (
                <li key={p.id}>
                  <span className="font-medium">{p.agent_id}</span>
                  <span className="text-ink-muted"> · {p.task_type} · {p.allowed_tools.join("، ")}</span>
                </li>
              ))}
            </ul>
            {list.state ? (
              <p className="mt-4 text-sm leading-7 text-ink-muted">
                {list.state.objective} — {list.state.next_action}
              </p>
            ) : null}
            <p className="mt-2 text-xs text-ink-subtle">آزادسازی قلم {list.qalam_release ?? "—"}</p>
          </article>
        </section>
      ) : null}

      <section className="max-w-2xl text-sm leading-7 text-ink-muted">
        <h2 className="font-display text-lg font-semibold text-ink">حد این فاز</h2>
        <p className="mt-2">
          pgvector و استنتاج مدل اینجا نیست. برش های B و C و G و پیکره نویسندگان نام دار در این بسته ضمیمه نبودند و جعل
          نشدند. سایت زنده teznevise.ir منتشر نشد.
        </p>
      </section>
    </main>
  );
}

function MemoryCard({ memory, highlight }: { memory: AdaMemory; highlight: boolean }) {
  return (
    <li className="rounded-[20px] bg-paper-elevated p-4 shadow-[var(--shadow-border)]">
      <div className="flex flex-wrap items-center gap-2">
        <span className="font-mono text-xs text-ink-subtle">{memory.canonical_key}</span>
        <Badge tone={memory.priority === 0 ? "ok" : "slate"}>P{memory.priority}</Badge>
        <span className="text-xs text-ink-subtle">
          {memory.scope_type}:{memory.scope_id}
        </span>
        {highlight && memory.priority <= 1 ? <Badge tone="ink">در بسته</Badge> : null}
      </div>
      <h3 className="mt-2 font-medium">{memory.title}</h3>
      <p className="mt-1 text-sm leading-7 text-ink-muted">{memory.summary ?? memory.content}</p>
    </li>
  );
}

function Item({ k, v, mono }: { k: string; v: string; mono?: boolean }) {
  return (
    <div className="rounded-[12px] bg-paper-sunken/70 px-3 py-2">
      <dt className="text-xs text-ink-subtle">{k}</dt>
      <dd className={cn("mt-0.5 text-sm leading-6 break-all", mono && "font-mono text-xs")}>{v}</dd>
    </div>
  );
}
