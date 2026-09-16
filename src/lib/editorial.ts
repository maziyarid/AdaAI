export type RegisterId =
  | "INTELLECTUAL_CONVERSATIONAL"
  | "NEUTRAL_EXPLANATORY"
  | "PROFESSIONAL_EDITORIAL"
  | "ACADEMIC_READABLE"
  | "RESEARCH_GUIDE"
  | "SERVICE_PAGE_NATURAL"
  | "LANDING_PRODUCT"
  | "UX_MICROCOPY"
  | "PATIENT_CLINIC"
  | "EDITORIAL_CRAFT"
  | "STUDENT_FAQ"
  | "BLOG_LONGFORM"
  | "ENGLISH_BRITISH";

export type Severity = "block" | "high" | "medium" | "note";

export type Finding = {
  id: string;
  severity: Severity;
  title: string;
  evidence: string;
  diagnosis: string;
  repair: string;
};

const RULES: Array<{
  id: string;
  title: string;
  re: RegExp;
  severity: Severity;
  diagnosis: string;
  repair: string;
  skip?: RegisterId[];
  only?: RegisterId[];
}> = [
  {
    id: "temporal-fluff",
    title: "افتتاحیۀ زمانی تهی",
    re: /در دنیای امروز|در عصر حاضر|در جهان امروز|بر کسی پوشیده نیست|In today's digital/,
    severity: "block",
    diagnosis: "در چکیده‌های علمی پژوهشی ایرانی و در نوشتار اصلی کافه فلسفه تقریباً غایب است.",
    repair: "جمله را حذف کنید و با کار، تمایز، یا مسئله شروع کنید.",
  },
  {
    id: "announce-article",
    title: "اعلام وجود مقاله",
    re: /در این مقاله قصد داریم|در ادامه به بررسی جامع|همه چیز درباره|از صفر تا صد|با ما همراه باشید/,
    severity: "block",
    diagnosis: "جمله کار خواننده را جلو نمی‌برد؛ فقط می‌گوید متن وجود دارد.",
    repair: "مستقیم تمایز یا پاسخ را بنویسید.",
  },
  {
    id: "mibashad",
    title: "می باشد / می گردد / می نماید",
    re: /می ?باشد|می ?گردد|خواهد گردید|می ?نماید|صورت پذیرفت|اقدام به انجام|اقدام نمود/,
    severity: "high",
    diagnosis: "علامت زبان اداری و کتاب درسی پیش از ۱۳۹۶. در نثر توضیحی معاصر نادر است.",
    repair: "است / شد / می کند / انجام شد.",
    skip: ["ENGLISH_BRITISH"],
  },
  {
    id: "tavassot-method",
    title: "توسط + فعل مجهول روشی",
    re: /توسط .{0,40}(تحلیل|بررسی|گردآوری|اندازه.?گیری|اجرا) (شد|گردید|گرفت)/,
    severity: "high",
    diagnosis: "گرته برداری از مجهول انگلیسی. «توسط» روایی (روایت شد توسط آنری) در پیکره کافه طبیعی است؛ «توسط SPSS تحلیل شد» نیست.",
    repair: "تحلیل داده ها با SPSS انجام شد.",
  },
  {
    id: "adjective-stack",
    title: "پشته صفت ابزار",
    re: /قدرتمند|جامع و کامل|یکپارچه|کاربرپسند|منحصر به فرد|هوشمند و/,
    severity: "high",
    diagnosis: "کلیشه ابزارهای بازاری که بین کانال های پایان نامه دست به دست می شود.",
    repair: "کار ابزار را بگویید، نه صفات آن را.",
  },
  {
    id: "guarantee",
    title: "زبان تضمین",
    re: /تضمینی|تضمین چاپ|پذیرش تضمین|چاپ تضمینی|ظرفیت محدود|از دست نده/,
    severity: "block",
    diagnosis: "ثبت سفارش پایان نامه، نه مشورت پژوهشی.",
    repair: "مرز خدمت را بنویسید. پذیرش مجله تضمین نمی شود.",
    only: ["SERVICE_PAGE_NATURAL", "RESEARCH_GUIDE", "NEUTRAL_EXPLANATORY", "LANDING_PRODUCT", "PATIENT_CLINIC"],
  },
  {
    id: "hamchenin-start",
    title: "همچنین / علاوه بر این در سر جمله",
    re: /(^|\n|۔|.)\s*(همچنین|علاوه بر این|از سوی دیگر)[،,]/,
    severity: "medium",
    diagnosis: "انسجام پرکننده. در نثر خوب، لولا معنایی یا تیتر جدید کافی است.",
    repair: "حذف کنید یا با اما / یعنی / پس جایگزین کنید؛ یکی در هر مرز.",
  },
  {
    id: "lazem-be-zekr",
    title: "لازم به ذکر است",
    re: /لازم به ذکر است|شایان توجه است|می بایست|حاصل فرمایید|ملاحظه فرمایید/,
    severity: "high",
    diagnosis: "اعلامیه دانشگاهی و بخشنامه.",
    repair: "نکته را مستقیم بگویید. برای شرط: اگر.",
  },
  {
    id: "jahet",
    title: "جهت به جای برای",
    re: /جهت (سفارش|ثبت|دستیابی|بررسی|استفاده|نیل)/,
    severity: "high",
    diagnosis: "جهت در متن خواننده اداری است. برای خنثی است.",
    repair: "برای.",
  },
  {
    id: "mored-stack",
    title: "مورد … قرار گرفت انباشته",
    re: /مورد (بررسی|استفاده|توجه|تجزیه و تحلیل|مطالعه) قرار/,
    severity: "medium",
    diagnosis: "در مقالات علمی رایج است؛ در راهنمای وبی معمولاً اضافه است. انباشتن آن آماس است.",
    repair: "بررسی شد / استفاده شد.",
    skip: ["ACADEMIC_READABLE"],
  },
  {
    id: "play-a-role",
    title: "نقش بازی کردن",
    re: /نقش .{0,24}را بازی/,
    severity: "high",
    diagnosis: "ترجمه تحت اللفظی play a role.",
    repair: "نقش X را به عهده دارد / X را تبیین می کند.",
  },
  {
    id: "method-that-is",
    title: "این روش، روشی است که",
    re: /این (روش|آزمون|پژوهش)،? \1?ی است که/,
    severity: "high",
    diagnosis: "تعریف ترجمه ای.",
    repair: "این آزمون برای … به کار می رود.",
  },
  {
    id: "final-slogan",
    title: "جمع بندی توخالی",
    re: /در نهایت می توان گفت|در پایان روز|راهگشا خواهد بود|به طور کلی می توان نتیجه گرفت/,
    severity: "medium",
    diagnosis: "پایان قالبی که ادعا را تکرار می کند.",
    repair: "یا معیار قابل استفاده بنویسید، یا جمله را حذف کنید.",
  },
  {
    id: "empty-methods",
    title: "روش خالی",
    re: /کیفی و از نوع توصیفی[- ]?تحلیلی|توصیفی تحلیلی است/,
    severity: "block",
    diagnosis: "عیب متعارف فصل روش: نوع پژوهش بدون منبع داده، نمونه، فن، ابزار.",
    repair: "منبع داده، منطق نمونه، فن تحلیل، و ابزار را بنویسید.",
    only: ["ACADEMIC_READABLE", "RESEARCH_GUIDE"],
  },
  {
    id: "synonym-stack",
    title: "پشته مترادف",
    re: /بررسی و تحلیل و ارزیابی|کاوش و بررسی و تحلیل|کلیدی، حیاتی و/,
    severity: "high",
    diagnosis: "فربهی / آماس. دو واژه متفاوت مانعی ندارد؛ سه مترادف تورم است.",
    repair: "یک فعل دقیق.",
  },
  {
    id: "flattery",
    title: "ندا و چاپلوسی",
    re: /کاربران عزیز|دوست عزیز|همراهان گرامی|پژوهشگران عزیز حتما|زیباجو عزیز/,
    severity: "high",
    diagnosis: "در کانال های خدمت، مرز ورود به دعوت به اقدام است.",
    repair: "خواننده را بزرگسال حساب کنید. کار را بگویید.",
  },
  {
    id: "boosters",
    title: "تقویت کننده بی پشتوانه",
    re: /بی تردید|بدون شک|قطعاً در|انکارناپذیر/,
    severity: "medium",
    diagnosis: "در چکیده ایرانی غایب است. اگر ادعا حدسی است، لحن قطعی آن را عوض نمی کند.",
    repair: "یا شاهد بیاورید، یا به نظر می رسد / معمولا.",
  },
  {
    id: "zwnj",
    title: "نیم فاصله (ZWNJ)",
    re: /\u200c/,
    severity: "note",
    diagnosis: "در فارسی معیار رایج است. در تولید Teznevise ممنوع است.",
    repair: "برای Teznevise: فاصله معمولی یا اتصال کامل. این قاعده سایت است، نه قاعده زبان.",
  },
  {
    id: "kiis",
    title: "کیس استادی",
    re: /کیس استادی|دیزرتیشن|دیتاها|ریسرچ(?!ر)/,
    severity: "medium",
    diagnosis: "برای این مفاهیم معادل جاافتاده فارسی هست.",
    repair: "مطالعه موردی / رساله / داده ها / پژوهش. پروپوزال و SPSS را عوض نکنید.",
  },
  {
    id: "absolute-proof",
    title: "زبان اثبات مطلق",
    re: /ثابت (کرد|شد|می کند) که|کاملاً درست از آب|فرضیه کاملا درست/,
    severity: "high",
    diagnosis: "یافته تجربی اثبات متافیزیکی نیست. در بحث و نتیجه، دلالت و همسویی طبیعی تر است.",
    repair: "آزمون فرض را در سطح اطمینان مشخص تأیید یا رد کنید.",
    skip: ["INTELLECTUAL_CONVERSATIONAL", "BLOG_LONGFORM", "ENGLISH_BRITISH"],
  },
  {
    id: "meta-nav",
    title: "فهرست سفر در چکیده یا سرآغاز",
    re: /در ادامه ابتدا|سپس تاریخچه|سپس انواع، سپس|ابتدا به تعریف می پردازیم/,
    severity: "high",
    diagnosis: "در چکیده علمی پژوهشی ایرانی غایب است. خواننده را به کار نمی برد.",
    repair: "حذف. اولین حرکت واقعی را شروع کنید.",
  },
  {
    id: "alpha-as-validity",
    title: "آلفا به جای روایی",
    re: /آلفا.{0,24}روایی|روایی.{0,24}آلفای کرونباخ (تأیید|تایید)/,
    severity: "block",
    diagnosis: "جمله ممکن است روان باشد و ادعا غلط. آلفا همسانی درونی است، نه روایی.",
    repair: "پایایی / همسانی درونی. روایی سازه را جدا گزارش کنید.",
    only: ["ACADEMIC_READABLE", "RESEARCH_GUIDE", "NEUTRAL_EXPLANATORY"],
  },
  {
    id: "dari-lexicon",
    title: "دری افغانستان در متن ایرانی",
    re: /پوهنتون|شفاخانه|دریور|لیسه|می ?باشم|نمیباشم/,
    severity: "block",
    diagnosis: "مخاطب ایران است. قاطی کردن دری خواننده را از ادامه متن دلسرد می کند.",
    repair: "دانشگاه، بیمارستان/کلینیک، راننده، دبیرستان، است/هست.",
    skip: ["ENGLISH_BRITISH"],
  },
  {
    id: "dari-motor",
    title: "موتر به جای خودرو/ماشین",
    re: /موتر/,
    severity: "block",
    diagnosis: "موتر در فارسی ایرانی خودرو نیست. ماشین در لندینگ ایرانی طبیعی است.",
    repair: "خودرو یا ماشین، بسته به رجیستر.",
    skip: ["ENGLISH_BRITISH"],
  },
  {
    id: "arabic-yeh-kaf",
    title: "ی/ک عربی در بدن ایرانی",
    re: /[\u064A\u0643]/,
    severity: "high",
    diagnosis: "نثر ایرانی ی (U+06CC) و ک (U+06A9) می خواهد مگر نقل عربی.",
    repair: "ی و ک فارسی.",
    skip: ["ENGLISH_BRITISH"],
  },
  {
    id: "dummy-cleft",
    title: "شکاف ساختگی این است که",
    re: /این (نکته|روش|امر|موضوع|مسئله|کار) است که|این است که باید/,
    severity: "high",
    diagnosis: "گرته برداری نام دار ویرایشی. آنچه بومی است؛ این … است که معمولا نیست.",
    repair: "جمله را از معنا بنویسید: ویرگول میان نهاد و گزاره نمی آید.",
    skip: ["ENGLISH_BRITISH"],
  },
  {
    id: "hype-speed",
    title: "شتاب و راز طلایی",
    re: /سه سوت|راز طلایی|۳۰ ثانیه ایده|۳۰ دقیقه گراندد|👇/,
    severity: "block",
    diagnosis: "ریتم فروش تلگرام معلم. منبع پرسش است نه بدن صفحه و نه لندینگ.",
    repair: "حرکت علمی یا کار محصول را بدون ایموجی و شتاب بنویسید.",
  },
  {
    id: "ghostwriting-offer",
    title: "پیشنهاد شبح نویسی",
    re: /انجام پایان.?نامه|ویراستاری فوری/,
    severity: "block",
    diagnosis: "بازار سفارش، نه مشورت. توانمندسازی (خودت بنویسی) با شبح نویسی قاطی نشود.",
    repair: "مشاوره نگارش و ویرایش. پایان نامه را پژوهشگر می نویسد.",
    only: ["SERVICE_PAGE_NATURAL", "LANDING_PRODUCT", "RESEARCH_GUIDE", "STUDENT_FAQ"],
  },
  {
    id: "saas-ecosystem",
    title: "اکوسیستم و تحول آفرین",
    re: /اکوسیستم|تحول آفرین|unlock the power|revolutionize your/,
    severity: "high",
    diagnosis: "ترجمه SaaS. لندینگ ایرانی کار را می گوید.",
    repair: "چه می شود، برای که، بعد از کلیک چه.",
    only: ["LANDING_PRODUCT", "SERVICE_PAGE_NATURAL", "UX_MICROCOPY", "ENGLISH_BRITISH"],
  },
  {
    id: "empty-cta",
    title: "شروع کنید خالی",
    re: /شروع کنید|Click here to get started/,
    severity: "high",
    diagnosis: "دکمه باید نام عمل را ببرد.",
    repair: "بررسی اولیه پژوهش / نوبت حضوری بگیرید / فهرست را ذخیره کنید.",
    only: ["LANDING_PRODUCT", "SERVICE_PAGE_NATURAL", "UX_MICROCOPY", "ENGLISH_BRITISH"],
  },
  {
    id: "content-heading",
    title: "کانتنت / کپی رایتینگ به عنوان تیتر",
    re: /کانتنت|کپی.?رایتینگ|Copy-?edit/,
    severity: "high",
    diagnosis: "حرفه ویراستار است نه کانتنت رایتر. مرحله انگلیسی یک بار در پرانتز.",
    repair: "ویرایش زبانی / پساویرایش (post-editing).",
    skip: ["ENGLISH_BRITISH"],
  },
  {
    id: "invalid-value",
    title: "مقدار نامعتبر",
    re: /مقدار نامعتبر|Invalid value/,
    severity: "high",
    diagnosis: "خطای UX باید فیلد را نام ببرد.",
    repair: "نوع مقیاس متغیر وابسته را انتخاب کنید.",
    only: ["UX_MICROCOPY", "LANDING_PRODUCT"],
  },
  {
    id: "clinic-beauty-seo",
    title: "زیباجو / اورژانس خارجی",
    re: /زیباجو|۹۱۱(?!\d)|(?<!\d)911(?!\d)|بدون عارضه|بهترین جراح/,
    severity: "block",
    diagnosis: "صفحه بیمار ایرانی: ۱۱۵، نه اسکلت دایره المعارف، نه زیبایی سئو.",
    repair: "کار بالینی، حد، اورژانس ۱۱۵. تضمین نتیجه ممنوع.",
    only: ["PATIENT_CLINIC", "LANDING_PRODUCT"],
  },
];

function sentences(text: string): string[] {
  return text
    .split(/(?<=[.\n؟!])/u)
    .map((s) => s.trim())
    .filter(Boolean);
}

export function scan(text: string, register: RegisterId): Finding[] {
  const findings: Finding[] = [];
  const seen = new Set<string>();

  for (const rule of RULES) {
    if (rule.skip?.includes(register)) continue;
    if (rule.only && !rule.only.includes(register)) continue;
    const m = text.match(rule.re);
    if (!m) continue;
    const key = rule.id + ":" + m[0];
    if (seen.has(key)) continue;
    seen.add(key);
    findings.push({
      id: rule.id,
      severity: rule.severity,
      title: rule.title,
      evidence: m[0],
      diagnosis: rule.diagnosis,
      repair: rule.repair,
    });
  }

  const sents = sentences(text);
  if (sents.length >= 5) {
    const lengths = sents.map((s) => s.length);
    const avg = lengths.reduce((a, b) => a + b, 0) / lengths.length;
    const variance =
      lengths.reduce((a, b) => a + (b - avg) ** 2, 0) / lengths.length;
    if (avg > 40 && variance < 180) {
      findings.push({
        id: "uniform-length",
        severity: "medium",
        title: "طول یکنواخت جمله ها",
        evidence: `${sents.length} جمله، واریانس پایین`,
        diagnosis: "یکنواختی ساختاری از نشانه‌های نثر تولیدشده است، نه خودِ طول.",
        repair: "جمله را جایی که فکر سرعت عوض می شود ببرید یا وصل کنید. حقه آشکارساز اضافه نکنید.",
      });
    }
  }

  if (register === "ACADEMIC_READABLE" && /می ?دون|یه |چیکار|رو /.test(text)) {
    findings.push({
      id: "register-clash-academic",
      severity: "high",
      title: "محاوره در مصنوع دانشگاهی",
      evidence: "علامت نوشتار گفتاری",
      diagnosis: "فصل روش و چکیده، یه / می دونن برنمی دارد.",
      repair: "را، است، انجام شد. گرمی را برای راهنما یا پرسش های متداول نگه دارید.",
    });
  }

  if (
    register === "ACADEMIC_READABLE" &&
    /ما .{0,32}(جمع آوری|پخش|استفاده) کردیم/.test(text)
  ) {
    findings.push({
      id: "first-person-methods",
      severity: "high",
      title: "ما کردی در روش کمی",
      evidence: "ما … کردیم",
      diagnosis: "در فصل روش کمی، مجهول بی کنشگر قرارداد است. ما آموزشی مال راهنماست.",
      repair: "گردآوری داده ها انجام شد.",
    });
  }

  if (
    register === "SERVICE_PAGE_NATURAL" &&
    /پژوهش حاضر|مقاله حاضر|نگارنده/.test(text)
  ) {
    findings.push({
      id: "journal-on-service",
      severity: "medium",
      title: "نثر مجله روی صفحه خدمت",
      evidence: "پژوهش حاضر / نگارنده",
      diagnosis: "این خودارجاع مال مقاله است، نه صفحه خدمت.",
      repair: "خدمت، مخاطب، مرز، فرایند، محدودیت.",
    });
  }

  if (
    register === "LANDING_PRODUCT" &&
    /پژوهش حاضر|مقاله حاضر|چکیده|نگارنده/.test(text)
  ) {
    findings.push({
      id: "journal-on-landing",
      severity: "block",
      title: "چکیده مجله روی لندینگ",
      evidence: "خودارجاع دانشگاهی",
      diagnosis: "لندینگ کار خواننده را در اولین صفحه می گوید، نه اسکلت IMRaD.",
      repair: "چه می شود، برای که، بعد از کلیک چه. CTA نام عمل است.",
    });
  }

  if (/جهت .{0,20}پیام بدهید/.test(text)) {
    findings.push({
      id: "register-clash-sentence",
      severity: "high",
      title: "برخورد رجیستر در یک جمله",
      evidence: "جهت + پیام بدهید",
      diagnosis: "اداری و گفتاری در یک جمله؛ قوی ترین نشانه ناهماهنگی.",
      repair: "یک سطح را انتخاب کنید.",
    });
  }

  if (
    (register === "ACADEMIC_READABLE" || register === "RESEARCH_GUIDE") &&
    /چیه|چطوری|مون /.test(text)
  ) {
    findings.push({
      id: "telegram-in-body",
      severity: "high",
      title: "ریتم تلگرام در بدن دانشگاه نما",
      evidence: "چیه / چطوری / مون",
      diagnosis: "پرسش دانشجو مال FAQ است. بدن صفحه impersonal و SOV می ماند.",
      repair: "تیتر گروه اسمی؛ فعل آخر.",
    });
  }

  const order: Record<Severity, number> = { block: 0, high: 1, medium: 2, note: 3 };
  return findings.sort((a, b) => order[a.severity] - order[b.severity]);
}

export const SAMPLE_DRAFTS: Record<RegisterId, string> = {
  RESEARCH_GUIDE: `در دنیای امروز اهمیت روش تحقیق بر کسی پوشیده نیست. در این مقاله قصد داریم به بررسی جامع و کامل روایی و پایایی بپردازیم.

داده ها توسط نرم افزار SPSS مورد تجزیه و تحلیل قرار گرفت. همچنین، این آزمون قدرتمند، جامع و کاربردی است. لازم به ذکر است که روش این پژوهش کیفی و از نوع توصیفی تحلیلی است. آلفای کرونباخ روایی پرسشنامه را تایید کرد.

در نهایت می توان گفت پژوهش حاضر راهگشا خواهد بود. جهت سفارش پیام بدهید.`,
  INTELLECTUAL_CONVERSATIONAL: `در دنیای امروز اهمیت تفکر بر کسی پوشیده نیست. در این مقاله قصد داریم فلسفه را از صفر تا صد شرح دهیم.`,
  NEUTRAL_EXPLANATORY: `در دنیای امروز روایی اهمیت دارد. این روش، روشی است که برای سنجش به کار می رود و می باشد که قدرتمند است.`,
  PROFESSIONAL_EDITORIAL: `لازم به ذکر است که ویرایش قلب تپنده تولید محتوا است و می باشد که متن را متحول می کند.`,
  ACADEMIC_READABLE: `در دنیای امروز اهمیت روش تحقیق بر کسی پوشیده نیست. روش این پژوهش کیفی و از نوع توصیفی تحلیلی است. ما داده ها را جمع آوری کردیم و یه تحلیل زدیم. آلفای کرونباخ روایی را تایید کرد.`,
  SERVICE_PAGE_NATURAL: `نگارش تضمینی پروپوزال و چاپ ISI با تحویل فوری. پژوهشگران عزیز حتما از این خدمت قدرتمند و یکپارچه استفاده نمایید. جهت سفارش پیام بدهید. پژوهش حاضر راهگشا خواهد بود.`,
  LANDING_PRODUCT: `در عصر اطلاعات، این پلتفرم اکوسیستم تحول آفرین هوش مصنوعی است. شروع کنید. پوهنتون شما را با ۱۲ راز طلایی به سطح بعدی می برد. پژوهش حاضر مسیر را نشان می دهد.`,
  UX_MICROCOPY: `خطا: مقدار نامعتبر است. شروع کنید. موفق.`,
  PATIENT_CLINIC: `زیباجو عزیز، بهترین جراح بدون عارضه شما را تضمین می کند. اورژانس: 911. شفاخانه ما می باشد که هوشمند و یکپارچه است.`,
  EDITORIAL_CRAFT: `هدف این راهنما آگاهی رسانی می باشد. این نکته است که باید به آن توجه شود که ویرگول مهم است. ویراستاری فوری پایان نامه با Copy-edit.`,
  STUDENT_FAQ: `چطور پیشینه ام را در سه سوت بنویسم؟ 👇 انجام پایان نامه با تضمین همانندجو.`,
  BLOG_LONGFORM: `در دنیای امروز اهمیت فرهنگ بر کسی پوشیده نیست. در نهایت می توان گفت که همه چیز راهگشا خواهد بود.`,
  ENGLISH_BRITISH: `In today's digital ecosystem, unlock the power of AI to revolutionize your thesis journey. Click here to get started!`,
};

export const SAMPLE_DRAFT = SAMPLE_DRAFTS.RESEARCH_GUIDE;

export function isSampleDraft(text: string): boolean {
  return Object.values(SAMPLE_DRAFTS).includes(text);
}

export function scoreLabel(findings: Finding[]): { label: string; tone: "ok" | "warn" | "mark" } {
  if (findings.some((f) => f.severity === "block")) return { label: "نیاز به بازنویسی از معنا", tone: "mark" };
  if (findings.some((f) => f.severity === "high")) return { label: "قابل ویرایش؛ رجیستر یا فعل مشکل دارد", tone: "warn" };
  if (findings.length) return { label: "قابل خواندن؛ چند لولا را کوتاه کنید", tone: "warn" };
  return { label: "نشانه قالبی آشکاری دیده نشد", tone: "ok" };
}
