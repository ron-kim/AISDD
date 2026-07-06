## ADDED Requirements

### Requirement: Open a buyer-seller conversation
The UI SHALL let users start or continue a conversation from a listing or seller surface.

#### Scenario: Contact seller from listing
- **WHEN** the user selects the chat action on a listing
- **THEN** the UI SHALL open the relevant conversation or create a new one for that listing

### Requirement: Send and receive messages in real time
The UI SHALL support live message exchange so buyer and seller can coordinate without manual refresh.

#### Scenario: New incoming message
- **WHEN** a new message arrives in an open conversation
- **THEN** the UI SHALL render the message immediately in the active thread

### Requirement: Show conversation state
The UI SHALL indicate connection and delivery state so users can tell whether a message is sending, sent, or delayed.

#### Scenario: Temporary connection loss
- **WHEN** the connection is interrupted while a message is being sent
- **THEN** the UI SHALL show a non-blocking status and allow the user to retry

