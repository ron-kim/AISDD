## ADDED Requirements

### Requirement: Suggest practical meetup points
The UI SHALL present suggested public meetup points for face-to-face trades based on proximity and convenience.

#### Scenario: Review meetup suggestions
- **WHEN** the user opens meetup suggestions for a listing
- **THEN** the UI SHALL show a ranked set of public locations suitable for handoff

### Requirement: Explain meetup recommendation factors
The UI SHALL explain why a meetup point is suggested so users can judge its suitability.

#### Scenario: Inspect a suggestion
- **WHEN** the user expands a meetup point suggestion
- **THEN** the UI SHALL show the main factors such as distance, public visibility, or transit convenience

### Requirement: Support selecting a meetup point
The UI SHALL allow the user to pick a suggested meetup point for later sharing in the conversation.

#### Scenario: Choose a meeting location
- **WHEN** the user selects a meetup point
- **THEN** the UI SHALL keep that point available for sharing in chat or copying for offline coordination

