# Operating Pygmy safely

Use Python 3.13 or newer and install the locked `requirements.txt`. Dependency
updates should be resolved from `requirements.in`, audited with `pip-audit`,
and tested before deployment. The container runs as UID/GID 10001.

Generate two independent random secrets (`openssl rand -hex 32`), then set
`PYGMY_SECRET_KEY` and `DJANGO_SECRET_KEY` privately in your environment or an
untracked `.env`. The checked-in API configuration deliberately cannot boot
without a secret. Never commit production configuration, environment files,
credentials, database copies, backups or logs. Build from a clean source
checkout, not from a running installation.

The Compose example is a **fresh SQLite installation**. Keep and back up an
existing database before changing deployment configuration. PostgreSQL/MySQL
remain supported through the existing database configuration; supply a supported
database and its driver separately. Never attach an old PostgreSQL volume to a
new major server version without a proper upgrade or restore.

Put the UI behind HTTPS and a rate-limiting reverse proxy. Set
`PYGMY_ALLOWED_HOSTS` to the actual hostnames, `PYGMY_PUBLIC_URL` to the HTTPS
origin, `PYGMY_CSRF_ORIGINS` to trusted HTTPS origins, and
`PYGMY_TRUST_PROXY=1` only when the proxy overwrites `X-Forwarded-Proto`.
Secure cookies are on by default; for local HTTP development only, set
`PYGMY_COOKIE_SECURE=0`. API CORS is not a replacement for authorization.

## Public demo

Set `PYGMY_DEMO_MODE=1` on **both** API and UI services. This removes account
forms, displays a demo notice, blocks signup/login/dashboard and all account
API/refresh endpoints, and ignores stale UI authentication cookies. Normal
self-hosted installations default to accounts enabled. Keep the API private.

Keep capabilities dropped, read-only root filesystems, no-new-privileges,
bounded CPU/memory/processes/logs, and an internal Docker network. Do not mount
the Docker socket or unrelated application directories. Also block new
container-to-host connections in the host firewall: an internal network alone
is not a complete host boundary. Put writable demo data on storage with a total
quota and retain bounded backups outside the web root. Containers share the
host kernel; a separate VM provides stronger isolation for an untrusted demo.

## Verification

Run `python -m unittest test_security` and
`PYGMY_SECRET_KEY=<synthetic-test-secret> python -m pytest pygmy/tests`.
Run `pip-audit -r requirements.txt`. Tests use synthetic credentials and an
isolated SQLite database. Test both demo mode and normal account mode before
release. Audit success covers known Python package advisories, not every
possible application or operating-system vulnerability.
