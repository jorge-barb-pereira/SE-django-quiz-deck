# Source review and maintained changes

## Original assessment application

The source used Django 5.1.3 and custom session flags for a two-step student sign-in. It generated a numeric code, printed it to the terminal and left the send-mail call commented out. Settings contained embedded credentials and a local SQLite database path. Those credentials and databases are excluded from the public repository.

The original middleware redirected most unauthenticated routes, including administrative routes. Its question-access middleware inspected resolver data before URL resolution and referenced a route name that differed from the actual URL. Individual game/card views did not consistently restrict queries to the authenticated student, allowing access by changing object IDs.

Original numeric input conversions could raise errors, verification codes lacked expiration and attempt limits, game creation could consume an attempt before failing on an insufficient question bank, and the third active game could be blocked by the attempt check. Time arithmetic used the timedelta seconds component, which wraps after whole days. Direct answer submissions did not consistently enforce expiration or finished status. Answers and scores were updated in separate operations, and completion deleted card history.

## Maintained application

- Environment-based settings; an ephemeral development secret and a mandatory secret when debug is disabled. No SMTP identity is hardcoded.
- Session-bound code hashes, five-minute expiration, a five-failure limit, one-minute resend cooldown, per-email failure counts and a per-IP issuance cap. Sessions and CSRF tokens rotate after successful verification.
- A generic verified-email participant model replaces institution-specific IDs. Admin uses Django's normal authentication independently.
- Every game/card lookup is scoped to the verified player. Anonymous users are redirected; another player's records return 404. Unsupported methods are rejected before data access.
- Atomic game creation checks all four question pools before consuming an attempt. An existing active game is resumed before applying the three-attempt limit.
- Persisted timezone-aware deadlines are checked on the server, including direct answer submissions. Reaching 20, answering all ten cards, expiration or explicit completion ends the game. Scores are capped and best scores cannot decrease.
- Conditional answer updates prevent sequential replay from awarding points twice. Game transitions lock the parent row on databases supporting row locks, and scores use database expressions.
- Typed form input, escaped question text, CSRF-protected mutation forms and no-cache participant responses. Local CSS/JavaScript replace external styling, math-rendering and legacy script CDNs. Questions are rendered as plain escaped text, not Markdown or HTML.
- Answer history remains available after completion. The included question bank is synthetic; no original student database is migrated.

## Tutorial exercises

Polls demonstrates the Django tutorial's question/choice schema and early response/template exercises. Movies contains an unresolved TemplateView import and missing template. The DRF exercises reference the quickstart's tutorial module paths instead of their local module. They are preserved as historical learning examples, not claimed to be repaired or exposed as live API routes.

## Practical limits

SQLite is suitable for the local demo; it does not provide SELECT FOR UPDATE row locking. The tests exercise sequential replay, integrity constraints and request authorization, not concurrent distributed traffic. A production database and concurrent-request testing are needed before claiming exactly-once behavior under load. Active questions should not be edited during real assessments; the demo does not snapshot question revisions or provide tamper-evident audit records.

The local-memory throttle is process-local and resets on restart. It is not a distributed abuse-prevention system. Console email is a demonstration transport; the ability to read the server terminal is not verified ownership of a real mailbox. No institutional identity, fairness of assessment, proctoring, delivery reliability, accessibility certification or public-service readiness is asserted.
