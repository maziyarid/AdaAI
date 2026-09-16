import { createHash, createHmac, randomUUID, timingSafeEqual } from "node:crypto";

/** Preview-only HMAC. Production must set ADA_RECEIPT_HMAC_KEY (≥32 chars). Never write a .env. */
const PREVIEW_HMAC = "ada-preview-hmac-key-not-for-production-use!";
export const RECEIPT_KEY_ID = process.env.ADA_RECEIPT_KEY_ID ?? "internal-hmac";
const RECEIPT_TTL_SECONDS = Number(process.env.ADA_RECEIPT_TTL_SECONDS ?? "900");

export function receiptHmacKey(): string {
  const env = process.env.ADA_RECEIPT_HMAC_KEY?.trim();
  return env && env.length >= 32 ? env : PREVIEW_HMAC;
}

export function newId(): string {
  return randomUUID();
}

export function canonicalJson(obj: unknown): string {
  return JSON.stringify(sortValue(obj));
}

function sortValue(v: unknown): unknown {
  if (v === null || typeof v !== "object") return v;
  if (Array.isArray(v)) return v.map(sortValue);
  const o = v as Record<string, unknown>;
  const out: Record<string, unknown> = {};
  for (const k of Object.keys(o).sort()) out[k] = sortValue(o[k]);
  return out;
}

export function sha256Text(text: string): string {
  return createHash("sha256").update(text).digest("hex");
}

export function sha256Obj(obj: unknown): string {
  return sha256Text(canonicalJson(obj));
}

export function hmacSign(payload: Record<string, unknown>): string {
  return createHmac("sha256", receiptHmacKey()).update(canonicalJson(payload)).digest("hex");
}

export function hmacVerify(payload: Record<string, unknown>, signature: string): boolean {
  const expected = Buffer.from(hmacSign(payload), "hex");
  const got = Buffer.from(signature, "hex");
  if (expected.length !== got.length) return false;
  return timingSafeEqual(expected, got);
}

export function receiptTtlMs(): number {
  return RECEIPT_TTL_SECONDS * 1000;
}

/** Floor to seconds so timestamptz round-trips through PGLite/Neon. */
export function toIsoSeconds(v: Date | string): string {
  const d = v instanceof Date ? v : new Date(v);
  return new Date(Math.floor(d.getTime() / 1000) * 1000).toISOString();
}
