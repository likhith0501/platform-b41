# Deployment TODO (GitHub Actions + GitHub Pages + Render backend)

## Publish-ready requirements
- [x] Frontend is now frontend-only (no backend URL / API key needed).
- [ ] (Optional) If backend is still deployed, ensure production readiness via `gunicorn` and `/health`.
- [ ] (Optional) API key handling if you continue to use backend endpoints.


## Frontend (GitHub Pages)
- [ ] Confirm Vite `base` matches repo path: `/platform-b41/`.
- [ ] Add/confirm GitHub Actions workflow to build and deploy frontend to GitHub Pages (existing workflow).

## Backend (Render)
- [ ] Replace placeholder backend workflow with a workflow that deploys backend to Render (if using Render Git integration).
- [ ] Or: add a clear Render deployment manifest/docs + Render webhook instructions.

## Repo hygiene
- [ ] Add/confirm `.env` is excluded from Git (existing root + frontend .gitignore; verify backend .env).
- [ ] Add root README with step-by-step local dev and production URLs.

## Final verification checklist
- [ ] After push to `main`: GitHub Pages deploys successfully.
- [ ] Backend health endpoint responds on Render.
- [ ] Frontend can call backend from Pages URL with correct CORS and env config.

