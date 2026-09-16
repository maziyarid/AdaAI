# Teznevise site overlay — zero U+200C

Status: canonical site policy. Scope: `site:teznevise.ir` only.

Persian Teznevise content contains **zero U+200C ZWNJ**.

This is a site-specific production rule. It must not be generalized to all Persian.

Standard academic Persian commonly uses ZWNJ. That is a language fact, not a licence to ignore this site policy.

Applies to:

- post/page body
- titles and excerpts
- Yoast/SEO titles and descriptions
- constructed examples in Teznevise content
- schema/visible copy that ships to teznevise.ir

Ada validators treat any U+200C in Teznevise live content as a verification failure.
