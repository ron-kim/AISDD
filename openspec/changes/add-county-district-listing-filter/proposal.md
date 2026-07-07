## Why

The marketplace search experience currently supports keyword and category filtering, but geographic browsing is still implicit. Listings expose a human-readable `location` string, yet users cannot narrow results by Taiwan county or district in a structured way.

Adding county and district filters will make local discovery faster and more predictable, especially as the listing set grows beyond a small Taipei sample.

## What Changes

- Add structured Taiwan location fields to listings so each item can be filtered by county and district.
- Add county and district filters to the exploration UI.
- Keep keyword search and category filtering working alongside the new geographic filters.
- Use district options that depend on the selected county, so the filter list stays manageable.
- Preserve the existing display `location` text for cards and detail views.

## Capabilities

### New Capability
- `county-district-listing-filter`: Filter marketplace listings by Taiwan county and district.

### Modified Capabilities
- `community-secondhand-market-ui`: Browse and listing flows need location-aware filtering controls.

## Impact

- Requires updates to listing data models and mock fixtures.
- Affects the home discovery page and any other views that rely on the shared filtered listing set.
- May require minor copy updates for the new filter labels and empty states.
