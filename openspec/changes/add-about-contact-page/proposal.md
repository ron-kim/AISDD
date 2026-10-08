## Why

The marketplace is published under the company domain `rondaymemories.com`, but the site never says who operates it or how to reach them. Visitors, partners, and program reviewers need a clear company identity and a contact address that matches the domain.

## What Changes

- Add an `/about` route that introduces Ronday Memories as the team behind Community Green Marketplace.
- Show the mission and a company-domain contact email (`ironya@rondaymemories.com`) with a `mailto:` action.
- Add an "About" link to the shell navigation.
- Add `about` and `nav.about` message keys in both `zh-TW` and `en`.
- Include the company name in the document title.

## Capabilities

### New Capability
- `about-contact-page`: Present company identity and contact information in both languages.

### Modified Capabilities
- `community-secondhand-market-ui`: The shell navigation gains an About entry.

## Impact

- Adds one view and one route; touches the shell, router, locale catalog, and `index.html`.
- No changes to market data, store, or existing routes.
