export type ClaimType =
  | "FIELD_OBSERVATION"
  | "CASE_STUDY"
  | "EXPERIMENT"
  | "Q_AND_A"
  | "PRACTICAL_RULE"
  | "OPINION"
  | "HYPOTHESIS"
  | "ALGORITHM_INTERPRETATION"
  | "TECHNICAL_FINDING"
  | "CONTENT_STRATEGY"
  | "SITE_ARCHITECTURE"
  | "LINK_BUILDING_OBSERVATION"
  | "SEARCH_CONSOLE_OBSERVATION"
  | "OUTDATED_OR_SUPERSEDED";

export type Stance = "DO" | "DONT" | "DEPENDS" | "TEST";

export type Currency =
  | "CURRENT"
  | "CURRENT_BUT_CONTEXTUAL"
  | "NEEDS_REVALIDATION"
  | "HISTORICAL_ONLY"
  | "SUPERSEDED";

export type Confidence = "high" | "medium" | "low";

export type EvidenceKind = "FIELD_EVIDENCE" | "OFFICIAL_EVIDENCE" | "SITE_DATA_EVIDENCE";

export type SourceId =
  | "ShahramRahbari"
  | "mahdi_araqii"
  | "MoradiSEOPR"
  | "TheSEOCommunity"
  | "GoogleOfficial"
  | "Synthesis";

export type Finding = {
  id: string;
  source: SourceId;
  messageId?: string;
  url?: string;
  date: string;
  author: string;
  topic: string;
  subtopic: string;
  claimType: ClaimType;
  stance: Stance;
  currency: Currency;
  confidence: Confidence;
  evidenceKind: EvidenceKind;
  conditions: string;
  observation: string;
  normalised: string;
  result?: string;
  conflictGroup?: string;
  applicability: string;
  risk: string;
  factory: string;
  actionability: "now" | "queue" | "test" | "reject";
};

export type NotebookBlock = {
  topic: string;
  do: string[];
  dont: string[];
  depends: string[];
  test: string[];
};

export type Conflict = {
  id: string;
  title: string;
  a: string;
  b: string;
  whenA: string;
  whenB: string;
  evidence: string;
  factoryNow: string;
  test?: string;
};

export type Experiment = {
  id: string;
  hypothesis: string;
  sources: string[];
  site: string;
  scope: string;
  variable: string;
  control: string;
  primary: string;
  secondary: string;
  window: string;
  confounders: string;
  rollback: string;
  status: "backlog" | "ready_for_review" | "rejected";
};

export type ActionItem = {
  id: string;
  priority: "P0" | "P1" | "P2" | "P3" | "P4";
  title: string;
  why: string;
  owner: string;
  sources: string[];
};

export type SiteProfile = {
  id: string;
  domain: string;
  role: string;
  intents: string[];
  serviceOwners: Array<{ intent: string; url: string }>;
  notes: string;
};

export type RejectItem = {
  id: string;
  title: string;
  why: string;
  sources: string[];
};

export type Opportunity = {
  id: string;
  priority: "P0" | "P1" | "P2" | "P3" | "P4";
  kind: "refresh" | "architecture" | "experiment" | "new_url" | "governance";
  site: string;
  target: string;
  intent: string;
  action: string;
  sources: string[];
};

export type LibraryEntry = {
  id: string;
  topic: string;
  claim: string;
  evidence: string[];
  evidenceKind: EvidenceKind;
  confidence: Confidence;
  date: string;
  sites: string;
  status: "reusable" | "superseded" | "hold";
  findingIds: string[];
};

export type FactoryChange = {
  at: string;
  agent: string;
  tab: string;
  old: string;
  now: string;
  reason: string;
  sources: string[];
  rollback: string;
  additive: boolean;
};

export type CoverageRow = {
  id: string;
  kind: string;
  url: string;
  earliest: string | null;
  latest: string | null;
  inspected: number;
  nonempty: number;
  usefulSeo: number;
  videos: number;
  qaProxy: number;
  inaccessible: string;
  note: string;
};

export type PageRole =
  | "HOME"
  | "SERVICE"
  | "RESEARCH_GUIDE"
  | "TOOL"
  | "DOWNLOAD"
  | "HUB"
  | "POLICY"
  | "AI_WORKSPACE"
  | "FORM";

export type PageDecision =
  | "KEEP"
  | "SURGICAL_UPDATE"
  | "EVIDENCE_REFRESH"
  | "UX_REWRITE"
  | "ADD_FIRST_PARTY_VALUE"
  | "ADD_INTERACTIVE_ASSET"
  | "ADD_MEDIA"
  | "MERGE"
  | "REMOVE"
  | "NEW_PAGE";

export type WhoHowWhy = "missing" | "partial" | "adequate";

export type VerificationStatus =
  | "unverified"
  | "identity_incomplete"
  | "verified"
  | "unassigned"
  | "do_not_use";

export type ExperienceKind =
  | "FIRST_PARTY_OBSERVATION"
  | "FIRST_PARTY_DATA"
  | "FIRST_PARTY_EXPERIMENT"
  | "EDITORIAL_INTERPRETATION"
  | "ANECDOTE";

export type SignalSource =
  | "GSC_WEB"
  | "GSC_AI"
  | "GSC_DISCOVER"
  | "GA4"
  | "CLARITY"
  | "AHREFS"
  | "SEMRUSH"
  | "MANUAL_SERP"
  | "AI_CITATION_MONITOR"
  | "PRODUCT_UX";

export type SourceTier = 0 | 1 | 2 | 3;

export type ArticleType =
  | "OFFICIAL_GUIDANCE"
  | "OFFICIAL_CHANGELOG"
  | "NEWS"
  | "VENDOR_GUIDE"
  | "VENDOR_STUDY"
  | "INDEPENDENT_STUDY"
  | "CASE_STUDY"
  | "EXPERIMENT"
  | "OPINION"
  | "INTERVIEW";

export type ClaimClass =
  | "OFFICIAL_FACT"
  | "DATA_FINDING"
  | "FIELD_OBSERVATION"
  | "INTERPRETATION"
  | "PREDICTION"
  | "HYPOTHESIS"
  | "MARKETING_CLAIM";

export type WebsiteImpact =
  | "WAIT"
  | "MONITOR"
  | "TEST"
  | "SURGICALLY_UPDATE"
  | "TECHNICAL_FIX"
  | "CHANGE_PROCESS"
  | "IGNORE";

export type Contributor = {
  id: string;
  name: string;
  role: string;
  sites: string[];
  experience: string;
  expertise: string;
  credentials: string;
  evidence: string;
  bio: string;
  profileUrl?: string;
  externalIds: string[];
  authored: string[];
  reviewed: string[];
  disclosure: string;
  verification: VerificationStatus;
  lastVerified: string;
  notes: string;
};

export type PolicyPage = {
  id: string;
  title: string;
  url?: string;
  status: "missing" | "fragmented" | "exists_weak" | "adequate";
  neededBecause: string;
  outline: string[];
  owner: string;
};

export type SchemaRule = {
  id: string;
  type: string;
  useWhen: string;
  never: string;
  googleStatus: string;
  factory: string;
};

export type PageAudit = {
  id: string;
  url: string;
  title: string;
  role: PageRole;
  lang: "fa" | "en";
  canonicalOwner: string;
  userJob: string;
  audience: string;
  originalValue: string;
  firstParty: string;
  author: string;
  reviewer: string;
  evidenceQuality: "none" | "thin" | "partial" | "strong";
  evidenceFreshness: string;
  who: WhoHowWhy;
  how: WhoHowWhy;
  why: WhoHowWhy;
  taskCompletion: "no" | "partial" | "yes";
  uxWriting: string;
  accessibility: string;
  interactive: string;
  media: string;
  pageExperience: string;
  internalLinks: string;
  trust: string;
  schema: string;
  aiVisibility: string;
  mainGap: string;
  action: PageDecision;
  priority: "P0" | "P1" | "P2" | "P3" | "P4";
  status: "queued" | "accepted_gap" | "blocked" | "demoed_here";
};

export type InteractiveAsset = {
  id: string;
  name: string;
  userJob: string;
  inputs: string[];
  outputs: string[];
  methodology: string;
  evidence: string;
  limitations: string;
  canonicalOwner: string;
  fallback: string;
  a11y: string;
  analytics: string[];
  maintenanceOwner: string;
  lastVerification: string;
  demoPath?: string;
  status: "spec" | "demoed_here" | "not_for_teznevise_yet";
};

export type UxSurface = {
  id: string;
  surface: string;
  bad: string;
  better: string;
  why: string;
};

export type A11yFinding = {
  id: string;
  where: string;
  issue: string;
  fix: string;
  status: "fixed_here" | "queued_for_site" | "accepted";
};

export type ExperienceNote = {
  id: string;
  kind: ExperienceKind;
  topic: string;
  observation: string;
  cannotPromoteTo: string;
  factory: string;
  date: string;
};

export type PubArticle = {
  id: string;
  source: string;
  tier: SourceTier;
  url: string;
  title: string;
  author: string;
  published: string;
  updated?: string;
  category: string;
  articleType: ArticleType;
  primaryTopic: string;
  hash: string;
  eventId?: string;
};

export type PubFinding = {
  id: string;
  articleId: string;
  eventId?: string;
  finding: string;
  claimClass: ClaimClass;
  dataset?: string;
  sample?: string;
  methodology?: string;
  limitations: string;
  officialVerification: string;
  confidence: Confidence;
  dateSensitive: boolean;
  applicability: string;
  factoryImpact: string;
  urgency: "P0" | "P1" | "P2" | "P3" | "P4";
  websiteImpact: WebsiteImpact;
};

export type PubEvent = {
  id: string;
  title: string;
  primarySource: string;
  reportingSources: string[];
  interpretations: string[];
  newEvidence: string;
  openQuestions: string;
  date: string;
};

export type IntelSource = {
  id: string;
  tier: SourceTier;
  name: string;
  url: string;
  lastChecked: string;
  lastProcessedDate: string;
  lastProcessedUrl: string;
  note: string;
};

export type GapDisposition = "fixed_here" | "queued" | "accepted" | "blocked";

export type OsGap = {
  id: string;
  area: string;
  gap: string;
  disposition: GapDisposition;
  owner: string;
  next: string;
};

export type ValidationCheck = {
  id: string;
  requirement: string;
  page: string;
  url: string;
  lang: "fa" | "en";
  role: PageRole;
  task: string;
  trust: string;
  a11y: string;
  schema: string;
  result: "pass" | "partial" | "blocked";
};

export type Technique = {
  id: string;
  name: string;
  claimedMechanism: string;
  evidence: string;
  risk: string;
  sites: string;
  testDesign: string;
  rollback: string;
  window: string;
  status: "ignore" | "backlog" | "ready_for_review";
};

export type CalculatorChild = {
  id: string;
  title: string;
  url: string;
  job: string;
  methodologySeen: "yes" | "thin" | "unseen";
  action: PageDecision;
  note: string;
};
