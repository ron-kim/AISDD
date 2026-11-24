## 1. Data

- [x] 1.1 Add deal hunter types (pricing, preferences, query, evaluation, watch, alert).
- [x] 1.2 Add listings, reference prices, price history and simulated price rounds to mock data.
- [x] 1.3 Expose pricing and price updates through `marketService`.

## 2. Engine and state

- [x] 2.1 Implement transport cost, deal scoring, hunting, price check and watchlist scan as pure functions.
- [x] 2.2 Add `dealStore` with persisted preferences, watchlist and alerts.
- [x] 2.3 Add `ensureConversation` so a confirmed contact always opens the right chat.

## 3. UI

- [x] 3.1 Add the `/deals` page: setup, hunt, check before buying, watchlist, alerts, contact confirmation.
- [x] 3.2 Add nav link and listing-detail actions.
- [x] 3.3 Add zh-TW and en copy.

## 4. Verification

- [x] 4.1 Production build passes.
- [x] 4.2 Browser check: setup → hunt → watch → price check → alert → confirmed contact; no horizontal scroll at 390 px.
