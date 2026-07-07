## Context

The codebase already includes a locale composable with:

- persistent storage for the selected language
- a `t()` helper for message keys
- a `text()` helper for localized content data
- document language updates for accessibility and browser behavior

The remaining work is mostly completeness and consistency.

## Goals / Non-Goals

**Goals:**
- Make the UI fully switch between Traditional Chinese and English.
- Ensure every visible label and state string is locale-aware.
- Keep the implementation lightweight and consistent with the existing Vue composition pattern.

**Non-Goals:**
- Adding additional languages beyond `zh-TW` and `en`.
- Introducing server-driven translation management.
- Building machine translation or user-editable localization tooling.

## Decisions

- Use the existing locale composable as the single source of truth.
  - Rationale: the app already depends on `t()`, `text()`, and persisted locale state. Extending that path is lower risk than introducing a second localization layer.

- Keep structural UI copy in message catalogs and content data in localized fixtures.
  - Rationale: page headings, buttons, and status text belong in `messages`, while listing titles, descriptions, and meetup suggestions should continue to use localized data objects.

- Localize all remaining hard-coded chrome in the feature screens.
  - Rationale: a switcher only feels complete if navigation, trust, meetup, and chat surfaces all respond to it.

- Repair corrupted Traditional Chinese strings as part of the same change.
  - Rationale: broken Chinese text would make the feature appear unfinished even if toggling works technically.

## Risks / Trade-offs

- [Risk] The localized string surface is larger than it first appears.
  - Mitigation: update by screen and verify each route rather than trying to replace everything at once.

- [Risk] Localized mock data may still contain malformed text if edited inconsistently.
  - Mitigation: keep all fixture text in one source file and verify the rendered output in both locales.

- [Risk] Some strings may need new message keys, which can spread changes across components.
  - Mitigation: add keys deliberately and keep naming aligned with the current `app`, `nav`, `common`, `home`, `chat`, `map`, `meetup`, and `trust` groups.

## Migration Plan

1. Inventory all visible strings and identify the remaining hard-coded text.
2. Add or repair locale keys for shell, trust, chat, meetup, and listing screens.
3. Fix localized fixtures and any corrupted Chinese strings.
4. Verify the toggle updates all screens, persists across reloads, and keeps document language in sync.
5. Build and review the app in both languages to catch missing keys or malformed output.

## Open Questions

- Should the app default to the browser language when no preference is stored, or always default to Traditional Chinese?
- Do we want to keep `zh-TW` as the internal locale key, or introduce a more generic `zh` alias later?
- Should future copy changes be required to add both languages at the same time?
