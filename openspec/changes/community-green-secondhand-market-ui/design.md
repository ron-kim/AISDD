## Context

This change introduces a community-first secondhand marketplace UI built with Vue. The product emphasizes nearby, face-to-face trading, so the frontend must make location-aware discovery, seller trust, chat, and meetup coordination feel like one connected flow rather than separate features.

The repo does not currently contain an application shell, so the design assumes a greenfield Vue frontend that can later connect to real APIs or use mock adapters during early implementation.

## Goals / Non-Goals

**Goals:**
- Deliver a cohesive Vue-based marketplace interface with a community green, rounded visual language.
- Keep nearby discovery central through map browsing and location-aware listing surfaces.
- Expose trust, messaging, and meetup guidance as first-class actions in the browse-to-contact flow.
- Keep the UI testable by separating presentation, state, and service adapters.

**Non-Goals:**
- Building a production backend for listing storage, chat transport, or trust scoring logic.
- Choosing a specific map vendor, WebSocket provider, or geocoding service in this design.
- Implementing moderation, payments, shipping, or dispute resolution flows.

## Decisions

- Use Vue 3 with the Composition API and route-level feature screens.
  - Rationale: Vue aligns with the request, gives a compact component model, and makes it straightforward to compose map, chat, and detail views.
  - Alternatives considered: React for ecosystem breadth, Svelte for smaller runtime. Vue is the best fit because the request explicitly calls for Vue and the UI is component-heavy.

- Use a feature-oriented structure with shared design tokens.
  - Rationale: The change spans discovery, map browsing, trust, chat, and meetup surfaces. A feature-first layout keeps these concerns isolated while preserving a shared visual system.
  - Alternatives considered: A single monolithic page or purely atomic component library. Both would make the cross-feature flow harder to maintain.

- Use CSS variables for theme tokens and rounded component primitives.
  - Rationale: The visual direction is intentional and brand-like. Tokens make the community green palette easy to enforce consistently across cards, maps, chat, and badges.
  - Alternatives considered: Utility-only styling or per-component hardcoded colors. Those approaches make consistency harder to guarantee.

- Keep map state and listing state synchronized through a shared store and URL state.
  - Rationale: Users should be able to move between list and map without losing context. Shared state also simplifies testing and deep linking.
  - Alternatives considered: Isolated component state or prop drilling. Those approaches make synchronization brittle as the UI grows.

- Treat chat, trust, and meetup suggestions as adapter-backed services.
  - Rationale: The initial UI can run with mock data, but the interfaces should match real services later. This keeps the frontend shippable before backend integration is complete.
  - Alternatives considered: Hardcoding everything in components. That would block replacement with live data and make tests less meaningful.

- Make meetup suggestions explainable rather than opaque.
  - Rationale: In a trust-sensitive local marketplace, users need to understand why a meetup point is recommended. Explainability increases confidence and reduces perceived risk.
  - Alternatives considered: A single best match with no rationale. That would be less transparent and harder to trust.

## Risks / Trade-offs

- [Risk] Map, trust, and chat integrations may not be available at the same time.
  - Mitigation: Define service interfaces and ship mock adapters so each screen can be developed and tested independently.

- [Risk] A local-first UI can become cluttered if too many actions compete for attention.
  - Mitigation: Keep the browse, message, trust, and meetup actions in a fixed hierarchy and reuse the same card patterns across screens.

- [Risk] Location permission denial may reduce discovery quality.
  - Mitigation: Provide a manual search and browse fallback with clear prompts to re-enable location.

- [Risk] Real-time chat and map updates can introduce state synchronization bugs.
  - Mitigation: Centralize state changes, keep side effects in service adapters, and favor explicit loading/error states.

## Migration Plan

1. Bootstrap the Vue frontend shell, routing, and shared theme tokens.
2. Add discovery and listing surfaces with mock data so the browse flow is complete early.
3. Introduce map exploration with synchronized list/map state.
4. Add trust score, chat, and meetup suggestion surfaces behind adapter interfaces.
5. Replace mock adapters with live services as backend endpoints become available.
6. If integration issues appear, roll back by swapping the adapters back to mocks while keeping the UI shell intact.

## Open Questions

- Which map provider should be used for production?
- Should chat use WebSockets, SSE, or a polling fallback?
- What data source will produce the seller trust score and its explanation factors?
- Should meetup points be generated by a rule engine, curated list, or geospatial service?
- Do we need authentication in this change, or should the UI assume an already-authenticated session?
