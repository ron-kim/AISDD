## ADDED Requirements

### Requirement: Show seller trust score on listings
The UI SHALL display a seller trust score on listing and seller surfaces so buyers can assess trust before contacting the seller.

#### Scenario: Open a listing
- **WHEN** the user opens a listing detail view
- **THEN** the UI SHALL show the seller trust score and the most relevant trust indicators

### Requirement: Explain trust score factors
The UI SHALL make the trust score explainable by showing the factors that contributed to it.

#### Scenario: Inspect score details
- **WHEN** the user expands the trust score information
- **THEN** the UI SHALL present the main factors behind the score such as response history, profile completeness, or transaction signals

### Requirement: Handle unavailable trust data
The UI SHALL present a clear fallback state when seller trust data is unavailable.

#### Scenario: Missing trust data
- **WHEN** trust data cannot be loaded
- **THEN** the UI SHALL show a neutral fallback state instead of a misleading score

