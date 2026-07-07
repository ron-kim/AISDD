## 1. Data Model

- [x] 1.1 Add structured `county` and `district` fields to the listing type.
- [x] 1.2 Update mock listing fixtures to populate county and district values.
- [x] 1.3 Keep the existing display `location` text intact.

## 2. Filter State

- [x] 2.1 Add county and district filter state to the shared marketplace store.
- [x] 2.2 Derive available district options from the selected county.
- [x] 2.3 Include county and district in the filtered listing computation.

## 3. UI

- [x] 3.1 Add county and district controls to the browse interface.
- [x] 3.2 Keep the controls compact enough for mobile layouts.
- [x] 3.3 Ensure filter changes update the home listing grid and linked views consistently.

## 4. Verification

- [x] 4.1 Verify keyword, category, county, and district filters work together.
- [x] 4.2 Verify invalid district selections are handled cleanly when county changes.
- [x] 4.3 Run a production build to catch any type or template regressions.
