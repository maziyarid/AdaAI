export type FeasInput = {
  data: "have" | "access" | "unknown" | "none" | "";
  method: "known" | "learnable" | "new" | "";
  time: "gt12" | "6to12" | "lt6" | "";
  ethics: "none_needed" | "in_progress" | "not_started" | "";
  supervisor: "aligned" | "unclear" | "opposed" | "";
};

export type Flag = {
  level: "stop" | "risk" | "ok";
  title: string;
  detail: string;
  ask: string;
};

export const DATA_OPTS = [
  { id: "have", label: "داده یا منبع در دست است" },
  { id: "access", label: "دسترسی محتمل است اما هنوز نگرفته ام" },
  { id: "unknown", label: "نمی دانم داده اصلا وجود دارد" },
  { id: "none", label: "می دانم داده در زمان من در دسترس نیست" },
] as const;

export const METHOD_OPTS = [
  { id: "known", label: "روش را بلدم یا مشاور روش دارم" },
  { id: "learnable", label: "روش تازه است اما در زمان باقی مانده آموختنی است" },
  { id: "new", label: "روش برایم ناشناخته است و استاد هم تخصصش را ندارد" },
] as const;

export const TIME_OPTS = [
  { id: "gt12", label: "بیش از دوازده ماه تا دفاع" },
  { id: "6to12", label: "شش تا دوازده ماه" },
  { id: "lt6", label: "کمتر از شش ماه" },
] as const;

export const ETHICS_OPTS = [
  { id: "none_needed", label: "داده عمومی یا بدون آزمودنی انسان" },
  { id: "in_progress", label: "مسیر اخلاق شروع شده" },
  { id: "not_started", label: "آزمودنی انسان یا داده حساس است و هنوز اقدام نشده" },
] as const;

export const SUPER_OPTS = [
  { id: "aligned", label: "استاد با سؤال و روش همراه است" },
  { id: "unclear", label: "هنوز معلوم نیست استاد این طرح را می پذیرد" },
  { id: "opposed", label: "استاد صریحا مخالف یا خارج از تخصص اعلام کرده" },
] as const;

export const FALLBACK_ROWS = [
  ["داده در دسترس نیست", "موضوع را عوض کنید یا منبع جایگزین تعریف کنید", "بدون داده طرح شدنی نیست"],
  ["روش ناشناخته برای دانشجو و استاد", "روش را ساده کنید یا مشاور روش بیاورید", "نرم افزار روش نمی سازد"],
  ["کمتر از شش ماه و روش تازه", "دامنه را ببرید", "زمان با یادگیری روش جمع نمی شود مگر طرح کوچک شود"],
  ["اخلاق شروع نشده و آزمودنی انسان", "قبل از گردآوری اقدام کنید", "داده بدون مجوز ممکن است غیرقابل استفاده شود"],
  ["استاد مخالف", "طرح را با استاد بازنویسی کنید", "این غربال جای جلسه استاد را نمی گیرد"],
];

export function screenFeasibility(input: FeasInput): Flag[] | null {
  if (!input.data || !input.method || !input.time || !input.ethics || !input.supervisor) return null;
  const flags: Flag[] = [];

  if (input.data === "none") {
    flags.push({
      level: "stop",
      title: "منبع داده در زمان شما نیست",
      detail: "موضوع با این منبع در این پنجره زمانی شدنی نیست.",
      ask: "اگر منبع جایگزین ندارید، سؤال را عوض کنید نه اینکه امیدوار بمانید.",
    });
  } else if (input.data === "unknown") {
    flags.push({
      level: "stop",
      title: "وجود داده معلوم نیست",
      detail: "تا وجود منبع ثابت نشود طرح را قفل نکنید.",
      ask: "از استاد بپرسید: این داده کجاست، مال کیست، و تا کی در دسترس است؟",
    });
  } else if (input.data === "access") {
    flags.push({
      level: "risk",
      title: "دسترسی هنوز گرفته نشده",
      detail: "وعده دسترسی داده نیست.",
      ask: "نامه، مجوز، یا مالک داده را قبل از تصویب نهایی بگیرید.",
    });
  } else {
    flags.push({
      level: "ok",
      title: "منبع داده ادعا شده در دست است",
      detail: "باز هم کدبوک و کیفیت را جدا چک کنید.",
      ask: "یک نمونه واقعی از رکورد را به استاد نشان دهید.",
    });
  }

  if (input.method === "new") {
    flags.push({
      level: "stop",
      title: "روش برای شما و استاد ناشناخته است",
      detail: "این ترکیب معمولا در یک پایان نامه آموزشی نمی گنجد.",
      ask: "روش را به چیزی که در گروه هست برگردانید، یا مشاور روش با مسئولیت روشن بیاورید.",
    });
  } else if (input.method === "learnable" && input.time === "lt6") {
    flags.push({
      level: "risk",
      title: "روش تازه در پنجره کوتاه",
      detail: "یادگیری روش و اجرای پژوهش در کمتر از شش ماه با هم جا نمی شود مگر دامنه خیلی کوچک شود.",
      ask: "کدام بخش طرح حذف شود تا روش آموختنی بماند؟",
    });
  } else if (input.method === "learnable") {
    flags.push({
      level: "risk",
      title: "روش آموختنی است نه آماده",
      detail: "زمان یادگیری باید در جدول پروژه بیاید.",
      ask: "منبع آموزش روش و کسی که خروجی را بازبینی می کند کیست؟",
    });
  }

  if (input.ethics === "not_started") {
    flags.push({
      level: "stop",
      title: "اخلاق شروع نشده",
      detail: "گردآوری از آزمودنی یا داده حساس بدون مسیر اخلاق، طرح را شکننده می کند.",
      ask: "آیین نامه دانشگاه شما برای این داده چیست و فرم از کی باید برود؟",
    });
  } else if (input.ethics === "in_progress" && input.time === "lt6") {
    flags.push({
      level: "risk",
      title: "اخلاق در جریان و زمان کم",
      detail: "تأخیر کمیته روی دفاع اثر می گذارد.",
      ask: "تاریخ جلسه کمیته را بپرسید و برنامه بدون داده حساس داشته باشید.",
    });
  }

  if (input.supervisor === "opposed") {
    flags.push({
      level: "stop",
      title: "استاد همراه نیست",
      detail: "غربال ما جای مخالفت استاد را عوض نمی کند.",
      ask: "طرح بدیل داخل تخصص استاد چیست؟",
    });
  } else if (input.supervisor === "unclear") {
    flags.push({
      level: "risk",
      title: "همراهی استاد معلوم نیست",
      detail: "قبل از سرمایه گذاری روی ابزار و داده یک جلسه کوتاه کافی است.",
      ask: "یک صفحه سؤال، داده، روش، و حد را ببرید نه یک پروپوزال کامل.",
    });
  }

  if (input.time === "lt6" && input.data !== "have") {
    flags.push({
      level: "risk",
      title: "زمان کم و داده هنوز کامل نیست",
      detail: "پنجره دفاع با گردآوری تازه معمولا نمی خواند.",
      ask: "آیا داده آرشیوی داخل همان سؤال هست؟",
    });
  }

  if (!flags.some((f) => f.level === "stop") && !flags.some((f) => f.level === "risk")) {
    flags.push({
      level: "ok",
      title: "این غربال پرچم ایست نداده",
      detail: "یعنی مانع آشکار در این پنج سؤال نیست. شدنی بودن نهایی با استاد و آیین نامه است.",
      ask: "حالا دامنه را یک جمله کنید و فایل داده را نشان دهید.",
    });
  }

  return flags;
}
