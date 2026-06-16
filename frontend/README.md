# Agentic AI Frontend

React + TypeScript + Vite frontend for the **Agentic AI Development Assistant**. This SPA communicates with the Django backend API and is served as static assets in production through the Antigravity runtime environment.

---

## Architecture

```
frontend/
├── index.html              # Vite HTML entry point
├── package.json            # Dependencies and scripts
├── vite.config.ts          # Vite configuration (proxy, build)
├── tsconfig.json           # TypeScript project references
├── tsconfig.app.json       # App TypeScript config
├── tsconfig.node.json      # Node/Vite TypeScript config
├── .env.example            # Environment variable template
└── src/
    ├── main.tsx            # React entry point
    ├── App.tsx             # Root component
    ├── App.css             # Global styles (design system)
    ├── vite-env.d.ts       # Vite + env type declarations
    ├── lib/
    │   └── api.ts          # Centralized API client
    ├── hooks/
    │   ├── useAgent.ts     # Agent interaction hook
    │   └── useHistory.ts   # History fetching hook
    └── context/
        └── ApiContext.tsx  # API configuration provider
```

---

## Quick Start

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Environment

```bash
# Copy the template
cp .env.example .env
```

Edit `.env` — in development, leave `VITE_API_BASE_URL` empty (the Vite dev proxy handles API routing):

```env
VITE_API_BASE_URL=
```

### 3. Start Development Server

```bash
# Start the Django backend first (in a separate terminal):
cd ../backend
python manage.py runserver

# Then start the Vite dev server:
cd ../frontend
npm run dev
```

The frontend runs at `http://localhost:5173`. All `/api/*` requests are proxied to `http://127.0.0.1:8000` automatically.

### 4. Production Build

```bash
npm run build
```

Output goes to `dist/`. The Django backend serves this directory as static assets in production.

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `VITE_API_BASE_URL` | No | `""` (empty) | Base URL for API requests. Empty = same origin (works with Vite proxy in dev, and same-origin deployment in prod). Set to full URL for cross-origin deployments. |

### `.env.example`

```env
# Development (Vite proxy handles routing)
VITE_API_BASE_URL=

# Production — same-origin deployment
# VITE_API_BASE_URL=

# Production — cross-origin deployment
# VITE_API_BASE_URL=https://your-backend.onrender.com
```

---

## API Integration

All API communication is centralized in `src/lib/api.ts`. **No hardcoded URLs exist anywhere in the codebase.** Every request resolves the base URL from `import.meta.env.VITE_API_BASE_URL`.

### Available Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/agent/` | Send a prompt to the AI agent |
| `GET` | `/api/history/` | Fetch conversation history |

### Custom Hooks

| Hook | Purpose |
|------|---------|
| `useAgent()` | Manages loading/error/result state for agent requests |
| `useHistory()` | Fetches and caches conversation history; exposes `refetch()` |
| `useApiConfig()` | Reads the resolved API base URL from context |

---

## Django Backend Integration

The frontend is designed to be served by the Django backend in production:

1. **Build** the frontend: `npm run build`
2. **Copy** `dist/` → `backend/frontend_dist/`
3. **Run** `python manage.py collectstatic`
4. Django serves `index.html` at `/` and hashed assets from `/static/`

The `backend/build.sh` script automates all of these steps.

---

## Scripts

| Script | Command | Description |
|--------|---------|-------------|
| `dev` | `npm run dev` | Start Vite dev server with hot reload |
| `build` | `npm run build` | TypeScript check + production build |
| `preview` | `npm run preview` | Preview the production build locally |
| `lint` | `npm run lint` | Run ESLint on source files |

---

## Tech Stack

| Technology | Version | Purpose |
|-----------|---------|----------|
| React | 19.1 | UI framework |
| TypeScript | 5.8 | Type safety |
| Vite | 6.3 | Build tool and dev server |
| Inter (Google Fonts) | — | Typography |
