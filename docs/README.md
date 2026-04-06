# Finance API GitHub Pages Docs

This directory is deployed to GitHub Pages using `.github/workflows/pages-deploy.yml`.

## Scope

- Static docs landing pages
- API endpoint summary
- Local backend setup guide
- Architecture boundary notes

## Runtime Docs

The live interactive API docs are served by Django when running the backend:

- `http://127.0.0.1:8000/docs/`
- `http://127.0.0.1:8000/redoc/`

## Deployment Trigger Note

This line was updated to force a fresh GitHub Pages deployment run from `main`.
