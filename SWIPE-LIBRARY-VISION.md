# Swipe Library — what we want (copy-ready note for Brad)

**The core ask:** capture and surface the metadata ScrapeCreators **already returns**, and stop capping the library at 200. Right now Exodus stores only `headline / body / CTA / transcript` and caps `--list-swipes` at 200 — it's discarding the rest and not paginating.

## What ScrapeCreators already gives us per ad (we're dropping most of it)
- `impressions_with_index` (impressions text + index) + `reach_estimate` — **impression / reach data**
- `start_date` / `end_date` (Unix) — **dates**
- `total_active_time` (seconds) — **longevity, exact**
- `collation_count` — **number of variants in the campaign** (winning proxy)
- `spend`, `is_active` / `status`, `publisher_platform`
- `cursor` + `searchResultsCount` — **pagination + true total (so: way more than 200 available)**

## What we want to do with it
- **Swipe/save** any competitor ad into the library.
- **Sort** by: date · longevity (`total_active_time`) · variant count (`collation_count`) · impression proxy.
- **Score** = combine **impressions × longevity** (and variant count) into one "what's working" number. Multiply the proxies.
- **Filter** by brand, by date range (e.g. last 7 days), by active status.
- **Semantic search on hooks** — search the opening hooks/copy, cluster by hook type, "find me hooks like this one."
- **No 200 cap** — paginate via `cursor`; show true total ("showing 50 of 1,240").

## Mining fix
- Mining pulls a brand's **entire catalog** — multi-product brands flood the library with off-niche ads. Let us **niche-filter / scope** which ads get pulled.

That's it. The data exists upstream; this is mostly "store it + surface it + let me sort/search it."
