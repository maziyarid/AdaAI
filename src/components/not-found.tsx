import { Link } from "@tanstack/react-router";
import { Button } from "@/components/ui/button";

export function NotFound() {
  return (
    <main className="flex min-h-[60dvh] max-w-lg flex-col justify-center gap-5">
      <p className="text-sm text-ink-subtle">صفحه پیدا نشد</p>
      <h1 className="font-display text-3xl font-semibold sm:text-4xl">این نشانی در کارگاه نیست.</h1>
      <p className="leading-7 text-ink-muted">
        شاید پیوند کهنه باشد. میز ویرایش، کارخانه، یا انتخاب آزمون را امتحان کنید.
      </p>
      <div className="flex flex-wrap gap-3">
        <Link to="/">
          <Button>خانه</Button>
        </Link>
        <Link to="/desk">
          <Button variant="secondary">میز ویرایش</Button>
        </Link>
        <Link to="/factory">
          <Button variant="secondary">کارخانه</Button>
        </Link>
      </div>
    </main>
  );
}
