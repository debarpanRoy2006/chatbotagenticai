#!/usr/bin/env bash

# ──────────────────────────────────────────────────────────
# Unified Build Script — Antigravity Platform
# Builds the React frontend and Django backend in sequence.
# ──────────────────────────────────────────────────────────

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "══════════════════════════════════════════════════════"
echo "  Antigravity Platform — Unified Build"
echo "══════════════════════════════════════════════════════"

# ── Phase 1: Frontend Build ──
echo ""
echo "▸ Phase 1/3: Building React frontend..."
FRONTEND_DIR="$PROJECT_ROOT/frontend"

if [ -d "$FRONTEND_DIR" ] && [ -f "$FRONTEND_DIR/package.json" ]; then
    cd "$FRONTEND_DIR"
    npm ci --prefer-offline --no-audit
    npm run build
    echo "  ✓ Frontend built successfully → $FRONTEND_DIR/dist/"
else
    echo "  ⚠ Frontend directory not found. Skipping frontend build."
fi

# ── Phase 2: Stage Frontend Assets for Django ──
echo ""
echo "▸ Phase 2/3: Staging frontend assets for Django..."
FRONTEND_DIST="$FRONTEND_DIR/dist"
DJANGO_FRONTEND_DIST="$SCRIPT_DIR/frontend_dist"

if [ -d "$FRONTEND_DIST" ]; then
    rm -rf "$DJANGO_FRONTEND_DIST"
    cp -r "$FRONTEND_DIST" "$DJANGO_FRONTEND_DIST"
    echo "  ✓ Frontend assets staged → $DJANGO_FRONTEND_DIST/"
else
    echo "  ⚠ Frontend dist/ not found. Skipping asset staging."
fi

# ── Phase 3: Django Backend Build ──
echo ""
echo "▸ Phase 3/3: Building Django backend..."
cd "$SCRIPT_DIR"

pip install --upgrade pip
echo "  Installing Python dependencies..."
pip install -r requirements.txt

echo "  Collecting static files..."
python manage.py collectstatic --noinput

echo ""
echo "══════════════════════════════════════════════════════"
echo "  ✓ Build complete."
echo "══════════════════════════════════════════════════════"