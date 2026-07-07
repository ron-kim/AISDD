## Why

The app already has a locale state and a language toggle in the shell, but the experience is incomplete:

- Several visible screens still contain hard-coded English strings.
- Some Traditional Chinese resources are corrupted or unreadable.
- The current toggle does not guarantee that every user-facing label, status, and empty state updates consistently.

The goal is to make the interface reliably switch between Traditional Chinese and English without visual gaps or broken text.

## What Changes

- Keep the existing `zh-TW` and `en` locale model, and treat language switching as a first-class UI capability.
- Move all user-facing chrome, page headings, button labels, status text, and empty states into locale-aware message keys.
- Ensure localized mock data and content cards render the correct language through the existing `text()` helper.
- Repair corrupted Traditional Chinese strings so the Chinese experience is readable and complete.
- Preserve the selected language in browser storage and apply it to the document language attribute.

## Capabilities

### New Capability
- `zh-en-interface-language-switcher`: Switch the entire marketplace UI between Traditional Chinese and English.

### Modified Capabilities
- `community-secondhand-market-ui`: The shell, home, listing, chat, map, meetup, and trust surfaces all need to render localized text correctly.

## Impact

- Affects the app shell navigation, feature screens, and trust/chat/meetup components.
- Requires updates to both message catalogs and localized mock content.
- Should preserve the current theme toggle and existing route behavior.
