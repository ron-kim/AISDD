## ADDED Requirements

### Requirement: Collect deal preferences before hunting
The UI SHALL ask for a transport mode, maximum distance and price-drop alert threshold before showing deal tools, and SHALL let the user edit them later.

#### Scenario: First visit
- **WHEN** the user opens the Deal Hunter page without completed setup
- **THEN** the UI SHALL show the setup form and hide hunting, price check and watchlist tools

### Requirement: Rank listings by real cost
The system SHALL rank matching listings by a deal score derived from real cost (price plus round-trip transport), savings against a new-retail reference price, recent price trend and seller trust, and SHALL return at most three picks within budget.

#### Scenario: Hunt within budget
- **WHEN** the user searches with a keyword and budget
- **THEN** the UI SHALL show up to three picks with price, transport cost, real cost, reference price, savings, trend, trust and score
- **AND** SHALL list every listing it checked

#### Scenario: Flag risks
- **WHEN** a pick is reserved, beyond the max distance, or from an unverified seller
- **THEN** the UI SHALL label the warning on that pick

### Requirement: Check before buying
The system SHALL compare a chosen listing with all listings in the same category and report whether any available listing has a lower real cost.

#### Scenario: Cheaper option exists
- **WHEN** a similar, unreserved listing has a lower real cost
- **THEN** the UI SHALL list it with how much cheaper it is

### Requirement: Quiet price watchlist
The system SHALL let the user watch a listing or keyword with an optional target price, and a price check SHALL alert only when a drop reaches the threshold or the target price.

#### Scenario: Small move
- **WHEN** a watched price drops by less than the threshold and stays above target
- **THEN** no alert SHALL be raised and the UI SHALL say nothing worth flagging changed

#### Scenario: Meaningful drop
- **WHEN** a watched price drops by at least the threshold
- **THEN** an alert SHALL show the old price, new price and drop percentage, and the same drop SHALL NOT be reported again

### Requirement: Never act without consent
The system SHALL NOT contact sellers or reserve items on its own.

#### Scenario: Ask seller
- **WHEN** the user chooses "Ask seller" on a pick
- **THEN** the UI SHALL ask for confirmation before opening the conversation
