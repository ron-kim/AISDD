## ADDED Requirements

### Requirement: Show nearby items on a map
The UI SHALL display nearby listings on an interactive map centered on the user's area when location access is available.

#### Scenario: Location access granted
- **WHEN** the user allows location access
- **THEN** the UI SHALL center the map on the user's area and show nearby listing markers

### Requirement: Keep map and list in sync
The UI SHALL keep map selections and listing results synchronized so users can move between geographic browsing and list browsing without losing context.

#### Scenario: Selecting a listing pin
- **WHEN** the user selects a marker on the map
- **THEN** the UI SHALL highlight the corresponding listing in the results list and show its key details

### Requirement: Handle missing location access
The UI SHALL provide a usable fallback when location access is denied or unavailable.

#### Scenario: Location access denied
- **WHEN** the browser blocks location access
- **THEN** the UI SHALL show a default discovery view and a clear way to search or browse manually

