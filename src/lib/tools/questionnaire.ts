export type QItem = {
  id: string;
  prompt: string;
  hint: string;
};

export const Q_ITEMS: QItem[] = [
  {
    id: "construct",
    prompt: "سازه هر مقیاس در یک جمله تعریف شده است؟",
    hint: "اگر ندانید چه چیزی اندازه گرفته می شود، پایایی عدد تزئینی است.",
  },
  {
    id: "leading",
    prompt: "گویه هدایت گر یا دو سؤالی ندارید؟",
    hint: "«آیا شما هم مثل بقیه موافق اید که…» داده نمی سازد.",
  },
  {
    id: "scale",
    prompt: "نوع مقیاس (اسمی، رتبه ای، فاصله ای ادعایی) نوشته شده است؟",
    hint: "لیکرت را بی توجیه فاصله ای نگیرید. آزمون بعداً روی همین ادعا سوار می شود.",
  },
  {
    id: "reverse",
    prompt: "گویه معکوس اگر هست، نمره گذاری اش نوشته شده است؟",
    hint: "معکوس فراموش شده آلفا را خراب می کند و کسی نمی فهمد چرا.",
  },
  {
    id: "pretest",
    prompt: "پیش آزمون روی چند نفر شبیه نمونه انجام شده است؟",
    hint: "ابهام گویه قبل از نمونه اصلی ارزان تر درست می شود.",
  },
  {
    id: "translation",
    prompt: "اگر ترجمه است، مسیر ترجمه و تطبیق فرهنگی ثبت شده است؟",
    hint: "کپی زیرنویس ابزار خارجی روایی نمی آورد.",
  },
  {
    id: "length",
    prompt: "زمان پر کردن برای پاسخ دهنده واقع بینانه است؟",
    hint: "پرسشنامه خسته کننده داده گمشده و پاسخ تصادفی می سازد.",
  },
  {
    id: "ethics",
    prompt: "رضایت، محرمانگی، و حق انصراف در مقدمه آمده است؟",
    hint: "حتی مقیاس کوتاه بدون این مقدمه در بسیاری از دانشگاه ها نمی گذرد.",
  },
];

export type QAnswer = "yes" | "no" | "unsure";

export type QFlag = {
  id: string;
  level: "stop" | "risk" | "ok";
  title: string;
  detail: string;
};

export function screenQuestionnaire(answers: Record<string, QAnswer | "">): QFlag[] | null {
  if (Q_ITEMS.some((i) => !answers[i.id])) return null;
  const flags: QFlag[] = [];

  const fail = (id: string, stop: boolean, title: string, detail: string) => {
    const a = answers[id];
    if (a === "no") flags.push({ id, level: stop ? "stop" : "risk", title, detail });
    else if (a === "unsure") flags.push({ id, level: "risk", title: `معلوم نیست: ${title}`, detail });
  };

  fail("construct", true, "سازه تعریف نشده", "اول بگویید هر مقیاس چه چیزی را می سنجد. وگرنه تحلیل تفسیر ندارد.");
  fail("leading", false, "گویه هدایت گر یا دو سؤالی", "گویه را دو تکه کنید و بار ارزشی را بردارید.");
  fail("scale", true, "نوع مقیاس نوشته نشده", "قبل از انتخاب آزمون، مقیاس را قفل کنید. درخت آزمون روی این ادعا سوار است.");
  fail("reverse", false, "نمره گذاری معکوس مبهم", "در کدبوک ستون معکوس را مشخص کنید.");
  fail("pretest", false, "پیش آزمون نیست", "پنج تا ده نفر شبیه نمونه، با یادداشت ابهام، کافی است برای غربال.");
  fail("translation", false, "ترجمه بدون مسیر", "حداقل ترجمه مستقیم و بازبینی فرد دوم. ادعای روایی ابزار اصلی به فارسی منتقل نمی شود.");
  fail("length", false, "طول واقع بینانه نیست", "زمان را با ساعت اندازه بگیرید نه با حدس.");
  fail("ethics", true, "مقدمه اخلاق نیست", "رضایت و محرمانگی را قبل از گویه اول بگذارید.");

  if (flags.length === 0) {
    flags.push({
      id: "ok",
      level: "ok",
      title: "این غربال مانع آشکار نشان نداد",
      detail: "جای روایی سازه، تحلیل عاملی، و نظر استاد را نمی گیرد. فقط نقص های رایج را کم می کند.",
    });
  }
  return flags;
}

export const Q_FALLBACK = Q_ITEMS.map((i) => [i.prompt, i.hint]);
