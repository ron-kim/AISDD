## Why

Buyers on the marketplace can search and filter, but they cannot tell whether a listing is actually a good deal. The asking price hides the cost of getting to the meetup, there is no reference to what the item costs new, and nobody watches prices on their behalf.

Shopping bots such as the Grok bot "Deal Hunting" and "Deal Watcher" templates solve this for online retail: they compare real (landed) cost across stores, name every store they checked, keep an optional watchlist that only speaks up when a price moves enough to matter, and never buy anything without the user's OK. This change brings the same workflow to local secondhand trading.

## What Changes

- Add a `/deals` "Deal Hunter" page with a one-time setup (transport mode, max distance, price-drop alert threshold).
- Hunt: keyword + budget + category search that returns up to 3 picks ranked by a deal score, and lists every listing it checked.
- Real cost: price + round-trip transport cost for the chosen mode, compared against a new-retail reference price and recent price history.
- Check before you buy: pick a listing (or arrive from a listing page via `?check=<id>`) to see whether a similar listing has a lower real cost.
- Watchlist: watch a listing or a keyword with an optional target price; "Check prices now" pulls simulated seller price updates and only raises alerts for drops at or above the threshold or at the target.
- Contacting a seller always goes through a confirmation dialog; the bot never contacts sellers or reserves items on its own.
- Listing detail gains "Check this deal" and "Watch this item" actions; the nav gains a Deal Hunter link.

## Capabilities

### New Capability
- `deal-hunter`: Rank listings by real cost, compare before buying, and watch prices.

### Modified Capabilities
- `community-secondhand-market-ui`: Navigation and listing detail gain deal-hunter entry points.

## Impact

- New: `services/dealHunter.ts` (pure scoring engine), `stores/dealStore.ts`, `views/DealsView.vue`, `components/DealTable.vue`.
- Mock data gains four listings, reference prices, price history and simulated price-update rounds.
- Preferences, watchlist and alerts persist in `localStorage` (best effort).
