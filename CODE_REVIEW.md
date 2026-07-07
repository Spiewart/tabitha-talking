# Code Review — July 7, 2026

Full review with fixes applied. **All 248 tests pass** (was 247 + 1 failing), plus an end-to-end smoke test of every page type on a fresh database with the upgraded dependencies. `ruff check`, `ruff format`, `djlint`, `manage.py check`, and `makemigrations --check` are all clean.

## 1. Dependency updates (applied)

| Package | Was | Now | Why |
|---|---|---|---|
| django | 5.2.10 | **5.2.15** | 5 security patches behind (Feb–Jun 2026 releases) |
| wagtail | 6.4.2 | **7.4.2 (LTS)** | 6.4 out of support since late 2025; 7.4 LTS is supported to Nov 2027 |
| pillow | 11.3.0 | 12.3.0 | Image decoder CVEs are common; stay current |
| gunicorn | 24.1.1 | 26.0.0 | |
| sentry-sdk | 2.50.0 | 2.64.0 | |
| django-crispy-forms | 2.5 | 2.6 | |
| crispy-bootstrap5 | 2025.6 | 2026.3 | |
| django-environ | 0.12.0 | 0.14.0 | |
| django-recaptcha | 4.0.0 | 4.1.0 | |
| hiredis | 3.3.0 | 3.4.0 | |
| psycopg | 3.3.3 | 3.3.4 | |
| django-model-utils | 5.0.0 | **removed** | Not imported anywhere |

The Wagtail 6.4 → 7.4 jump needed no code changes here (verified by tests + fresh-DB migration run). Wagtail 7.4 now ships its own `modelsearch` app — migrations apply cleanly.

**Left for you to decide** (production-only, not exercisable by the test suite — upgrade one at a time and watch Sentry):

- django-anymail 14.0 → 15.0 (contact-form email via Mailgun)
- django-redis 6.0 → 7.0 and redis 7.1 → 8.0 (production cache client)

## 2. Bugs fixed

**Wagtail URL routing**

- `tests/test_contact.py::test_footer_on_about_page` called `reverse("about")`, but /about/ is a Wagtail page served by the catch-all — there is no named Django route. This was the one failing test. It now creates an `AboutPage` and requests its Wagtail URL.
- Added a comment block in `config/urls.py` documenting the resolution order (Django views shadow same-slug Wagtail pages; `path("blog/", ...)` matches only /blog/ exactly; the Wagtail include must stay last). Added regression assertions that /about/ and /portfolio/ resolve to `wagtail.views.serve`.
- Page-tree rules now enforce the URL structure in the CMS: `BlogPage` can only be created under `BlogIndexPage` (so posts always live at /blog/<slug>/ and always appear in the index), `DemoReelPage` under `PortfolioIndexPage`, and the index/About pages are limited to one each (`max_count = 1` — matches the views and navbar, which assume one of each).

**Templates**

- `search_results.html` referenced `result.blogpage.date` / `result.blogpage.intro`, which don't exist on `BlogPage` results — Django templates fail silently, so search results never showed dates or intros. Fixed.
- Five fields rendered rich text with `|safe` instead of `|richtext` (home, portfolio index ×2, demo reel ×2). Internal page links and embeds in those fields would have rendered as raw `<a linktype="page">` tags.

**Views / config**

- `contact_view` only caught `OSError`. Production sends mail through Mailgun's HTTP API, whose `AnymailError` is not an `OSError` — a Mailgun outage would have been a 500 instead of the friendly error message. Now catches both.
- `WAGTAILADMIN_BASE_URL` was hardcoded to `http://localhost:8000`; production now sets it (env-overridable) so CMS notification emails and preview links point to the real domain.
- RSS feed exposed the post owner's email address publicly (`<author>`); removed.
- Sitemap was missing the homepage entry; added with priority 1.0.
- Deleted `tabitha_talking/contrib/recaptcha.py` + `recaptcha_widgets.py`: dead code, and the former referenced settings that don't exist (`RECAPTCHA_V3_TESTING` etc.), so it would have crashed if ever called.
- `.dockerignore`: excluded `.envs/` from the image (local env files were being copied in) and fixed a stale `squeaky_knees.code-workspace` entry left over from another project.

## 3. Performance (matters on a small Droplet)

- **Blog index N+1 removed**: `BlogIndexPage.get_context` used `get_children().type().specific()` plus a per-post query for each header image. Now a single `BlogPage.objects.child_of(self).select_related("header_image")` query. Same for the portfolio index and headshots.
- **Image renditions**: header images rendered the original upload (`{{ ...file.url }}` — potentially multi-MB files). Now `{% image ... fill-800x450 %}` / `width-1000` renditions.
- **Response caching**: home 5 min, sitemap and RSS 1 h (README already claimed the sitemap was cached; now it is). robots.txt was already 24 h. Backed by Redis in production with `IGNORE_EXCEPTIONS`, so a Redis hiccup degrades gracefully.
- **Gunicorn**: 1 worker but now 4 threads (a slow Mailgun call no longer blocks every visitor), worker recycling via `--max-requests 1000` to cap slow memory growth, heartbeat in `/dev/shm`.
- **Dockerfile**: multi-stage build — compilers (`build-base`, `postgresql-dev`) stay in the builder; runtime image carries only `libpq` + `gettext`. Smaller image, faster deploys, less disk on the Droplet. Dependency layer is cached separately from code. *Note: validate with one CI build before relying on it.*

## 4. Suggestions (not implemented)

- **Wagtail-page 404s bypass caching**: every bot probing random URLs hits the DB through the catch-all. If Droplet load becomes an issue, consider `wagtail.contrib.frontend_cache` or Cloudflare in front.
- **Search backend**: the default DB backend is fine at this scale; on Postgres it already uses full-text search. No action needed.
- **`config/validation.py` (`sanitize_html`)** is only used by its own tests — the contact form doesn't render user HTML anywhere. Keep or delete; if you delete it, update the README's Safety section.
- **Navbar hardcodes `/portfolio/` and `/about/`** — fine as long as those slugs never change in the CMS (the new `max_count`/parent rules make this safer). `{% slugurl %}` is the Wagtail-native alternative.
- **HSTS is still 60 s** (`SECURE_HSTS_SECONDS`) — the TODO in production.py says to raise it once HTTPS is proven; it clearly is, so consider 518400 (6 days) or more.
- **X-XSS-Protection header** is obsolete (ignored by modern browsers); harmless, but you could drop it from `SecurityHeadersMiddleware` (its tests pin it, so update both together).
- **Rate-limiter trusts `X-Forwarded-For` blindly** — fine behind Traefik, but worth remembering if the proxy setup ever changes.
- The duplicate site-configuration data migrations (`blog/0002` and `portfolio/0002` do the same thing) are idempotent and already applied; not worth the churn to consolidate.

## 5. Verification performed

1. Full pytest suite on the old pins → 247 pass / 1 pre-existing failure (the `reverse("about")` bug).
2. Bug fixes applied → 248/248 pass.
3. Dependencies upgraded, `uv.lock` regenerated → 248/248 pass again, **including a fresh-database run** exercising the full Wagtail 6.4 → 7.4 migration chain.
4. End-to-end smoke test: created one of every page type and requested all 13 public routes (200s), validated sitemap/feed XML parse, confirmed homepage in sitemap, search results show date + intro, no email in the feed.
5. `manage.py check`, `makemigrations --check` (no model changes need migrations), `ruff check` + `format`, `djlint` on all 16 HTML templates — clean.
