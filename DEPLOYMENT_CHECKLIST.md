# Antigravity Platform — Frontend Deployment Checklist

This checklist ensures the React frontend is correctly built, staged, and integrated with the Django backend for the Antigravity agent harness to serve.

---

## Prerequisites

| Tool | Minimum Version | Check Command |
|------|----------------|---------------|
| Node.js | 18.x LTS | `node --version` |
| npm | 9.x | `npm --version` |
| Python | 3.10+ | `python --version` |
| pip | 23.x | `pip --version` |

---

## Step-by-Step Deployment

### Phase 1: Frontend Build

```bash
# 1. Navigate to the frontend directory
cd frontend/

# 2. Install dependencies (clean install for CI)
npm ci

# 3. Create the production .env (if not already present)
cp .env.example .env
# Edit .env to set VITE_API_BASE_URL for your target environment:
#   - Same-origin deployment: leave VITE_API_BASE_URL empty
#   - Cross-origin deployment: set to backend URL
#     e.g., VITE_API_BASE_URL=https://your-backend.onrender.com

# 4. Build the production bundle
npm run build

# 5. Verify the build output
ls dist/
#   Expected: index.html, assets/ (with .js and .css files)
```

### Phase 2: Stage Assets for Django

```bash
# 6. Copy the build output into the Django project
#    (The build.sh script does this automatically, but for manual deployment:)
cd ..
cp -r frontend/dist/ backend/frontend_dist/

# 7. Verify the staged assets
ls backend/frontend_dist/
#   Expected: index.html, assets/, vite.svg
```

### Phase 3: Django Backend Build

```bash
# 8. Navigate to the backend directory
cd backend/

# 9. Install Python dependencies
pip install -r requirements.txt

# 10. Collect static files (picks up React assets)
python manage.py collectstatic --noinput

# 11. Verify static files were collected
ls staticfiles/
```

### Phase 4: Antigravity Harness Verification

```bash
# 12. Start the Django server
python manage.py runserver 0.0.0.0:8000

# 13. Verify the following endpoints:
#   GET  /              → Should serve React SPA (or legacy template if no build)
#   POST /api/agent/    → Should return JSON response
#   GET  /api/history/  → Should return JSON history array
#   GET  /admin/        → Should serve Django admin
```

---

## Environment Variable Matrix

| Variable | Location | Required | Description |
|----------|----------|----------|-------------|
| `VITE_API_BASE_URL` | `frontend/.env` | No | Backend API URL. Empty = same origin. |
| `GEMINI_API_KEY` | `backend/.env` | **Yes** | Google Gemini API key |
| `DJANGO_SECRET_KEY` | Server env | Prod only | Django secret key for production |
| `RENDER_EXTERNAL_HOSTNAME` | Server env | Render only | Auto-set by Render |
| `DATABASE_URL` | Server env | Render only | PostgreSQL connection string |
| `RENDER_FRONTEND_URL` | Server env | Render only | Frontend origin for CORS |

---

## Automated Build (CI/CD)

The unified build script handles all phases automatically:

```bash
# From the backend/ directory:
chmod +x build.sh
./build.sh
```

This script:
1. ✅ Builds the React frontend (`npm ci && npm run build`)
2. ✅ Copies `frontend/dist/` → `backend/frontend_dist/`
3. ✅ Installs Python dependencies
4. ✅ Runs `collectstatic`

---

## Pre-Flight Verification

```bash
# Type-check the frontend
cd frontend && npx tsc --noEmit

# Verify no circular imports (check for warnings)
npm ls 2>&1 | grep -i "circular"

# Dry-run collectstatic
cd ../backend && python manage.py collectstatic --noinput --dry-run

# Verify SPA middleware is registered (production settings)
python -c "from agent_ai_project.deployment_settings import MIDDLEWARE; print('SPA middleware:', 'spa_middleware' in str(MIDDLEWARE))"
```

---

## Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| React app not loading at `/` | `frontend/dist/` not built or not copied | Run `npm run build` in `frontend/`, then copy `dist/` → `backend/frontend_dist/` |
| API calls fail with CORS error | `CORS_ALLOWED_ORIGINS` not set | Add frontend URL to `CORS_ALLOWED_ORIGINS` in `deployment_settings.py` |
| Static assets return 404 | `collectstatic` not run | Run `python manage.py collectstatic --noinput` |
| Client-side routes return 404 | SPA middleware not active | Ensure `SPAFallbackMiddleware` is in `MIDDLEWARE` list |
| Legacy template shown instead of React | Build not found at `FRONTEND_BUILD_DIR` | Verify `frontend_dist/index.html` exists in `backend/` |
