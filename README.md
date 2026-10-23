# Kamel Khelifa-Kerfa: academic website · الموقع الأكاديمي

The bilingual (English / العربية) personal website of Dr Kamel Khelifa-Kerfa, Associate Professor of Physics at Qatar University.
It replaces the WordPress site [khelifak.wordpress.com](https://khelifak.wordpress.com/). Course pages live on the companion site
[TeachWeb](https://kamelkhelifa.github.io/TeachWeb/); everything else from the old site has been migrated here.

- **English:** `https://kamelkhelifa.github.io/Home/`
- **العربية:** `https://kamelkhelifa.github.io/Home/ar/`

**Sections:** Home · Studying (Physics at Manchester, Medicine at Chlef) · Teaching (every course, linked to TeachWeb) ·
Research · Books · Resources (websites, channels, HEP software guides, articles).

It is a static site: plain HTML and CSS plus a little vanilla JavaScript, with no frameworks and no tracking. It supports light and dark themes,
right-to-left Arabic, and phones.

---

## How content is organised

| Where | What | Language |
|-------|------|----------|
| `data/*.yml` | Structured content: profile, courses, publications, books, links | Each text is `{ en: …, ar: … }` |
| `data/i18n.yml` | Interface words (buttons, headings, labels) | `{ en: …, ar: … }` |
| `content/en/…` and `content/ar/…` | Full pages: MPhys notes, medicine years, software guides, articles | One file per language |

### Editing on GitHub (no coding needed)
Open a file, click ✏️, edit, then **Commit changes**. The site rebuilds and redeploys automatically in about a minute.

- **Change any text:** find it in `data/` and edit both the `en:` and the `ar:` lines.
- **Add a paper:** copy an entry at the top of `publications:` in `data/research.yml`. Paper titles stay in English.
  `type` is `journal` or `proceedings`; `area` is `qcd`, `materials` or `ew`; add `status: accepted` if it applies.
- **New semester:** edit `current:` in `data/teaching.yml`.
- **Add a course:** add it to the right university in `data/teaching.yml` with `teachweb: taught/<university>/<course>`.
  This is the course's path on TeachWeb. The course card then opens that page, in the reader's language.
- **Add a full page** (notes, guide, article): write `content/en/<section>/<name>.html` and `content/ar/<section>/<name>.html`
  (plain HTML starting at `<h2>`; headings become the table of contents), then reference it with `page: <section>/<name>`
  in `data/studying.yml` or `data/resources.yml`. Inside a page, link to another page with `href="@@resources/herwig"`.
- **Books:** in `data/books.yml`, copy a block under `theses:`, `notes:` or a group of `in_progress:`. When a book is published,
  move it out of `in_progress` and add `url:`. A real cover image can go in `static/img/books/`, referenced with `cover:`.
- **Portrait photo:** save it as `static/img/portrait.jpg`.
- **Downloadable CV:** save it as `static/files/CV.pdf`.

YAML tip: wrap any value containing `:`, `#` or `?` in "double quotes".

## Launch switch
While `launched: false` in `data/site.yml`, every page carries a `noindex` tag, so search engines will not list the site.
Anyone with the link can still open it. On launch day, set `launched: true` and commit.

## Publishing (one-time setup)
1. In the repository: **Settings → Pages → Build and deployment → Source → GitHub Actions**.
2. Push to `main`. The workflow `.github/workflows/pages.yml` builds and deploys the site.
3. **Custom domain (optional):**
   - put the domain in a file named `CNAME` at the repository root
   - point your DNS at GitHub Pages
   - set `base_url` in `data/site.yml`

## Files from the old site
PDFs, slides and images linked from the migrated pages are still served from the WordPress file store
(`khelifak.wordpress.com/wp-content/uploads/…`). Keep the WordPress site online, or set it to private but don't delete it,
until those files are copied here (to `static/files/`) and the links updated.

## Building locally (optional)
```bash
pip install -r requirements.txt
python build.py                  # writes the site to _site/ (English at /, Arabic at /ar/)
python -m http.server -d _site   # preview at http://localhost:8000
```

`tools/wp_import.py` is the one-off importer used to convert the WordPress export into `content/`.
