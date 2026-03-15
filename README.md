# Tabitha Talking

Voice acting portfolio and blog site built with Django and Wagtail CMS.

[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

License: MIT

## Features

### Portfolio

- **Demo reels** -- audio demos organized by category (Commercial, Narration, Animation/Character, Audiobook, E-Learning, Promo). Each demo has an HTML5 audio player, description, duration, and optional transcript.
- **Headshot gallery** -- managed via Wagtail's image system with automatic renditions for thumbnails.
- **Video embeds** -- YouTube/Vimeo embeds via Wagtail's EmbedBlock for responsive playback without self-hosting video.
- **About page** -- profile photo, bio content via StreamField (rich text, images, video embeds), and credentials section.

### Blog

Blog posts are authored in the Wagtail CMS admin (`/cms/`) using a StreamField body with rich text and image blocks. Each post can have a header image, intro text, and tags via django-taggit.

### Discovery & SEO

- **Full-text search** -- Wagtail's search backend indexes post titles, intros, and body content at `/blog/actions/search/`.
- **Tag filtering** -- clicking a tag filters posts by tag slug.
- **Pagination** -- blog index paginates at 10 posts per page.
- **RSS feed** -- RSS 2.0 XML at `/feed.xml` with the latest 20 posts.
- **Sitemap & robots.txt** -- `/sitemap.xml` includes portfolio, about, and blog pages. Both are cached.

### Safety & Anti-Abuse

- **reCAPTCHA v3** on the contact form.
- **Rate limiting** -- cache-backed limiter on contact submissions (5 per hour).
- **Input sanitization** -- `sanitize_html()` strips scripts, event handlers, iframes, and style tags.
- **Security headers** -- `X-Content-Type-Options`, `X-XSS-Protection`, `X-Frame-Options`. Production uses HSTS, secure cookies, and Argon2 password hashing.
- **Sentry** integration for error tracking.

## Getting Started

### Prerequisites

- Python 3.13
- PostgreSQL (production) or SQLite (development)
- uv package manager

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Spiewart/tabitha_talking.git
   cd tabitha_talking
   ```

2. Install dependencies:
   ```bash
   uv sync
   ```

3. Set up environment variables:
   - Local defaults live in `.envs/.local/.django` and `.envs/.local/.postgres`
   - Set `RECAPTCHA_V3_SITE_KEY` and `RECAPTCHA_V3_SECRET_KEY` for the contact form

4. Run migrations:
   ```bash
   python manage.py migrate
   ```

5. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

6. Run the development server:
   ```bash
   python manage.py runserver
   ```

### Setting Up Content

1. Access Wagtail admin at `http://localhost:8000/cms/`
2. Create a **Portfolio Index Page** as a child of the root page
3. Add **Demo Reel Pages** as children of the portfolio index
4. Create an **About Page** as a child of the root page
5. Create a **Blog Index Page** and add **Blog Pages** under it
6. Configure the site under Settings > Sites to set the root page

### Useful Endpoints

- Home: `/`
- Portfolio: `/portfolio/` (Wagtail page)
- About: `/about/` (Wagtail page)
- Blog: `/blog/`
- Contact: `/contact/`
- RSS feed: `/feed.xml`
- Sitemap: `/sitemap.xml`
- Wagtail admin: `/cms/`

## Project Structure

```text
tabitha_talking/
├── tabitha_talking/
│   ├── blog/           # Blog app (Wagtail page models)
│   ├── portfolio/      # Portfolio app (demos, about, headshots)
│   ├── users/          # Custom user model
│   ├── templates/      # Django/Wagtail templates
│   └── static/         # Static files (CSS, JS, images)
├── config/             # Django settings and configuration
└── tests/              # Test files
```

## Technology Stack

- **Framework**: Django 5.2
- **CMS**: Wagtail 6.4
- **Frontend**: Bootstrap 5
- **Database**: PostgreSQL 16 (production), SQLite (development)
- **Cache**: Redis 7 (production), local memory (development)
- **Media**: AWS S3 (audio files, images)
- **Tags**: django-taggit
- **Email**: Mailgun via django-anymail
- **Package Manager**: uv

## Deployment

The site runs on a DigitalOcean $6/month Droplet. The stack runs as Docker containers managed by Docker Compose.

### Architecture

```text
Internet
  │
  ▼
Traefik v3.1  ──  TLS termination (Let's Encrypt) + HTTP→HTTPS redirect
  │
  ▼
Gunicorn  ──  1 worker, 120s timeout
  │
  ├── PostgreSQL 16  ──  shared_buffers=64MB, max_connections=25
  ├── Redis 7  ──  64MB max, allkeys-lru eviction
  └── AWS S3  ──  static files + media (audio, images)
```

### CI/CD Pipeline

GitHub Actions workflows:

**CI** -- linting (ruff, djLint), pytest, migration consistency check.

**Deploy** -- build Docker image, push to GHCR, collectstatic to S3, deploy to droplet.
