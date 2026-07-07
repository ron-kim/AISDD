## 1. Locale Coverage

- [x] 1.1 Inventory all visible strings across shell, home, listing, chat, map, meetup, and trust screens.
- [x] 1.2 Add or repair missing locale keys in the message catalog.
- [x] 1.3 Confirm the language toggle persists selection and updates the document language attribute.

## 2. Screen Localization

- [x] 2.1 Localize the shell navigation, language toggle label, and startup/error copy.
- [x] 2.2 Localize trust score, meetup suggestions, and chat status panels.
- [x] 2.3 Localize listing detail copy and any remaining route-level headings or actions.

## 3. Content and Fixtures

- [x] 3.1 Repair corrupted Traditional Chinese strings in localized mock data.
- [x] 3.2 Confirm `text()` renders the correct language for listings, sellers, trust summaries, conversations, and meetup suggestions.

## 4. Verification

- [x] 4.1 Run a production build and fix any type or template errors caused by localization changes.
- [x] 4.2 Verify both `zh-TW` and `en` render correctly on the main routes.
- [x] 4.3 Check that language switching updates the current view without requiring a manual refresh.
