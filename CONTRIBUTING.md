# Contributing

Run Django checks, migration drift checks, `python manage.py test game` and `python tools/audit_sources.py` before proposing changes. Add regression tests for authorization and game-rule changes. Use only fictional participants and newly authored demo questions in fixtures and screenshots.

Do not commit databases, session data, email outboxes, credentials, local environments or original course documents. Keep the sanitized archive unchanged and update its manifest only when documenting a deliberate source transformation. Changes to game rules, authentication or production deployment must describe their actual tested scope.
