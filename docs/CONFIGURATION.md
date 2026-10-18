# Configuration and running the demonstration

Run all commands from the directory containing `manage.py`. SQLite is created locally by `migrate` and is ignored by Git. `seed_demo` adds 20 invented questions without reading the original databases or creating users. The original database schema is not migrated into this maintained app.

## Environment

Settings read the process environment. `.env.example` is documentation, not an automatically loaded configuration file. Do not commit your real configuration.

| Variable | Default / behavior |
| --- | --- |
| `DJANGO_DEBUG` | `1` for local development; set `0` for deployment checks |
| `DJANGO_SECRET_KEY` | Random ephemeral value in development; required with debug off |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1`; comma-separated explicit hosts |
| `DJANGO_EMAIL_BACKEND` | Django console backend, which sends no email |
| `DJANGO_EMAIL_HOST`, `DJANGO_EMAIL_PORT` | Your own SMTP provider and port, if configured |
| `DJANGO_EMAIL_HOST_USER`, `DJANGO_EMAIL_HOST_PASSWORD` | Your private SMTP credentials, if needed |
| `DJANGO_DEFAULT_FROM_EMAIL` | `quiz@example.invalid`; configure your own sender for real delivery |

For a persistent development secret in PowerShell:

```powershell
$env:DJANGO_SECRET_KEY = python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
python manage.py runserver
```

For Linux/macOS:

```bash
export DJANGO_SECRET_KEY="$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')"
python manage.py runserver
```

These commands keep the generated secret in the current shell environment. Restarting that shell without preserving the same secret invalidates previous sessions. The source archive's credentials are deliberately removed and must not be reused.

## Local sign-in

Use a fictional participant and `demo@example.invalid`. The server terminal prints a verification email containing a six-digit code; no external message is sent with the default backend. Codes expire after five minutes. Repeated requests for the same email wait one minute, and five incorrect attempts block further verification for ten minutes in the local process. Each client IP may request at most ten codes per hour in that process.

Administrator login at `/admin/` uses a separately created Django superuser. Participant verification does not grant admin permissions. Sign-out is a CSRF-protected POST action. Use invented identities when making screenshots or sharing a local demo.

## Beyond local development

This repository publishes source, not a hosted website. Django's development server is not a production server. HTTPS, a reviewed reverse proxy/server, static file serving, real mail delivery, shared throttling, session cleanup and operational monitoring are deployment responsibilities. With debug disabled, the settings enable secure cookies, HTTPS redirection and HSTS and refuse to start without a secret. They do not blindly trust forwarded proxy headers.

Run `python manage.py check --deploy --fail-level WARNING` with your intended environment. Passing it checks Django configuration, not all application-security or concurrency properties. The CI key is an explicitly public test value and must never be used for deployment.

References: [Django deployment checklist](https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/) and [Django 5.2 security release, October 2026](https://www.djangoproject.com/weblog/2026/oct/06/security-releases/).
