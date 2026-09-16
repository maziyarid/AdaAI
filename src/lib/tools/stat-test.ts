export type Goal = "compare2" | "compareK" | "paired" | "association" | "prediction" | "categorical" | "unsure";
export type Scale = "continuous" | "ordinal" | "binary" | "count";
export type Independence = "independent" | "paired" | "unknown";
export type Parametric = "ok" | "no" | "unknown";

export type StatInput = {
  goal: Goal | "";
  scale: Scale | "";
  independence: Independence | "";
  parametric: Parametric | "";
};

export type StatResult = {
  candidates: string;
  assumptions: string;
  notThis: string;
  next: string;
  hedge: string;
};

export const GOALS: { id: Goal; label: string }[] = [
  { id: "compare2", label: "مقایسه میانگین یا توزیع دو گروه جدا" },
  { id: "compareK", label: "مقایسه سه گروه یا بیشتر" },
  { id: "paired", label: "دو اندازه از همان واحد (قبل/بعد)" },
  { id: "association", label: "ارتباط دو متغیر پیوسته یا رتبه ای" },
  { id: "prediction", label: "پیش بینی یک متغیر از روی چند پیش بین" },
  { id: "categorical", label: "ارتباط دو متغیر رده ای" },
  { id: "unsure", label: "هنوز سؤال پژوهش به این شکل درنیامده" },
];

export const SCALES: { id: Scale; label: string }[] = [
  { id: "continuous", label: "وابسته پیوسته (نمره، زمان، مقدار)" },
  { id: "ordinal", label: "رتبه ای (لیکرت بدون توجیه فاصله)" },
  { id: "binary", label: "دو حالتی" },
  { id: "count", label: "شمارشی" },
];

export const INDEPENDENCE: { id: Independence; label: string }[] = [
  { id: "independent", label: "هر مشاهده یک واحد جدا است" },
  { id: "paired", label: "تکرار روی همان واحد یا جفت همسان" },
  { id: "unknown", label: "نمی دانم" },
];

export const PARAMETRIC: { id: Parametric; label: string }[] = [
  { id: "ok", label: "مفروضات پارامتری محتمل است یا قابل بررسی است" },
  { id: "no", label: "نقض جدی نرمال یا واریانس، یا مقیاس رتبه ای سخت" },
  { id: "unknown", label: "هنوز داده ندیده ام" },
];

export const TREE_ROWS = [
  ["دو گروه مستقل، وابسته پیوسته، پارامتری", "آزمون t مستقل", "نرمال بودن مانده، همگنی واریانس، استقلال"],
  ["دو گروه مستقل، رتبه ای یا نقض پارامتری", "من ویتنی", "استقلال؛ توزیع مشابه شکل اگر میانه تفسیر می شود"],
  ["قبل و بعد روی همان واحد", "t زوجی یا ویلکاکسون", "وابستگی جفت؛ تفاوت ها برای t"],
  ["سه گروه یا بیشتر مستقل، پارامتری", "ANOVA یک راهه سپس مقایسه برنامه ریزی شده", "نرمال مانده، همگنی، استقلال؛ آزمون تعقیبی بی برنامه نه"],
  ["سه گروه، رتبه ای یا نقض", "کروسکال والیس", "استقلال"],
  ["دو پیوسته، ارتباط", "پیرسون یا اسپیرمن", "خطی بودن برای پیرسون؛ علیت از همبستگی درنمی آید"],
  ["پیش بینی پیوسته", "رگرسیون خطی (شروع)", "مانده، هم خطی، مشخص بودن مدل"],
  ["دو رده ای", "خی دو یا فیشر", "فراوانی مورد انتظار؛ طرح نمونه"],
  ["شمارشی", "این درخت کافی نیست", "پواسون / دوجمله ای منفی نیاز طراحی جدا دارد"],
];

export function advise(input: StatInput): StatResult | null {
  if (!input.goal) return null;
  if (input.goal === "unsure") {
    return {
      candidates: "هنوز آزمون انتخاب نکنید.",
      assumptions: "اول سؤال، واحد تحلیل، و طرح. نرم افزار روش نیست.",
      notThis: "گشتن منوی SPSS برای پیدا کردن آزمون.",
      next: "سؤال را یک جمله کنید: چه را در چه واحدی با چه مقایسه ای می خواهید بدانید.",
      hedge: "این غربال آموزشی است نه نسخه تحلیل.",
    };
  }
  if (input.goal === "categorical") {
    return {
      candidates: "آزمون خی دو استقلال یا دقیق فیشر اگر سلول کم است.",
      assumptions: "نمونه گیری مشخص؛ فراوانی مورد انتظار خیلی کوچک نباشد.",
      notThis: "تفسیر درصد ستون بدون طرح. علیت.",
      next: "جدول توافقی و اندازه اثر (مثلاً V کرامر) را با p تنها گزارش نکنید.",
      hedge: "اگر طرح پیچیده یا جفت رده ای است، این درخت کوتاه است.",
    };
  }
  if (input.goal === "prediction") {
    return {
      candidates: "شروع با رگرسیون خطی اگر وابسته پیوسته است؛ لجستیک اگر دو حالتی است.",
      assumptions: "مانده، مشخص بودن مدل، حجم نسبت به پیش بین ها، نبود نشت داده.",
      notThis: "وارد کردن همه متغیرها چون در پرسشنامه بودند.",
      next: "مدل را از نظریه بسازید. اندازه اثر و بازه را گزارش کنید.",
      hedge: "مدل چندسطحی و بقا خارج از این ابزار است.",
    };
  }
  if (input.goal === "association") {
    const spearman = input.scale === "ordinal" || input.parametric === "no";
    return {
      candidates: spearman ? "همبستگی اسپیرمن (رتبه)." : "همبستگی پیرسون اگر هر دو پیوسته و رابطه خطی است؛ وگرنه اسپیرمن.",
      assumptions: "استقلال جفت ها. پیرسون: خطی بودن و مانده معقول.",
      notThis: "همبستگی یعنی علیت. حذف پرت فقط برای بزرگ شدن r.",
      next: "نمودار پراکنش را قبل از عدد ببینید.",
      hedge: "اندازه اثر r است نه فقط معنی داری.",
    };
  }
  if (input.goal === "paired" || input.independence === "paired") {
    const nonparam = input.parametric === "no" || input.scale === "ordinal";
    return {
      candidates: nonparam ? "آزمون رتبه علامت دار ویلکاکسون." : "آزمون t زوجی اگر تفاوت ها تقریباً نرمال اند؛ وگرنه ویلکاکسون.",
      assumptions: "جفت واقعی (همان واحد). استقلال بین جفت ها.",
      notThis: "t مستقل روی قبل و بعد.",
      next: "تفاوت میانگین یا میانه و بازه را گزارش کنید نه فقط p.",
      hedge: "اندازه گیری مکرر بیش از دو زمان = مدل جدا.",
    };
  }
  if (input.goal === "compareK") {
    const nonparam = input.parametric === "no" || input.scale === "ordinal";
    return {
      candidates: nonparam ? "کروسکال والیس." : "ANOVA یک راهه اگر مفروضات برقرار است.",
      assumptions: "استقلال گروه ها. ANOVA: مانده و همگنی واریانس.",
      notThis: "چندین t دو به دو بدون برنامه.",
      next: "مقایسه های از پیش نوشته. اندازه اثر کلی و ساده.",
      hedge: "طرح عاملی یا کوواریانس خارج است.",
    };
  }
  if (input.goal === "compare2") {
    if (input.independence === "unknown") {
      return {
        candidates: "اول استقلال را روشن کنید. اگر جفت است مسیر زوجی؛ اگر دو نمونه جدا است مسیر t مستقل.",
        assumptions: "واحد تحلیل باید مشخص باشد.",
        notThis: "فشردن t مستقل پیش فرض.",
        next: "از استاد یا کدبوک بپرسید هر سطر کیست.",
        hedge: "این ابزار حدس نمی زند.",
      };
    }
    if (input.scale === "count") {
      return {
        candidates: "t روی شمار خام معمولاً نامناسب است. مدل شمارشی را جدا طراحی کنید.",
        assumptions: "پراکندگی، صفر زیاد، زمان در معرض.",
        notThis: "نرمال فرض کردن شمار.",
        next: "با مشاور آمار طرح را بگویید. این غربال کافی نیست.",
        hedge: "خروجی قطعی نیست.",
      };
    }
    if (input.scale === "binary") {
      return {
        candidates: "مقایسه نسبت ها (خی دو یا دقیق فیشر؛ یا رگرسیون لجستیک اگر پیش بین دارید).",
        assumptions: "استقلال. فراوانی مورد انتظار.",
        notThis: "t روی صفر و یک بدون توجیه.",
        next: "اندازه اثر نسبت یا نسبت بخت با بازه.",
        hedge: "خوشه و طرح پیچیده خارج است.",
      };
    }
    const nonparam = input.parametric === "no" || input.scale === "ordinal";
    return {
      candidates: nonparam ? "من ویتنی." : "آزمون t مستقل اگر مفروضات قابل دفاع است؛ وگرنه من ویتنی.",
      assumptions: "استقلال دو گروه. t: نرمال مانده یا حجم کافی؛ همگنی یا اصلاح.",
      notThis: "حذف موردها تا p ستاره بگیرد.",
      next: "اندازه اثر (d یا معادل رتبه) و بازه. در SPSS: Analyze → Compare Means برای t.",
      hedge: "همسان سازی و کوواریانس جدا است. این پیشنهاد شروع است.",
    };
  }
  return null;
}
