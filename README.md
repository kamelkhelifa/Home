# Kamel Khelifa-Kerfa: academic website

Personal academic website of Dr Kamel Khelifa-Kerfa, Associate Professor of Physics at Qatar University.
It replaces the WordPress site at [khelifak.wordpress.com](https://khelifak.wordpress.com/).

**Sections:** Home · Studying (Physics at Manchester, Medicine at Chlef) · Teaching (Qatar University + archive) ·
Research (themes, publications, grants, talks) · Books · Resources (websites, channels, projects, articles).

It is a static site: plain HTML and CSS plus a little vanilla JavaScript, with no frameworks and no tracking.
It supports light and dark themes, works on phones, and loads fast.

---

## Editing content (no coding needed)

All content lives in the `data/` folder as plain YAML text files. You can edit them directly on GitHub
(open the file, click the pencil ✏️, then **Commit changes**). The site rebuilds and redeploys automatically in about a minute.

| File | What it controls |
|------|------------------|
| `data/site.yml` | Name, title, bio, email, research-profile links, menu |
| `data/studying.yml` | Physics & medicine timelines, MPhys notes archive, medical study channels |
| `data/teaching.yml` | Current courses, previous universities & courses, workshops, supervision |
| `data/research.yml` | Research themes, **publications**, grants, talks, service, labs |
| `data/books.yml` | Authored books/theses/notes and the textbook shelf |
| `data/resources.yml` | Websites, YouTube/Telegram channels, conference sites, projects, articles |

Common tasks:

- **Add a paper:** copy an entry at the top of `publications:` in `data/research.yml` and edit it.
  `type` is `journal` or `proceedings`. `area` is `qcd`, `materials` or `ew`. Add `status: accepted` for accepted papers.
  The home-page counters update automatically.
- **Add a book:** copy a block under `authored:` in `data/books.yml`. To use a real cover, put the image in
  `static/img/books/` and add `cover: my-cover.jpg`.
- **Add a link to a channel:** add `url: https://…` to that item in `data/resources.yml`.
- **Add a portrait photo:** save a square photo as `static/img/portrait.jpg`. It replaces the "KK" monogram on the home page.
- **Add a downloadable CV:** save it as `static/files/CV.pdf`. A "CV" button appears on the home page.
- **New semester:** update `current:` in `data/teaching.yml`, and move the old courses into `archive:`.

YAML tip: if a value contains a colon `:`, `#` or `?`, wrap it in "double quotes".

## Publishing on GitHub Pages (one-time setup)

1. Create a repository on GitHub. Name it `<your-username>.github.io` for the address `https://<your-username>.github.io`,
   or any other name for `https://<your-username>.github.io/<repo-name>/`.
2. Push this folder to the `main` branch.
3. In the repository, open **Settings → Pages → Build and deployment → Source** and choose **GitHub Actions**.
4. Set `base_url` in `data/site.yml` to the final address. It is used for the sitemap, social previews and the 404 page.

The workflow in `.github/workflows/pages.yml` builds and deploys on every push.

**Custom domain (optional):** put the domain (for example `khelifak.com`) in a file named `CNAME` at the repository root,
point your DNS at GitHub Pages, and set `base_url` to `https://khelifak.com`.

## Building locally (optional)

```bash
pip install -r requirements.txt
python build.py                 # writes the site to _site/
python -m http.server -d _site  # preview at http://localhost:8000
```

## Structure

```
data/        content (YAML)
templates/   page layouts (Jinja2)
static/      css, js, images, files → copied to _site/assets/
build.py     the build script
```
