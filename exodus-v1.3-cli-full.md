# Exodus v1.3 — CLI / Image-Gen Edits & Feedback

**Date:** 2026-06-03
**CLI version under test:** 2026.6.300 (updated from 2026.6.100 this session)
**Brand:** flow2 (test brand) · Founder set to **Mike Blanchard** · Product = Adonis Vitality **FLOW (Men's Vitality Blend)** tub
**Tester:** Lucas · driven via Claude (terminal-only)
**Scope:** Stress-test of the image-generation path (paste ad → images) across all engines, plus copy/ideation surface review.

> This doc has 5 parts:
> A. App findings & requested changes (for Brad)
> B. Process feedback (how Claude should run these sessions)
> C. The canonical image-gen architecture
> D. Reference data (engines, ad-types, caps, where things live)
> E. Record of the run we actually executed

---

## PART A — APP FINDINGS & REQUESTED CHANGES (for Brad)

Severity: 🔴 high · 🟠 medium · 🟡 low/polish

### A0. 🔴🔴 [#1 ISSUE — THE big one] Steering MUST be an explicitly-requested, first-class input — including steering-ONLY (no ad copy) and steering-EMPHASIS runs
- **What:** The flow **MUST ask the operator for their specific steering instructions** — every time. Steering cannot be skipped, assumed empty, or buried as an afterthought. Two first-class modes must work:
  1. **Steering-only (no ad copy):** a run *for* an ad where the operator deliberately does **not** include the ad copy — they want **only their steering instructions** to drive the render. (Architecturally already supported: Native `--steer` with no copy → steering becomes the brief — but the flow must *ask/offer* this, never force copy.)
  2. **Steering-emphasis:** copy IS included, but the operator wants to **emphasize / weight their steering** as the primary driver of the image.
- **Lucas (verbatim, 2026-06-03 — every word, as requested):**
  > "the ONLY big issue OVERALL and iTS REALLY FUCKING IMPROTANT... IT MUST Ask for my specific steering information because sometimes it's for an ad, but I don't even want to include the ad copy. I just want my steering instructions, or I want to emphasize my steering instructions. That is fucking, fucking, fucking, fucking, fucking, fucking, fucking, fucking important, and include every single one of those fucks in this GitHub."
- **Why it matters:** Steering is the operator's single most important lever — it injects *his own* creative direction into the render. If the flow assumes ad copy is required, or treats steering as optional-at-the-bottom, his core use case (his ideas driving the image, **with or without** the ad copy) is blocked. This is the #1 issue overall.
- **Requested change:**
  1. In the **Native** config wave, **always ASK for steering instructions** as a prominent, first-class free-text input — not "(optional)" at the bottom.
  2. **Support steering-only runs:** allow a run with **no ad copy** when steering is provided (Native engines render from steering as the brief). Never enforce copy as required when steering is present.
  3. **Support steering-emphasis:** a way to mark steering as the primary/weighted driver when copy is also present.
  4. Steering stays **Native-only** (per the clean split) — surface it in the Native wave and **ask for it every time**.

### A1. 🟠 CLI `--type native` mislabels the **Reptile** engine
- **What:** `exodus image --type native` (and `creative native`) creates a run the dashboard badges as **Reptile**. There is **no standalone "native" engine.**
- **Reality:** "Native" is a dashboard **tab / category** containing **two** engines: **Reptile** (13 psych triggers → wild concepts) and **Copy-Derived** (ads built from your copy blocks).
- **Why it matters:** Operator thinks "native" is a third engine and that there are two different native runs. CLI vocab (`native | copy-derived | ref-match`) doesn't match the dashboard vocab (`Reptile | Copy-Derived`).
- **Requested change:** Rename CLI `native` → `reptile` (keep `native` as a deprecated alias), or group the CLI under a `native` parent with `reptile`/`copy-derived` sub-engines to mirror the dashboard. Update all help text + run labels so the CLI label and dashboard badge match.

### A2. 🔴 No `cancel` / `stop` for in-flight runs
- **What:** Once a creative or template run is fired (especially `--no-wait`), there is **no way to abort it** from the CLI. `creative` help has no cancel; no `template cancel`.
- **Why it matters:** A mistaken or oversized run (e.g., the 3 premature runs fired early this session) **cannot be killed** — it runs to completion and bills. This is the single biggest cost-control gap.
- **Requested change:** Add `exodus creative cancel --id <run>` and `exodus template cancel --id <run>` (+ a dashboard cancel button). Bonus: `exodus cancel --all-running`.

### A3. 🔴 No CLI setter for **Brand Info** (founder + product images) — and doctor doesn't catch it empty
- **What:** Settings → **Brand Info** (Founder name + Product photos) is **dashboard-only**. The `brand` command only lists/switches brands. There is **no CLI** to set the founder or upload product images.
- **Compounding bug:** `exodus doctor` reported **"brand-profile (Genesis depth) … filled"** and **"foundation READY"** while Brand Info was **completely empty** (no founder, "No product images uploaded yet"). These are **two different things** and doctor conflates them:
  - "brand-profile / foundation" = the **copy** layer (audience concerns, brand voice, core offer) → feeds the **writer**. *(And even this was partial: Brand Voice + Core Offer = "not yet filled in.")*
  - "Brand Info" tab (founder + product photos) = feeds **image generation** so ads show the right founder/product. *(This was empty.)*
- **Why it matters:** Image runs against empty Brand Info **invent a fake product/founder** — garbage creative — with nothing warning you. Also blocks any scripted brand onboarding.
- **Requested change:**
  1. Add CLI setters: `exodus brand set-founder "<name>"`, `exodus brand add-product-image <path...>`, `exodus brand info` (show current).
  2. Doctor must check **Brand Info image assets** separately and **WARN/FAIL** if founder or product images are empty before image runs — don't let an empty Brand Info pass as "READY."
  3. Clarify naming so "foundation" (copy) vs "Brand Info" (image assets) aren't conflated anywhere.

### A4. 🟠 Manual template caps at **50 images per run** (hard error, no auto-split)
- **What:** `template run --mode manual --quantities "..."` errors **"manual mode supports at most 50 requested images"** when the total exceeds 50. Running all 33 ad-types × 2 = 66 **failed outright**.
- **Why it matters:** You can't run the full ad-type set at ≥2 each in one shot; the operator (or Claude) has to **manually split** into ≤50 batches.
- **Requested change:** The front door should **auto-split** a >50 manual request into sequential ≤50 batches (or warn with a suggested split) instead of erroring. Surface the cap in `--help`.

### A5. 🟠 Template has **no CLI status** endpoint
- **What:** `template run` prints only a dashboard URL; the Convex HTTP route is **POST-only**, so there's no CLI polling. (Native/creative DO have `creative status --id`.)
- **Why it matters:** Can't track or confirm template completion from the terminal; must watch the dashboard.
- **Requested change:** Add a GET status route + `exodus template status --id <run>` returning progress / imageCount / terminal state (parity with `creative status`).

### A6. 🟠 Dashboard **manual template picker** UI is unusable
- **What:** Per Lucas (screenshot), the manual ad-type selection screen is "displayed horribly" and offers **no clean way to set how many of each** ad-type.
- **Requested change:** Redesign the manual picker as a clear scannable list/grid of the 33 ad-types, each with a **numeric quantity input** (and a running total vs the 50 cap). Mirror what the CLI `--quantities "type:N"` does.

### A7. 🟡 Steering only works via the `image` front door (parity gap)
- **What:** `--steer` / `--direction` is passed through by `exodus image` for all engines, but the **`creative` and `template` commands invoked directly do NOT accept `--steer`.**
- **Requested change:** Accept `--steer` on `creative native` / `creative copy-derived` too for parity (note: per Lucas, steering should remain a **Native-only** concept — keep it off templates by design).

### A8. 🟡 No cost/scale preview before large image batches
- **What:** Nothing summarizes "this will generate N images / N runs" before firing.
- **Requested change:** A `--dry-run` (or auto preview) on `image`/`template` that prints the total render count + run plan before committing. Especially important given A2 (no cancel).

---

## PART B — PROCESS FEEDBACK (how Claude should run these sessions)

These are the corrections Lucas gave Claude this session. **All are durable rules for future Exodus work.**

### B1. Spec BEFORE generating — never auto-fire
The run config **is** the creative decision. Do **not** paste an ad and immediately generate. Especially when multiple ads are dropped at once, the first question is "what do you want done with these," not "render everything." *(Burned: auto-fired native + copy-derived + template on Ad #1 unasked.)*

### B2. Do the LITERAL ask — don't substitute your own plan
Execute exactly what Lucas specified. Do **not** invent a "calibration wave," drop engines, or change his counts/scope after he's already decided. No re-litigating settled decisions.

### B3. Don't ASSUME what he wants per item
When given an ad, do **not** pre-decide which engines or formats "fit" it (e.g., "Ad #1 is emotional so Reptile + testimonial"). That's his call. Present the options **neutrally**; he assigns them.

### B4. You may offer to do it — but you must ASK
It's fine to say **"Do you want me to just do it for you?"** — but **ask**; never assume the answer and proceed.

### B5. Use MENUS for multi-knob config
When there are many settings, drive them with menu questions (waves), not walls of prose. Lucas explicitly asked for "a menu of questions." For large open inputs (e.g., a count), **ask the value** rather than forcing preset options.

### B6. Clean, scannable output
Tables and tight lists, not paragraphs. No clutter. ("Just give me the list." / "displayed horribly.")

### B7. Verify before asserting — don't conflate facts
Don't claim state you haven't checked. *(Burned: said "brand profile is set" when only the copy foundation existed and Brand Info was empty.)* Distinguish similar-sounding things (copy foundation vs image Brand Info).

### B8. Confirm scale on irreversible / costly actions
Large paid render batches + **no cancel** = confirm the total first. *(The 360-render confirm before firing was correct and expected.)*

### B9. Surface limitations honestly, in real time
Flag gaps as they're hit (no-cancel, 50-cap, dashboard-only Brand Info) instead of glossing over them.

### B10. Always give full `file://` links
Never bare paths — full clickable `file://` URLs (spaces as `%20`) for every file mention.

---

## PART C — CANONICAL IMAGE-GEN ARCHITECTURE

**One input (ad copy) → two engine families → four choices.**

```
                          AD COPY
                             │
            ┌────────────────┴────────────────┐
            │                                  │
        NATIVE                             TEMPLATE
   (images from your copy)        (copy poured into fixed formats)
            │                                  │
    ┌───────┴───────┐                  ┌───────┴───────┐
  REPTILE      COPY-DERIVED          AUTO            MANUAL
 13 psych      literal ads      system picks      you pick the
 triggers →    from your        the ad-types      ad-types + how
 wild          copy blocks                        many of each
 concepts
            │                                  │
   ▸ count per engine                 ▸ 33 ad-types available
   ▸ aspect (1:1 / 9:16)              ▸ realism: ON or OFF
   ▸ STEERING ◄ your ideas              (one switch, whole batch)
```

**The two levers, and where each lives (the clean split):**

| Lever | What it does | Lives on |
|---|---|---|
| **Steering** (`--steer`) | injects *your own idea/direction* into the render | **Native only** (Reptile + Copy-Derived) |
| **Realism** (`--realism`) | photographic-realism guardrail | **Template only** — single on/off, all-or-nothing |

They never cross: steering never touches templates; realism never touches native.

**The decision space, in order — four choices:**
1. **Which ads** — one or many
2. **Which engines** — any mix of {Reptile, Copy-Derived, Template}
3. **Native config** — count per engine · aspect · steering (optional)
4. **Template config** — auto OR manual (which formats + how many each) · realism on/off

---

## PART D — REFERENCE DATA

### Engine vocabulary
- **CLI accepts:** `native` (= Reptile), `copy-derived`, `ref-match`, `template`.
- **Dashboard shows:** Native tab → **Reptile** + **Copy-Derived**; **Template** tab separate.
- **`ref-match`** = generate images matching a reference image (`creative ref-match --refs <id,id>`). Needs existing `creativeSuiteImages` IDs — not usable from a fresh paste.

### Steering
- Flag: `--steer "<direction>"` (alias `--direction`). "Steers every image in the batch."
- Works **only via `exodus image`** (not `creative`/`template` direct — see A7).
- Native quirk: `--steer` with **no copy** = steering becomes the brief (no-copy render).
- Granularity = **per run**. Apply same string across an ad's runs = per-ad; across all = global.

### Realism (template only)
- `--realism off | realistic` — single per-run guardrail for the whole batch (not per-type).

### Aspect / model
- Aspect: `1:1` (feed) · `9:16` (reels). [`4:5` accepted by creative engines.]
- Template model: `gpt-image-2` (default) · `nano-banana-pro`.

### Caps
- **Manual template: ≤ 50 images per run** (hard error above; must split — see A4).

### The 33 template ad-types (`exodus template ad-types`)
`testimonial · multi-testimonial · ugc · comment · happy-avatar · founder-note · handwritten · holding-sign · writing-on-body · native-news · breaking-news · screenshot · scientific · statistics · infographic · comparison · before-after · step-by-step · carousel · quiz-interactive · post-it-notes · problem-solution · cost-of-inaction · product-breakdown · hero · receipt · bold · headline · meme · collage · lofi · animation · sale-promotional-offer`

### The 13 Reptile triggers (`exodus template reptile-triggers`)
`ultra-real · bizarre · voyeur · suffering · gory · sexual · primal-fear · odd-contrast · inside-joke · time-warp · victory-lap · selfie · uncanny-objects`
*(Reptile auto-samples across these — you set a total count, not per-trigger.)*

### Where things live
- **Brand Info** (founder + product photos): Dashboard → **Settings → Brand Info**. Dashboard-only (see A3).
- **Copy foundation** (audience/voice/offer): `state/brand-profile.md` + dashboard Settings → Brands.
- **Run status:** `exodus creative status --id <run>` (native/creative) · template = dashboard only (A5).
- **Library / past runs:** `exodus browse`.

---

## PART E — RECORD OF THE EXECUTED RUN (2026-06-03)

**Config:** all 4 ads · Reptile 12 + Copy-Derived 12 (Native) · Template manual, all 33 ad-types × 2, realism **ON** · aspect 1:1 · steering off · against the real FLOW product. **Total = 360 renders.**

**Native (96 images) — pollable via `creative status`:**
| Ad | Reptile | Copy-Derived |
|---|---|---|
| #1 | `rx74rg5nvnza38a5ttsydntfjd87ybwn` | `rx7ejhxvm8tz81qqfz52wmn8ss87znmh` |
| #2 | `rx78dvjpnkz19wxah4s516e9t587yhv3` | `rx7c013d0mkzsynr596d08j0qh87ymy4` |
| #3 | `rx7a29h0wd5m8cvdp16bfz65e187zgad` | `rx7d4k91r9htrnjm3wp0xtz3kd87yrb2` |
| #4 | `rx7322b017m3wf37jgzc8t040587ymrx` | `rx78aa2gkse3yj9cch15beg57587z0gh` |

**Template (264 images) — split 50 + 16 per ad due to the 50 cap (A4); dashboard status only:**
| Ad | Part A (25 fmt ×2 = 50) | Part B (8 fmt ×2 = 16) |
|---|---|---|
| #1 | `th77rhkf7jkz562s13sh5rapjn87zga5` | `th72r1273h58mv5hka9cre6yxh87yvt0` |
| #2 | `th7deht2spjn6wb31cj92qnnr187yzd9` | `th755kpyc72hvp0fx3wtqtqrxn87yx1m` |
| #3 | `th78p430rk2d2q0xekh8evnesh87z0rb` | `th741nfzs9yrmk6wsnb4nq9h3h87z5a9` |
| #4 | `th76wrf8txap9681v2f3sj001h87yp1g` | `th7c7pb0gqdjgddcw738j6dq5h87z0nw` |

**Earlier premature runs (Ad #1 only, fired before the process was corrected — product is invented, ignore):**
`rx7c9cv3cdw83pcdhbdzt29djd87zaz8` (reptile) · `rx7f0s9230nqphwtnzkqjykz4d87y99d` (copy-derived) · `th70t8f43d6dw1g7vrta2we82h87yn8k` (template).

**Source assets staged:**
- Ad copy: `file:///tmp/exodus-ad1.txt` … `file:///tmp/exodus-ad4.txt`
- Product photos (downloaded from adonisvitality.com): `file:///Users/lucasmills/Desktop/flow2-brand-info/flow-product-tub.png` · `file:///Users/lucasmills/Desktop/flow2-brand-info/flow-hero.png`

---

*End of v1.3 CLI edits.*
