## Context

The app already has shared store-driven filtering for search and category. The listing data also includes a readable `location` string, but it is not enough for reliable geographic filtering.

This change should introduce structured location data without breaking existing display text or search behavior.

## Goals / Non-Goals

**Goals:**
- Let users filter listings by Taiwan county and district.
- Keep the existing search and category filters intact.
- Make the county and district controls easy to scan and update.
- Keep the rendered listing location text unchanged for display purposes.

**Non-Goals:**
- Building map-based geospatial search or radius filtering.
- Adding neighborhood-level polygons or GPS-based nearest matching.
- Adding backend geocoding or address normalization.
- Expanding beyond Taiwan county and district metadata.

## Decisions

- Add `county` and `district` as structured listing fields.
  - Rationale: structured data is easier to filter and safer than parsing a formatted string.

- Keep `location` as a display field.
  - Rationale: cards and detail views still need a human-readable location string, and the display text may not always map cleanly to filters.

- Make district options depend on the selected county.
  - Rationale: this reduces choice overload and prevents invalid county-district combinations.

- Keep all filtering in the shared store.
  - Rationale: the home page, map view, and any future browse surfaces should observe the same filtered set.

## Risks / Trade-offs

- [Risk] Existing mock data only covers a few Taipei examples.
  - Mitigation: introduce the structured fields in the same mock source and keep the initial set small but valid.

- [Risk] UI space is already tight on mobile.
  - Mitigation: use compact select controls or segmented filter blocks instead of a heavy filter panel.

- [Risk] Adding more filters can make the browse flow feel slower.
  - Mitigation: keep county and district selection obvious, and leave keyword search as the fastest path.

## Migration Plan

1. Extend the listing model with county and district fields.
2. Update fixtures to include structured location metadata.
3. Add county and district filter state to the shared store.
4. Wire the filters into the browse UI and filtered listing computation.
5. Verify keyword, category, and location filters work together without regressions.

## Open Questions

- Should the initial dataset cover only Taipei, or should it include a broader Taiwan sample from the start?
- Should the county and district controls use dropdowns, chips, or a two-step selector?
- Should selecting a county reset the district filter automatically when the district becomes invalid?
