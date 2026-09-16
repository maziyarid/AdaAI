import type { ErrorComponentProps } from "@tanstack/react-router";
import { Link } from "@tanstack/react-router";

const FALLBACK_MESSAGE = "خطای پیش بینی نشده. صفحه را تازه کنید.";

function errorMessage(error: unknown): string {
  if (error instanceof Error && error.message) return error.message;
  if (typeof error === "string" && error) return error;
  return FALLBACK_MESSAGE;
}

export function AppErrorComponent({ error }: ErrorComponentProps) {
  return (
    <main className="mx-auto flex min-h-[70dvh] max-w-lg flex-col items-start justify-center gap-4 px-6">
      <p className="text-sm text-ink-subtle">خطای کارگاه</p>
      <h1 className="font-display text-3xl font-semibold">این صفحه الان کار نمی کند.</h1>
      <p className="text-sm leading-7 text-ink-muted break-words">{errorMessage(error)}</p>
      <Link to="/" className="text-sm text-slate hover:underline">
        بازگشت به خانه
      </Link>
    </main>
  );
}
