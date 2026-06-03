# Exodus v1.3 — CLI Audit

**Started:** 2026-06-03
**Auditor:** Lucas (`lukemiha@gmail.com`, Member role, brand `flow2`)
**Scribe:** Claude (terminal — reads saved screenshots, writes findings + fixes)
**For:** Brad (implements) + any downstream AI he hands this to
**Surface under review:** the **Exodus CLI** (`exodus image`, `genesis`, `brand`, the spec wizard, `doctor`) — and the CLI↔dashboard seams it exposes.

**Companion pass:** the **dashboard** audit lives in its own repo (`exodus-v1.3-dashboard`, findings #37–46). This is the **CLI** companion. Finding numbers continue the shared audit sequence — #1–46 were prior dashboard/onboarding/creative passes; **this CLI pass is #47+.**

---

## How to read this doc (for Brad + downstream AI)

Each finding is **self-contained** so it can be lifted out and worked in isolation:

- **ID** — `#NN` finding, `A.NN` the corresponding action item.
- **Area** — which surface (CLI command / flow / component).
- **Severity** — P0 (blocks customer / wrong-brand) · P1 (broken or badly confusing) · P2 (polish / nice-to-have).
- **What / Where / Repro / Screenshot / Expected / Proposed fix / Status** — observed behavior, exact location, steps, verbatim screenshot path, the intended behavior, the suggested change, and state.

Screenshots live in `screenshots/` and are **never edited** — saved exactly as captured. Filenames encode the finding: `NN-short-slug.png`.

---

## TL;DR — running summary

- **#47 (P1)** — **"Native" is mislabeled — it's the category, not an engine.** Native is the *tab*; the two engines under it are **Reptile** and **Copy-Derived**. There is no standalone "Native" engine — yet a run card reads "Creative Suite — **Native**" while badged **Reptile**, because CLI `--type native` silently maps to the Reptile engine. Customer can't tell which engine ran. Fix the taxonomy across CLI + dashboard + run-card labels.
- **#48 (P1)** — **Generation auto-fires a default suite without asking — the config IS the creative call.** Dropping 4 ads fired **three runs in one batch** (Template `auto·1:1` + Copy-Derived 4-concept + Reptile 4-concept) that Lucas never selected. It should *ask first* via a spec step (the Lucas-approved **Engine → Scope → Aspect → Count → Submit** wizard), and ship bounded **run formats (F1–F6)** instead of open spray. Default to **nothing**; never generate unasked output.
- **#49 (P2)** — **No cancel command in the CLI.** Once runs are fired there's no way to stop them. Add `exodus image cancel <runId>` / batch-cancel.
- **#50 (P1)** — **Brand Info (image-gen assets) isn't prompted or validated when empty; two "brand" layers are conflated; no CLI setter.** Image gen ran with founder/product empty while `doctor` said "READY" (that only reflects the partial copy layer). Founder name + product photos are dashboard-only — no CLI to set them.

---

## The architecture (canonical — Lucas, 2026-06-03)

> This is the authoritative model the spec/UX in #47–#50 must conform to. The two
> levers (Steering, Realism) **do not cross**: Steering is Native-only, Realism is
> Template-only.

You start with one input: **ad copy**. It branches into two independent engine families.

```
                          AD COPY
                             │
            ┌────────────────┴────────────────┐
            │                                  │
        NATIVE                             TEMPLATE
   (images from your copy)        (your copy poured into fixed formats)
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

**The two levers, and where each one lives**

| Lever | What it does | Lives on |
|---|---|---|
| **Steering** | injects your own idea/direction into the render | **Native only** (Reptile + Copy-Derived) |
| **Realism** | photographic-realism guardrail | **Template only** (single on/off for all) |

They don't cross. Steering never touches templates; realism never touches native.

**The decision space, in order — four choices:**
1. **Which ads** — one or many
2. **Which engines** — any mix of {Reptile, Copy-Derived, Template}
3. **Native config** — count per engine · aspect · steering (your ideas, optional)
4. **Template config** — auto or manual (which formats + how many each) · realism on/off

---

## Findings

### #47 — "Native" is mislabeled: it's the category, not an engine (CLI `--type native` actually = Reptile)
- **Area:** New batch run modal → **Engine** toggle (Native | Template) **+** run-result cards **+** CLI `exodus image --type native`.
- **Severity:** P1 — a run labeled "Native" is actually the Reptile engine; the customer can't tell what ran, and the vocabulary is inconsistent across CLI / dashboard / cards.
- **What:** "Native" is being used as if it's an engine when it's really the **category**:
  - **Native is the tab/category.** Under it sit **two engines**, each with its own per-aspect image count:
    - **Reptile** — reptile-brain triggers, 13 psychological angles → wild concepts.
    - **Copy-Derived** — native ads built from your copy blocks.
  - There is **no standalone "Native" engine.** But a completed run card reads **"Creative Suite — Native"** while its badge says **Reptile** (see screenshot) — because the **CLI `--type native` maps to the Reptile engine.** So "Native" silently means "Reptile" in the CLI, and the dashboard inherits the mislabel.
  - Lucas: *"There's no fucking native; copy-derived and reptile are both versions of native. There's not a second native one."* Confirmed by the CLI agent that fired the run: *"`--type native` confusingly maps to the Reptile engine — that's why the dashboard badged my 'Native' run as Reptile. A genuine CLI naming bug."*
- **Where:** Engine toggle at top of New batch run modal; result-card title vs badge; CLI `--type` argument.
- **Repro:**
  1. Fire a run with CLI `exodus image --type native` (or pick the Native engine + Reptile in the modal).
  2. Open the run card → title says **"Creative Suite — Native"**, badge says **"Reptile."** Title and badge disagree; "Native" is presented as an engine.
- **Screenshot:** `screenshots/47-native-mislabel-run-cards.png`
- **Screenshot:** `screenshots/48-batch-run-modal.png`  *(shows the Engine "Native | Template" toggle with Reptile + Copy-Derived as the two real engines underneath)*
- **Expected:** One consistent taxonomy everywhere. **Native = category** containing **Reptile** + **Copy-Derived**. "Native" never appears as an engine name; runs are always labeled by the actual engine that ran.
- **Proposed fix:**
  1. **CLI:** deprecate/rename `--type native`. Expose the two real engines explicitly (e.g. `--engine reptile` / `--engine copy-derived`). If `--type native` must stay for back-compat, require an engine sub-choice or alias it transparently and label the run by the resolved engine.
  2. **Dashboard:** keep **Native / Template as category tabs**, but **label every run by its engine** (Reptile / Copy-Derived) — never "Native."
  3. **Make card title + badge agree** (no "Native" title paired with a "Reptile" badge).
- **Screenshot:** `screenshots/48-spec-wizard-1-engine.png`  *(the spec wizard's Engine step already names the real engines — Reptile / Copy-Derived — and flags inline that "CLI confusingly calls [Reptile] --type native"; this is the fix surfaced in UI)*
- **Status:** open — CLI-level + dashboard-level. (See memory `reference_exodus_image_engines` for the canonical taxonomy.)

### #48 — Generation auto-fires a default suite without speccing; needs a config step + zero unasked output
- **Area:** Image/copy generation flow — CLI `exodus image` **and** the New batch run modal.
- **Severity:** P1 — produces output the customer never requested (wasted spend + time); for image gen the **configuration IS the creative decision**, so skipping it defeats the point.
- **What:**
  - Dropping **4 ads at once** auto-fired **three runs in a single batch** (all stamped Jun 3, 1:59 PM):
    - **Template** — `auto · 1:1`, "1 ad · 4/4 images"
    - **Copy-Derived** — "4 concepts · 4/4 images"
    - **Native / Reptile** — "4 concepts · 4/4 images"
    - None of these were explicitly chosen. Lucas: *"You're just going and generating shit I didn't even ask for."*
  - **Before generating, the system should ask** (this is the spec the run needs):
    - **Native engines:** Reptile? Copy-Derived? **how many each** per aspect?
    - **Template:** auto vs **manual** mode; **which** of the **33 ad-types**; **per-type quantities** (e.g. testimonial:3, hero:2); model (**gpt-image-2 / nano-banana-pro**); realism on/off.
    - **Steering / image direction** (optional) + **aspect** (1:1 feed / 9:16 reels).
  - **Steering is a specific, optional refinement** the operator gives *if they want* — not a default the engine should assume. (Reinforces #37.)
  - **Brand-profile nuance — corrected (see #50):** an initial `doctor` read said "foundation: READY" and the run proceeded as if brand context existed. That was misleading on two counts: (a) the **copy foundation** is only *partial* (Audience Concerns ✅, Brand Voice ❌, Core Offer ❌); (b) the thing that actually feeds **image** gen — **Settings → Brand Info** (founder name + product photos) — is **completely empty** for flow2, and the run was **never prompted or validated against it.** So it's both a missing-**ask** (this finding) *and* a missing-**validation** of empty assets (#50). Don't conflate the two brand layers.
- **Where:** CLI `exodus image` (fires a suite from ad copy with no spec prompt); dashboard New batch run modal (the fields exist but a suite can fire without an explicit per-engine/per-template spec).
- **Repro:**
  1. Feed ~4 ads' copy into the generation flow.
  2. Observe **3 runs** fire (Template + Copy-Derived + Reptile) with **no prompt** for engines, counts, template ad-type, mode, model, or realism.
- **Screenshot:** `screenshots/47-native-mislabel-run-cards.png`  *(the three unasked runs from one batch)*
- **Screenshot:** `screenshots/48-batch-run-modal.png`  *(the inputs that should be an explicit spec, not silent defaults)*
- **Expected:** A **spec / confirm step before any generation.** The user picks engines + per-engine counts, template mode + ad-type(s) + per-type quantities + model + realism, optional steering, aspect — **and nothing generates that wasn't asked for.** Default state = zero engines selected.
- **✅ Reference design — Lucas-approved (build to this):** the CLI now drafts the spec as a **step-through wizard** with a tab bar **Engine → Scope → Aspect → Count → Submit** — *nothing fires until Submit.* Lucas on seeing it: *"it needs to look like this — how can we make it explicit?"* Each step is an explicit choice with plain-language consequences and a **"Chat about this"** escape hatch:
  - **Engine** (multi-select): Reptile · Copy-Derived · Template · "Type something." Each option states what it is; Template's note says *"33 ad-types, auto/manual mode, per-type quantities — I'll ask which ad-types + counts next if you pick this"* (conditional branching). The Reptile note also explicitly says *"this is what CLI confusingly calls --type native"* — surfaces the #47 mislabel right in the UI. → `screenshots/48-spec-wizard-1-engine.png`
  - **Scope** ("Which of the 4 ads should I run?"): *Just one, go deep* · *All 4, separate runs* · *Ad #N only* · "Type something." → `screenshots/48-spec-wizard-2-scope.png`
  - **Aspect** ("What aspect ratio(s)?"): 1:1 feed · 9:16 reels · "Type something." → `screenshots/48-spec-wizard-3-aspect.png`
  - **Count / Submit:** per-engine quantities, then a single explicit Submit.
- **🧩 Open design — the config LOGIC (Lucas's question):** the hard part is the combinatorial space — **N ads × {Reptile, Copy-Derived, Template} × {auto | manual} × per-type counts × realism on/off**. Naïve "12 of everything on every ad" = ~150+ renders with no read on what's working. Proposed logic (architecture-level; CLI agent is pulling the real ad-type + reptile-trigger lists to put concrete numbers on it):
  1. **Make volume opt-in, not multiplicative-by-default.** The common path should be cheap: pick engine(s) → Scope = "one, go deep" → accept small count defaults → Submit. The full matrix is a power-user expansion, never the default.
  2. **Scope is the spend governor** (decide *before* counts): *one ad, go deep* (cheapest signal / stress test — the right default) vs *all N, separate runs* (breadth, more spend). Scope sets how many ads get rendered.
  3. **Count is PER-ENGINE, not per-ad×per-type×per-angle.** Native engines vary their own angles internally — Reptile samples from its 13 psychological triggers, Copy-Derived from the copy blocks — so the user sets a single per-engine concept count (e.g. 3), and the engine handles type variety. Don't expose 13 angle-counts.
  4. **Template is its own branch** (it has structure Native lacks):
     - **auto** = system picks a sensible ad-type spread (low-config default).
     - **manual** = user picks specific ad-types + a count each (e.g. `founder-note:2`, `testimonial:3`).
     - **Realistic enhancer** (on/off) is **Template-only** — a photographic-realism guardrail on the render prompt that doesn't rewrite the raw Template output (see screenshot). One per-batch toggle; default **off** unless the product needs photographic realism.
  5. **Signal-first defaults:** start narrow (1 strongest ad · each chosen engine at ~3 · Template auto · realism off ≈ ~9 renders), read the winners, *then* scale the winner — instead of spraying 150 up front.
- **Screenshot:** `screenshots/48-realistic-enhancer-toggle.png`  *(the Template-only realism guardrail toggle)*
- **📐 Run formats (the bounded presets Lucas asked for — build these as selectable formats):** instead of an open combinatorial form, ship a menu of **named formats**, each a complete, testable run config. Native count = concepts per engine (engine varies its own angles); Template = ad-types + per-type counts + realism (template-only); aspects 1:1 feed / 9:16 reels.
  | Format | Ads | Engines & counts | Template | Realism | Aspect | ≈ Renders | Use |
  |---|---|---|---|---|---|---|---|
  | **F1 · Native Stress Test** | strongest 1 | Reptile 3 + Copy-Derived 3 | — | — | 1:1 | ~6 | fastest concept read |
  | **F2 · Native Breadth** | all | Reptile 2 + Copy-Derived 2 each | — | — | 1:1 | ~16 (4 ads) | which copy wins |
  | **F3 · Template Auto** | 1 | — | auto (system picks types) | off | 1:1 | auto | what templates yield, no fuss |
  | **F4 · Template Manual** | 1 | — | manual: pick 2–3 types + count (e.g. founder-note 2 / testimonial 2 / hero 2) | on | 1:1 | per picks | deliberate template formats |
  | **F5 · Winner Scale-Up** | the winner | Reptile 4 + Copy-Derived 4 + Template auto 4 | auto | on | 1:1 + 9:16 | ~24 | full coverage on a proven concept |
  | **F6 · Reels Pass** | chosen | chosen engines | optional | as set | 9:16 only | varies | reels/stories placement test |
  - **Principle:** each format is bounded and answers one question — never "12 of everything on every ad." Start at F1, scale the winner with F5. (Concrete type/trigger lists for F4 land when the CLI agent returns them.)
- **🚫 The deeper rule — ELICIT, never assume (Lucas, 2026-06-03, emphatic):** it is **not enough to "ask" by presenting a fully pre-decided plan.** The CLI did exactly that — staged all 4 ads, assigned engines + specific Reptile triggers + template formats per ad, totaled ~156 images, then said "give me 2 knobs and I fire." That's *assuming*, dressed as asking. Lucas: *"Stop assuming you know what the fuck I want. I will tell you… You can say 'do you want me to just do it for you?' but you have to ASK."* The spec step must **elicit each choice from the operator**; a "do it for me" path is allowed **only as an explicit option the user selects**, never as a default or a fait accompli.
- **✅ APPROVED WIZARD (converged 2026-06-03) — build to this (supersedes the Engine→Scope→Aspect→Count sketch above):** a **"who decides" gate**, then a **menu of questions** — one decision per screen, tab bar + ◄►, a "Chat about this" escape on every step. Replaces the rejected free-text "here are the slots, type it / Go" dump (`screenshots/48-tell-me-slots.png`; Lucas: *"can't we do this with a menu of questions?"*).
  - **Step 0 — Who decides** *(gate)*: **1) I'll tell you** (you give settings per-ad or globally; system builds exactly that, no creative calls) · **2) Do it for me** (system picks engines/formats/realism/counts and runs) · Type something · Chat. *(PNG lost to cache rotation — re-paste to archive. Clearer copy, per Lucas's "make it more readable":)*
    > **Who picks the settings?**
    > For these 4 ads, who chooses the setup — which engines run, which template formats, realism on or off, and how many of each?
    > **1. I'll tell you** — You give me the settings (one ad or all of them) and I build exactly that. I decide nothing on my own.
    > **2. Do it for me** — I pick the engines, formats, realism, and counts for all 4 ads, then run it.
    > **3. Type something else** · **4. Talk it through first**
  - **Wave 1 — Native:** **Ads** (multi-select; **default ALL ads selected** — Lucas: *"probably they want to run ALL ads"*) → **Engines** → **Aspect** → **Native count** → Submit. → `screenshots/48-menu-of-questions-ads.png` (+ step shots `48-spec-wizard-1-engine.png`, `-2-scope.png`, `-3-aspect.png`)
  - **Wave 2 — Template:** **Tmpl mode** (Auto = system picks ad-types, total count per ad · Manual = you pick which of the 33) → **Realism** (Off/On, one switch all templates) → **Tmpl count** (1/3/5 per type-per-ad; Auto = total per ad, Manual = per format) → Submit. → `screenshots/48-wizard-w2-mode.png`, `48-wizard-w2-realism.png`, `48-wizard-w2-count.png`
  - **Wave 3 — Manual ad-types** (only if Tmpl mode = Manual): pick which of the **33 ad-types** (grouped: social-proof · authority/story · demo/breaking · science/data · listicle/steps · problem/meme · product · bold/graphic) — same set across all ads, or per-ad. → `screenshots/48-wizard-manual-adtypes.png`
- **Proposed fix:**
  1. **Insert this configuration step before any run** — CLI: the step-through wizard above (Engine→Scope→Aspect→Count→Submit). Dashboard: make submitting the modal the **only** way to fire — no implicit suite.
  2. **Template config surface:** which ad-type(s) of the 33, per-type quantities, auto vs manual, model (gpt-image-2 / nano-banana-pro), realism — all explicit choices (the wizard branches into these when Template is picked).
  3. **Default to nothing.** No engine fires until the user picks + hits Submit; never fire a full suite implicitly.
  4. **Validate assets at the spec step** — if a chosen path needs Brand Info that's empty, warn/prompt (ties to #50), don't silently render.
  5. **Cross-ref #49** — once fired, runs can't be cancelled, which makes the auto-fire worse.
- **Status:** open — reference design captured (above). **Needs Brad input** on porting the wizard to the dashboard modal vs keeping it CLI-only. (See memory `feedback_exodus_spec_before_generating`.)

### #49 — No cancel command in the CLI
- **Area:** CLI — run lifecycle (`exodus image` / batch runs).
- **Severity:** P2 (capability gap) — escalates the impact of #48.
- **What:** Once runs are fired there is **no way to stop them.** Surfaced this session: the 3 unasked runs from #48 had to run to completion because no cancel exists. CLI agent: *"I can't cancel the 3 runs I fired — there's no cancel command in the CLI. They'll finish on their own."*
- **Where:** CLI run commands; dashboard run cards (no cancel control observed there either).
- **Repro:** fire any run → look for a way to cancel it → none exists.
- **Expected:** a cancel path — `exodus image cancel <runId>` (and/or batch-cancel), plus a cancel control on the dashboard run card.
- **Proposed fix:** add a cancel command keyed on runId (and batch id); surface a Cancel button on in-progress run cards; free the queue slot on cancel (ties to the Genesis VPS 1-concurrent constraint — v1.2 A.44).
- **Status:** open — CLI gap.

### #50 — Brand Info (image-gen assets) isn't prompted or validated when empty; two "brand" layers are conflated; no CLI setter
- **Area:** Settings → **Brand Info** tab + the generation flow's readiness check (`doctor`) + CLI brand surface.
- **Severity:** P1 — image gen runs with **no founder/product reference** while reporting "ready," so ads can't show the right founder/product (literally the tab's stated purpose).
- **What:** Three tangled problems:
  1. **Fired without prompting for empty Brand Info.** Image gen ran while **Settings → Brand Info** was completely empty — **Founder** blank (placeholder "e.g. Jordan Lee"), **Product photos** "No product images uploaded yet." Nothing warned or asked. The tab's own header: *"Details about Flow2… These feed image generation so your ads show the right founder and product."* — and it had nothing in it.
  2. **Two "brand" layers get conflated, and the readiness signal is misleading.** There are **two distinct stores**:
     - **Copy foundation** (`state/brand-profile.md`) — the *writing* layer. For flow2: Audience Concerns ✅, **Brand Voice ❌ "not yet filled in"**, **Core Offer ❌ "not yet filled in"** — only *partial*.
     - **Brand Info** (Settings → Brand Info) — the *image-gen reference* layer (founder name + product photos). For flow2: **empty.**
     - `doctor` reported **"foundation: READY"**, which reflects only (and even then partially) the copy layer — **not** Brand Info. A customer reading "READY" would reasonably think image gen has what it needs. It doesn't.
  3. **No CLI setter for Brand Info.** The CLI `brand` command only **lists/switches** brands; the only "founder" reference in source is a *template ad-type* (`founder-note`), **not** a brand-info field. So **founder name + product photos are dashboard-only** — they can't be set programmatically (another CLI gap).
  - Lucas: *"It didn't ask me for brand info even though my stuff was empty."*
- **Where:** Settings → Brand Info (Founder field + Product photos drop-zone); the pre-run `doctor`/readiness check; CLI `brand`.
- **Repro:**
  1. Leave Settings → Brand Info empty (founder blank, no product photos).
  2. Run image gen → it proceeds; **no prompt** for founder/product; `doctor` says "foundation: READY."
  3. Try to set founder/product photos from the CLI → no command exists.
- **Screenshot:** `screenshots/50-brand-info-empty.png`  *(Brand Info tab — founder blank, "No product images uploaded yet")*
- **Screenshot:** `screenshots/50-no-cli-setter-brand-info.png`  *(CLI confirming there's no Brand-Info setter; `brand` only lists/switches; `founder-note` is a template ad-type, not a field)*
- **Expected:** before a run that needs founder/product, the system **checks Brand Info and warns/prompts if empty** (don't silently render generic); `doctor` reports **both** layers separately and honestly (copy foundation completeness *and* Brand Info presence); a **CLI path** exists to set founder + add product photos.
- **Proposed fix:**
  1. **Run-time validation:** before asset-dependent runs, check Brand Info; if founder/product missing, warn or prompt inline (wire into the #48 spec wizard's asset-validation step).
  2. **Honest readiness:** make `doctor` (and any "READY" badge) report the **two layers distinctly** — copy foundation (with the missing Brand Voice / Core Offer called out) and Brand Info (founder/product present?). One "READY" must not paper over an empty image-gen layer.
  3. **Disambiguate the two layers in the UI** so it's obvious which feeds writing vs image gen.
  4. **Add a CLI setter** for Brand Info (set founder, add/remove product photos) so it isn't dashboard-only.
- **Note (don't conflate with #39):** #39 is "templates must *declare/receive* the right inputs"; **#50** is "the system claims ready, never validates the empty assets, splits the data confusingly, and gives no CLI to fill it." Related, distinct.
- **Status:** open — **needs Brad input** on unifying/labeling the two layers and where the CLI setter lives.

---


---

## Action index (for Brad)

| Action | Finding | Severity | One-liner | Status |
|---|---|---|---|---|
| A.55 | #47 | P1 | Fix "Native" taxonomy: rename CLI `--type native` (→ Reptile); label runs by engine, never "Native"; make card title+badge agree | open |
| A.56 | #48 | P1 | Add spec step before generation (build to the Engine→Scope→Aspect→Count→Submit wizard + the F1–F6 run formats); default to nothing; validate assets; never auto-fire a suite | open · needs-brad-input |
| A.57 | #49 | P2 | Add CLI cancel (`exodus image cancel <runId>`/batch) + dashboard Cancel button; free the queue slot | open |
| A.58 | #50 | P1 | Validate Brand Info before asset-dependent runs; make `doctor` report both brand layers honestly; disambiguate copy-foundation vs Brand-Info; add CLI setter for founder/product | open · needs-brad-input |

---

## Open questions for Brad / Lucas

- **#47:** keep CLI `--type native` as a back-compat alias (resolving to Reptile) or hard-rename to `--engine reptile`?
- **#48:** port the spec wizard into the dashboard modal, or keep the wizard CLI-only and just stop the modal's implicit suite?
- **#50:** unify the two brand layers (copy foundation + Brand Info) into one surface, or keep separate but cross-validate? And where should the CLI Brand-Info setter live (`exodus brand info …`)?
- **Brand-isolation (flag):** is `flow2` genuinely the Adonis Vitality brand (so pulling Mike Blanchard + adonisvitality.com product images is correct), or a clean test brand (so that would contaminate the audit per the fresh-content hard rule)?
