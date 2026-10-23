# Kamel Khelifa-Kerfa: academic website · الموقع الأكاديمي

The bilingual (English / العربية) personal website of Dr Kamel Khelifa-Kerfa, Associate Professor of Physics at Qatar University.
It replaces the WordPress site [khelifak.wordpress.com](https://khelifak.wordpress.com/); all of that site's published pages have been migrated here.

- **English:** `https://kamelkhelifa.github.io/home/`
- **العربية:** `https://kamelkhelifa.github.io/home/ar/`

**Sections:** Home · Studying (Physics at Manchester, Medicine at Chlef) · Teaching (Qatar University + 30 archived course pages) ·
Research · Books · Resources (websites, channels, HEP software guides, articles).

It is a static site: plain HTML and CSS plus a little vanilla JavaScript, with no frameworks and no tracking. It supports light and dark themes,
right-to-left Arabic, and phones.

---

## How content is organised

| Where | What | Language |
|-------|------|----------|
| `data/*.yml` | Structured content: profile, courses, publications, books, links | Each text is `{ en: …, ar: … }` |
| `data/i18n.yml` | Interface words (buttons, headings, labels) | `{ en: …, ar: … }` |
| `content/en/…` and `content/ar/…` | Full pages: course pages, MPhys notes, medicine years, software guides, articles | One file per language |
| `content/fr/…` | French originals of courses taught in French (kept for reference, not published) | — |

### Editing on GitHub (no coding needed)
Open a file, click ✏️, edit, then **Commit changes**. The site rebuilds and redeploys automatically in about a minute.

- **Change any text:** find it in `data/` and edit both the `en:` and the `ar:` lines.
- **Add a paper:** copy an entry at the top of `publications:` in `data/research.yml`. Paper titles stay in English.
  `type` is `journal` or `proceedings`; `area` is `qcd`, `materials` or `ew`; add `status: accepted` if it applies.
- **New semester:** edit `current:` in `data/teaching.yml`.
- **Add a course page:**
  1. Write `content/en/teaching/<name>.html` and `content/ar/teaching/<name>.html`. They are plain HTML, starting at `<h2>` headings.
  2. Add the course to the right university in `data/teaching.yml` with `page: teaching/<name>`.
  3. Headings become the page's table of contents automatically.
  4. To link to another page of the site from inside a page, write `href="@@teaching/phys321"`.
- **Add a book:** copy a block under `authored:` in `data/books.yml`. A real cover image can go in `static/img/books/`, referenced with `cover:`.
- **Portrait photo:** save it as `static/img/portrait.jpg`.
- **Downloadable CV:** save it as `static/files/CV.pdf`.

YAML tip: wrap any value containing `:`, `#` or `?` in "double quotes".

## Publishing (one-time setup)
1. In the repository: **Settings → Pages → Build and deployment → Source → GitHub Actions**.
2. Push to `main`. The workflow `.github/workflows/pages.yml` builds and deploys the site.
3. **Custom domain (optional):**
   - put the domain in a file named `CNAME` at the repository root
   - point your DNS at GitHub Pages
   - set `base_url` in `data/site.yml`

## Files from the old site
PDFs, slides and images linked from course pages are still served from the WordPress file store
(`khelifak.wordpress.com/wp-content/uploads/…`). Keep the WordPress site online, or set it to private but don't delete it,
until those files are copied here (to `static/files/`) and the links updated.

## Building locally (optional)
```bash
pip install -r requirements.txt
python build.py                  # writes the site to _site/ (English at /, Arabic at /ar/)
python -m http.server -d _site   # preview at http://localhost:8000
```

`tools/wp_import.py` is the one-off importer used to convert the WordPress export into `content/`.
