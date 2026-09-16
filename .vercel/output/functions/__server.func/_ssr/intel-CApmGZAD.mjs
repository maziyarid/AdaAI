//#region node_modules/.nitro/vite/services/ssr/assets/intel-CApmGZAD.js
var INTEL_SOURCES = [
	{
		id: "google-search-blog",
		tier: 0,
		name: "Google Search Central Blog",
		url: "https://developers.google.com/search/blog",
		lastChecked: "2026-09-16",
		lastProcessedDate: "2026-09-08",
		lastProcessedUrl: "https://developers.google.com/search/docs/appearance/aggregator-features",
		note: "منبع اولیه. خبر شخص ثالث بدون پیوند به اینجا وارد کتابخانه نمی شود. 8 سپتامبر 2026: تفاوت منطقه ای واحد تجمیع گر — برای ایران IGNORE."
	},
	{
		id: "google-ai-features",
		tier: 0,
		name: "AI features documentation",
		url: "https://developers.google.com/search/docs/appearance/ai-features",
		lastChecked: "2026-09-16",
		lastProcessedDate: "2025-12-10",
		lastProcessedUrl: "https://developers.google.com/search/docs/appearance/ai-features",
		note: "سئوی جدا برای AI لازم نیست. متن خزیدنی و اسکیمای مطابق مرئی."
	},
	{
		id: "google-spam",
		tier: 0,
		name: "Spam policies",
		url: "https://developers.google.com/search/docs/essentials/spam-policies",
		lastChecked: "2026-09-16",
		lastProcessedDate: "2026-08-28",
		lastProcessedUrl: "https://developers.google.com/search/docs/essentials/spam-policies",
		note: "اسکیل، دامنه منقضی، شهرت سایت."
	},
	{
		id: "google-sd-policies",
		tier: 0,
		name: "Structured data policies",
		url: "https://developers.google.com/search/docs/appearance/structured-data/sd-policies",
		lastChecked: "2026-09-16",
		lastProcessedDate: "2026-07-10",
		lastProcessedUrl: "https://developers.google.com/search/docs/appearance/structured-data/sd-policies",
		note: "نشانه باید با متن مرئی یکی باشد."
	},
	{
		id: "bing",
		tier: 0,
		name: "Bing Webmaster",
		url: "https://www.bing.com/webmasters/help",
		lastChecked: "2026-09-16",
		lastProcessedDate: "—",
		lastProcessedUrl: "—",
		note: "این دور مقاله تازه ماده ای برای تزنویسه استخراج نشد."
	},
	{
		id: "ahrefs",
		tier: 1,
		name: "Ahrefs research",
		url: "https://ahrefs.com/blog/",
		lastChecked: "2026-09-16",
		lastProcessedDate: "—",
		lastProcessedUrl: "—",
		note: "مطالعه داده بدون روش وارد قانون نمی شود. این دور مطالعه تازه اولویت دار کشیده نشد."
	},
	{
		id: "semrush",
		tier: 1,
		name: "Semrush original research",
		url: "https://www.semrush.com/blog/",
		lastChecked: "2026-09-16",
		lastProcessedDate: "—",
		lastProcessedUrl: "—",
		note: "مثل Ahrefs. تضاد روش را در ماتریس تعارض ثبت کنید نه میانگین."
	},
	{
		id: "google-docs-changelog",
		tier: 0,
		name: "Search documentation changelog",
		url: "https://developers.google.com/search/updates",
		lastChecked: "2026-09-16",
		lastProcessedDate: "2026-09-08",
		lastProcessedUrl: "https://developers.google.com/search/docs/appearance/aggregator-features",
		note: "RSS: search_docs_updates.rss. تغییر چیدمان منطقه ای رتبه نیست."
	},
	{
		id: "sej",
		tier: 2,
		name: "Search Engine Journal",
		url: "https://www.searchenginejournal.com/",
		lastChecked: "2026-09-16",
		lastProcessedDate: "2026-06-03",
		lastProcessedUrl: "https://developers.google.com/search/blog/2026/06/gen-ai-performance-reports",
		note: "گزارش. منبع اولیه گوگل حاکم است."
	},
	{
		id: "sel",
		tier: 2,
		name: "Search Engine Land",
		url: "https://searchengineland.com/",
		lastChecked: "2026-09-16",
		lastProcessedDate: "2026-06-03",
		lastProcessedUrl: "https://developers.google.com/search/blog/2026/06/gen-ai-performance-reports",
		note: "گزارش. کلیک GSC_AI هنوز نیست."
	}
];
var PUB_EVENTS = [
	{
		id: "EV-GSC-GENAI",
		title: "گزارش Generative AI در سرچ کنسول",
		primarySource: "https://developers.google.com/search/blog/2026/06/gen-ai-performance-reports",
		reportingSources: ["https://cicero.studio/en/blog/search-console-generative-ai-performance-reports-geo-2026/", "https://www.seroundtable.com/google-search-console-generative-ai-tools-live-41984.html"],
		interpretations: [
			"رسمی: ایمپرشن در AI Overviews و AI Mode و Discover جدا شده است.",
			"گزارش: در پرتاب کلیک و پرس وجو نیست.",
			"گزارش: رول اوت تدریجی؛ 31 اوت 2026 کنترل AI جهانی شد. اگر داده کافی نباشد گزارش نمی آید."
		],
		newEvidence: "اولین پنجره اول شخص گوگل برای دید در ویژگی های زایشی. با تخمین فروشنده یکی نیست.",
		openQuestions: "آیا دارایی teznevise.ir گزارش را می بیند؟ کلیک کی اضافه می شود؟",
		date: "2026-06-03"
	},
	{
		id: "EV-AI-FEATURES",
		title: "راهنمای رسمی ویژگی های هوش مصنوعی جستجو",
		primarySource: "https://developers.google.com/search/docs/appearance/ai-features",
		reportingSources: [],
		interpretations: ["سئوی بنیادی کافی است. فایل یا اسکیمای جدا برای AI لازم نیست."],
		newEvidence: "متن مهم باید متن باشد. اسکیما با مرئی یکی. خزش اجازه داشته باشد.",
		openQuestions: "—",
		date: "2025-12-10"
	},
	{
		id: "EV-SITE-REP-EEA",
		title: "اجرای شهرت سایت در EEA تغییر کرد",
		primarySource: "https://developers.google.com/search/blog/2026/08/update-site-reputation-policy",
		reportingSources: [],
		interpretations: ["خارج EEA اقدام دستی روی بخش ثالث اثر می کند.", "داخل EEA اثر اقدام دستی روی نتایج آن کاربران اعمال نمی شود؛ بخش ممکن است جدا رتبه بگیرد."],
		newEvidence: "سیاست وجود دارد؛ اجرا جغرافیایی شد.",
		openQuestions: "تزنویسه مخاطب ایران است نه EEA. میزبانی محتوای ثالث برای رتبه همچنان خطر است.",
		date: "2026-08-28"
	},
	{
		id: "EV-BACK-BTN",
		title: "ربودن دکمه بازگشت اسپم شد",
		primarySource: "https://developers.google.com/search/blog/2026/04/back-button-hijacking",
		reportingSources: [],
		interpretations: ["اجرا از 15 ژوئن 2026. اسکریپت تاریخچه فریبنده را بردارید."],
		newEvidence: "سیاست جدید اعمال مخرب.",
		openQuestions: "آیا تزنویسه یا چت زنده تاریخچه را دستکاری می کند؟",
		date: "2026-04-13"
	},
	{
		id: "EV-DISCOVER-2026-02",
		title: "آپدیت هسته Discover فوریه 2026",
		primarySource: "https://developers.google.com/search/blog/2026/02/discover-core-update",
		reportingSources: [],
		interpretations: ["تخصص بخش به بخش. کلیک بیت کمتر. محتوای محلی بیشتر."],
		newEvidence: "هم راستا با F-017 درباره تخصص بخش.",
		openQuestions: "Discover برای تزنویسه چقدر مهم است؟ احتمالاً کم.",
		date: "2026-02-05"
	},
	{
		id: "EV-RICH-PHASEOUT",
		title: "حذف تدریجی برخی ریچ ریزالت ها",
		primarySource: "https://developers.google.com/search/blog/2025/06/simplifying-search-results",
		reportingSources: [],
		interpretations: ["Course Info، Claim Review، Learning Video و چند نوع از کنسول خارج شدند."],
		newEvidence: "اسکیما برای ریچ ریزالت مرده سرمایه گذاری رتبه نیست.",
		openQuestions: "تزنویسه کدام نوع را هنوز دارد؟",
		date: "2025-09-08"
	},
	{
		id: "EV-FAQ-LIMIT",
		title: "محدودیت FAQ و HowTo ریچ ریزالت",
		primarySource: "https://developers.google.com/search/blog/2023/08/howto-faq-changes",
		reportingSources: [],
		interpretations: ["FAQ ریچ ریزالت برای اکثر سایت ها دیگر معمول نیست. پرسش مرئی برای انسان بماند."],
		newEvidence: "زمینه SCH-FAQ.",
		openQuestions: "—",
		date: "2023-08-08"
	},
	{
		id: "EV-REGIONAL-2026-09",
		title: "اسناد تفاوت منطقه ای تجربه جستجو",
		primarySource: "https://developers.google.com/search/docs/appearance/aggregator-features",
		reportingSources: ["https://developers.google.com/search/updates", "https://www.seroundtable.com/google-regional-differences-search-experience.html"],
		interpretations: ["رسمی: واحد تجمیع گر، تأمین کننده، کاروسل در برخی کشورها.", "صنعت: تغییر چیدمان است نه آپدیت هسته."],
		newEvidence: "صلاحیت منطقه ای برای ناشران تجمیع گر. مخاطب ایران تزنویسه داخل این واحدها نیست.",
		openQuestions: "آیا SERP فارسی واحد مشابه دارد؟ تا مشاهده دستی IGNORE.",
		date: "2026-09-08"
	},
	{
		id: "EV-FAVICON-2026-08",
		title: "فرمت فاویکون در سند صریح شد",
		primarySource: "https://developers.google.com/search/docs/appearance/favicon-in-search",
		reportingSources: ["https://developers.google.com/search/updates"],
		interpretations: ["فرمت های پشتیبانی شده عوض نشدند؛ فهرست صریح شد."],
		newEvidence: "ابهام ارجاع بیرونی کم شد.",
		openQuestions: "فاویکون تزنویسه در نتایج چیست؟ P4.",
		date: "2026-08-28"
	}
];
var PUB_FINDINGS = [
	{
		id: "PF-01",
		articleId: "A-GSC-GENAI",
		eventId: "EV-GSC-GENAI",
		finding: "سرچ کنسول ایمپرشن ویژگی های زایشی را جدا گزارش می کند. کلیک و پرس وجو در پرتاب نیست.",
		claimClass: "OFFICIAL_FACT",
		limitations: "رول اوت تدریجی؛ داده ناکافی = بدون گزارش. تخمین فروشنده GEO معادل نیست.",
		officialVerification: "PRIMARY. وبلاگ 3 ژوئن 2026.",
		confidence: "high",
		dateSensitive: true,
		applicability: "هر دارایی تأییدشده. تزنویسه: وجود گزارش ناشناخته.",
		factoryImpact: "SEO Signals باید منبع GSC_AI جدا از GSC_WEB و جدا از AHREFS/SEMRUSH نگه دارد.",
		urgency: "P1",
		websiteImpact: "MONITOR"
	},
	{
		id: "PF-02",
		articleId: "A-AI-FEATURES",
		eventId: "EV-AI-FEATURES",
		finding: "برای حضور در AI Overviews / AI Mode سئوی بنیادی کافی است. متن مهم متن باشد. اسکیما با مرئی یکی باشد. خزش باز باشد.",
		claimClass: "OFFICIAL_FACT",
		limitations: "سند 2025-12-10؛ اگر عوض شد تاریخ را تازه کنید.",
		officialVerification: "PRIMARY.",
		confidence: "high",
		dateSensitive: true,
		applicability: "همه صفحات عمومی تزنویسه.",
		factoryImpact: "llms.txt پروژه نیست. صفحه جدا برای هر fan-out نسازید.",
		urgency: "P1",
		websiteImpact: "CHANGE_PROCESS"
	},
	{
		id: "PF-03",
		articleId: "A-SPAM-EEA",
		eventId: "EV-SITE-REP-EEA",
		finding: "سیاست شهرت سایت مانده است. اجرای EEA فرق دارد. ایران EEA نیست.",
		claimClass: "OFFICIAL_FACT",
		limitations: "به میزبانی محتوای ثالث برای رتبه مربوط است نه به خدمات خود تزنویسه مگر رپورتاژ وارونه.",
		officialVerification: "PRIMARY 28 اوت 2026 + spam policies 28 اوت 2026.",
		confidence: "high",
		dateSensitive: true,
		applicability: "اگر تزنویسه محتوای ثالث تجاری میزبانی کند — نباید.",
		factoryImpact: "Do-not-adopt میزبانی رپورتاژ روی دامنه اعتماد.",
		urgency: "P2",
		websiteImpact: "CHANGE_PROCESS"
	},
	{
		id: "PF-04",
		articleId: "A-BACK-BTN",
		eventId: "EV-BACK-BTN",
		finding: "دستکاری دکمه بازگشت از 15 ژوئن 2026 سیاست اسپم اعمال مخرب است.",
		claimClass: "OFFICIAL_FACT",
		limitations: "باید روی اسکریپت چت/پاپ تزنویسه چک شود. اینجا دسترسی به منبع قالب نبود.",
		officialVerification: "PRIMARY.",
		confidence: "high",
		dateSensitive: false,
		applicability: "هر اسکریپت فرانت تزنویسه.",
		factoryImpact: "Technical SEO: چک تاریخچه مرورگر. پاپ فریبنده در do-not-adopt.",
		urgency: "P2",
		websiteImpact: "MONITOR"
	},
	{
		id: "PF-05",
		articleId: "A-FAQ-2023",
		eventId: "EV-FAQ-LIMIT",
		finding: "FAQ rich result برای اکثر سایت ها دیگر هدف معقول نیست. پرسش مرئی برای انسان بماند.",
		claimClass: "OFFICIAL_FACT",
		limitations: "استثنای سلامت/دولت معتبر شامل تزنویسه نیست.",
		officialVerification: "PRIMARY 2023؛ ساده سازی سرپ 2025 همسو.",
		confidence: "high",
		dateSensitive: false,
		applicability: "راهنماها و خدمات با پرسش.",
		factoryImpact: "A-09. اسکیمای FAQ تزئینی نه.",
		urgency: "P1",
		websiteImpact: "SURGICALLY_UPDATE"
	},
	{
		id: "PF-06",
		articleId: "A-DISCOVER",
		eventId: "EV-DISCOVER-2026-02",
		finding: "Discover تخصص را بخش به بخش می سنجد. کلیک بیت کم می شود.",
		claimClass: "OFFICIAL_FACT",
		limitations: "تزنویسه احتمالاً Discover-first نیست.",
		officialVerification: "PRIMARY.",
		confidence: "medium",
		dateSensitive: false,
		applicability: "اگر Discover ترافیک دارد.",
		factoryImpact: "همسو F-017. عمود تازه برای Discover باز نکنید.",
		urgency: "P3",
		websiteImpact: "WAIT"
	},
	{
		id: "PF-07",
		articleId: "A-REGIONAL",
		eventId: "EV-REGIONAL-2026-09",
		finding: "اسناد 8 سپتامبر 2026 تفاوت منطقه ای واحدهای سرپ را توضیح می دهد. تغییر چیدمان است نه قانون رتبه برای سایت مشاوره فارسی.",
		claimClass: "OFFICIAL_FACT",
		limitations: "ایران در فهرست واحد تجمیع گر این سند هدف نیست.",
		officialVerification: "PRIMARY changelog 2026-09-08 + aggregator-features.",
		confidence: "high",
		dateSensitive: true,
		applicability: "teznevise.ir: شرط برقرار نیست.",
		factoryImpact: "تکنیک تازه نیست. IGNORE. صفحه برای واحد تجمیع گر نسازید.",
		urgency: "P4",
		websiteImpact: "IGNORE"
	},
	{
		id: "PF-08",
		articleId: "A-FAVICON",
		eventId: "EV-FAVICON-2026-08",
		finding: "فهرست فرمت فاویکون صریح شد. خود فرمت ها عوض نشدند.",
		claimClass: "OFFICIAL_FACT",
		limitations: "فقط اگر فاویکون خراب یا فرمت نامعمول باشد.",
		officialVerification: "PRIMARY 2026-08-28.",
		confidence: "high",
		dateSensitive: false,
		applicability: "فنی جزئی.",
		factoryImpact: "P4. قانون محتوا نمی شود.",
		urgency: "P4",
		websiteImpact: "IGNORE"
	}
];
var BRIEFING = {
	fa: {
		changed: [
			"سرچ کنسول ایمپرشن ویژگی های زایشی را جدا می کند — بدون کلیک در پرتاب.",
			"برای AI Overviews سئوی جدا و llms.txt لازم نیست.",
			"FAQ ریچ ریزالت هدف این سایت نیست.",
			"شهرت سایت در EEA جور دیگر اجرا می شود؛ خطر میزبانی ثالث برای ایران سر جایش است.",
			"8 سپتامبر 2026: اسناد واحد منطقه ای سرپ. برای تزنویسه IGNORE."
		],
		why: "اندازه گیری و اسکیما و تولید صفحه را عوض می کند. رتبه جادویی نمی سازد.",
		evidence: "وبلاگ و اسناد گوگل، خوشه شده. گزارش های صنعت منبع اولیه نیستند.",
		sites: "teznevise.ir: MONITOR برای وجود گزارش GSC_AI. CHANGE_PROCESS برای اسکیما و fan-out.",
		action: "گزارش را اگر هست جدا ذخیره کنید. اسکیمای FAQ/ستاره را پاک کنید. صفحه fan-out نسازید."
	},
	en: {
		changed: [
			"Search Console now isolates generative-AI impressions (AI Overviews, AI Mode, Discover AI). Clicks and queries were not in the launch.",
			"Google's AI-features documentation still says ordinary technical SEO is the eligibility bar — crawlable text, matching structured data, no special AI file.",
			"FAQ rich results are not a realistic target for this site.",
			"Site-reputation enforcement changed in the EEA; hosting third-party ranking bait remains a bad idea everywhere.",
			"8 Sep 2026: regional SERP-unit documentation. Layout, not a ranking update. Ignore for an Iranian consultation site unless we later see the units on Persian SERPs."
		],
		why: "This changes measurement, schema hygiene, and whether we mint URLs for query fan-out. It does not create a new ranking lever.",
		evidence: "Google Search Central blog and docs as PRIMARY. Industry posts clustered, not promoted to independent findings.",
		sites: "teznevise.ir: MONITOR whether the property has the GSC AI report. Do not mix vendor GEO estimates with GSC_AI.",
		action: "Store GSC_AI separately from GSC_WEB. Strip decorative FAQ/star markup. Do not build one URL per fan-out query."
	}
};
var SIGNAL_POLICY = [
	{
		source: "GSC_WEB",
		use: "کلیک، ایمپرشن، پرس وجوی وب. با سرنخ کسب وکار بخوانید."
	},
	{
		source: "GSC_AI",
		use: "ایمپرشن ویژگی زایشی. کلیک نیست. با GSC_WEB جمع نکنید."
	},
	{
		source: "GSC_DISCOVER",
		use: "جدا. تزنویسه احتمالاً کم حجم."
	},
	{
		source: "GA4",
		use: "رفتار و تبدیل. فاکتور رتبه گوگل نیست."
	},
	{
		source: "CLARITY",
		use: "الگوی استفاده. فاکتور رتبه نیست."
	},
	{
		source: "AHREFS",
		use: "تخمین فروشنده. با کنسول قاطی نشود."
	},
	{
		source: "SEMRUSH",
		use: "تخمین فروشنده. روش با Ahrefs فرق دارد."
	},
	{
		source: "MANUAL_SERP",
		use: "مشاهده دستی با تاریخ و پرس وجو."
	},
	{
		source: "AI_CITATION_MONITOR",
		use: "ذکر در ابزار ثالث. اول شخص گوگل نیست."
	},
	{
		source: "PRODUCT_UX",
		use: "مفید بود؟ رها کردن فرم. فاکتور رتبه نیست."
	}
];
//#endregion
export { SIGNAL_POLICY as a, PUB_FINDINGS as i, INTEL_SOURCES as n, PUB_EVENTS as r, BRIEFING as t };
