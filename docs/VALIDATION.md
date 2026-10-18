# Validation

The maintained app includes 32 Django tests against a fresh test database. They cover:

- Verification delivery through the test outbox, hash-only challenge state, session rotation, expiry, malformed codes, failure limits, resend cooldown and sign-out.
- Ten-card level distribution, unique cards, idempotent demo seeding, game resumption and the third-attempt boundary.
- Atomic rollback when the question bank is incomplete, wrong/correct scoring, sequential duplicate submissions, score caps, best-score retention and answer-history retention.
- Expiry after more than a day, direct post-deadline submissions, completion when all answers are wrong, foreign object access, invalid forms, HTML escaping, CSRF and independent admin authentication.

All 32 tests passed locally on Python 3.12 with Django 5.2.18. System checks, migration drift checks, fresh migrations and the synthetic seed also passed. The source audit verifies 58 sanitized historical-file hashes and rejects forbidden publication artifacts. Additional private checks compare the publication against original embedded secret values without printing or recording them.

GitHub Actions repeats tests, source audit, migration checks, fresh database setup, static collection and a deployment-settings check on Python 3.11 and 3.12. The root badge links to the actual workflow status. Deployment configuration checks are performed with a public CI-only key and debug disabled.

The suite does not exercise real SMTP delivery, browser compatibility across devices, a production database or simultaneous distributed requests. The browser timer is not trusted for scoring. Demo questions are intentionally simple and do not validate an educational assessment instrument.

After resolving the sandbox's blocked localhost connection, the app was verified in the in-app browser using a fictional participant and the console email backend: request code, verify session, start a ten-card game, open a question, submit a correct answer, observe the score change from 0 to 2, finish and view the saved result. The sign-in and dashboard layouts were visually inspected; real browser screenshots are retained under `docs/images/`. This is a desktop smoke check, not cross-device browser coverage. No real email was sent.
