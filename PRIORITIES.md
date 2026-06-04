# Exodus v1.3 — Fix Priority Roadmap (first-pass evaluation)

**Date:** 2026-06-03
**Ordered by Lucas's workflow priority:** Image pipeline → Random idea + Organic/Instagram → Swipe (competitor) → Cosmetic. Severity-ordered within each bucket (🔴 P0 · 🟠 P1 · 🟡 P2).

**Repos:**
- CLI / image-gen / copy findings (#47–60): https://github.com/lukemiha17/exodus-v1.3-cli
- Dashboard findings (#37–46): https://github.com/lukemiha17/exodus-v1.3-dashboard

---

## 1️⃣ IMAGE PIPELINE — most important
*Paste a dump of ads → generate images, all correctly organized.*

- 🔴 **#52 [CLI]** — Steering must be always-asked, first-class (steering-only with no copy + steering-emphasis). *Lucas's #1.*
- 🔴 **#49 [CLI]** — No cancel command (cross-cuts copy too, but worst here — uncancellable 360-render batches; cost control).
- 🟠 **#48 [CLI]** — Stop auto-firing; build the spec wizard (Engine→Scope→Aspect→Count; nothing unasked) + F1–F6 run formats.
- 🟠 **#50 [CLI]** — Brand Info empty/unvalidated (founder + product photos feed image gen); no CLI setter; `doctor` falsely says "READY."
- 🟠 **#55 [CLI]** — Template renders fail under load (Convex `claimRenderSlot` OptimisticConcurrencyControlFailure).
- 🟠 **#51 [CLI]** — 50-image cap errors instead of auto-splitting.
- 🟠 **#47 [CLI]** — "Native" mislabeled (`--type native` = Reptile).
- 🟠 **#38 [Dash]** — Native+Template not unified; toggling silently wipes the other's config (data loss).
- 🟠 **#37 [Dash]** — Allow steering-only runs in the batch modal (dashboard side of #52).
- 🟠 **#39 [Dash]** — Templates don't declare/receive inputs (founder/note/product).
- 🟠 **#40 [Dash]** — Library search broken (can't find your generated images).

## 2️⃣ RANDOM IDEA + ORGANIC / INSTAGRAM
*Put in a random idea → it writes; Instagram/reel → it writes.*

- 🟠 **#56 [CLI]** — Ask the pre-write questions (segment/awareness/primer/mechanism/CTA/steering; offered, never blocks).
- 🟠 **#54 [CLI]** — Idea Bank can't re-dispatch an idea (lock skips re-runs).
- 🟠 **#46 [Dash]** — Primers too long; make collapsible (the writer's primers).
- ✅ **#53 [CLI]** — Copy ideation gate (Write / Both / Just save) — approved, build it.
- *No broken bug logged yet for IG-reel ingestion itself (`genesis --reel` covers IG/TikTok) — failures here slot in.*

## 3️⃣ SWIPE — competitor ads
*⚠️ Holds the two most-severe individual bugs (both P0), even though ranked third overall.*

- 🔴 **#60 [CLI]** — Writing from a competitor ad fails 100% (`genesis:paste` key-scoping bug; deconstruct step reads the LLM key from the wrong place). *The headline break.*
- 🔴 **#57 [CLI]** — Can't ingest raw FB ad copy / Ad Library URL (`--fb-ad`, `--paste`).
- 🟠 **#58 [CLI]** — Swipe pipeline broken end-to-end (auto-resolve page id from an ad URL; chain research→mine→write).
- 🟠 **#59 [CLI]** — Swipe library drops metadata + 200 server-side cap + no brand query (store impressions/longevity/variants; paginate; sort/score/search).
- 🟠 **#42 [Dash]** — Mining blocked without FB Page ID + noisy "20 brands failed" banner.
- 🟠 **#41 [Dash]** — Mining grid: missing video thumbnails + broken static thumbnails.

## 4️⃣ COSMETIC
- 🟡 **#43 [Dash]** — "Swipe this ad" video shows "no image" (awareness-level flow itself is good — keep).
- 🟡 **#44 [Dash]** — Whole "Since" date bar should open the picker, not just the icon.
- 🟡 **#45 [Dash]** — Gambit "random shit" placeholder — unprofessional copy.

---

**Sequencing note:** by Lucas's workflow order, Image pipeline is #1. But the two single most-severe bugs — **#60** and **#57** (both P0) — live in the Swipe bucket. So they remain the most-broken individual items even though Swipe ranks third. The competitor-loop cluster is **#57 (ingest) + #58 (pipeline) + #59 (library) + #60 (write)**; #60 is the highest-leverage single fix (precise key-scoping root cause).

*Full detail per finding: see `exodus-v1.3-cli-edits.md` / `exodus-v1.3-cli-full.md` (CLI repo) and `exodus-v1.3-dashboard-edits.md` (dashboard repo).*
