## Context

The app is a front-end-only Vue 3 prototype backed by mock data through `marketService`. The deal hunter has to work the same way: deterministic, no external API, and easy to swap for a real backend later.

## Decisions

- **Pure engine, thin store.** `services/dealHunter.ts` holds all scoring as pure functions (`transportCost`, `evaluateDeal`, `huntDeals`, `checkBeforeBuying`, `scanWatchlist`). `dealStore` only wires them to reactive state and persistence. Results are computed, so they re-rank when prices, trust data or preferences change.
- **Real ("landed") cost = price + round trip.** Transport model (NT$, per direction, doubled): walk 0; YouBike 10 per started 6 km; MRT 20 + 3/km capped at 65; taxi 85 + 25/km beyond 1.25 km.
- **Deal score (0–100).** `0.65 × savings% vs new retail (on real cost) + 0.35 × seller trust`, ±5 for a falling/rising price, −20 reserved, −15 over budget, −5 unverified seller, −10 beyond max distance. Verdicts: ≥70 great, ≥55 good, ≥40 fair, else skip.
- **Transparency.** Every hunt and price check names all listings it compared, and shows the time prices were checked.
- **Quiet watchlist.** Each watch keeps a per-listing baseline price. Drops below the threshold keep the old baseline so small drops accumulate; an alert resets the baseline so the same drop is never reported twice. New watches seed baselines without alerting.
- **Simulated price feed.** `marketService.fetchPriceUpdates(round)` returns scheduled batches from `scheduledPriceRounds`; an empty batch exercises the quiet path.
- **No autonomous actions.** "Ask seller" opens a confirmation dialog; only on confirm does the store create/open the conversation and navigate to chat.

## Non-Goals

- Real price scraping, scheduled background checks or push notifications.
- Auto-negotiation, reservation or payment.
- Geolocation-based distance (uses each listing's existing `distanceKm`).

## Risks / Trade-offs

- Reference prices are hand-entered mock values; a real system needs a price source.
- Mock price changes mutate in-memory listings and reset on reload, while watch baselines persist; baselines only move up on reload, so no false alerts are produced.
