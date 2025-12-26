#!/bin/bash
# Quick Netlify Deployment Script
# This script helps you prepare for deployment

echo "🚀 AI Code Review - Netlify Deployment Checker"
echo "=============================================="
echo ""

# Check if git repo is clean
if [[ -n $(git status -s) ]]; then
    echo "⚠️  Warning: You have uncommitted changes"
    echo "   Commit and push your changes before deploying"
    git status -s
    echo ""
else
    echo "✅ Git repository is clean"
fi

# Check if on main branch
current_branch=$(git branch --show-current)
if [ "$current_branch" != "main" ]; then
    echo "⚠️  Warning: You're on branch '$current_branch'"
    echo "   Netlify typically deploys from 'main' branch"
    echo ""
else
    echo "✅ On main branch"
fi

echo ""
echo "📋 Pre-Deployment Checklist:"
echo "=============================="
echo ""
echo "Backend (Render.com):"
echo "  [ ] Created Render account"
echo "  [ ] Connected GitHub repository"
echo "  [ ] Deployed via render.yaml blueprint"
echo "  [ ] Set environment variables (GITHUB_APP_ID, etc.)"
echo "  [ ] Ran init_db.py in Render shell"
echo "  [ ] Copied backend URL"
echo ""
echo "Frontend (Netlify):"
echo "  [ ] Created Netlify account"
echo "  [ ] Connected GitHub repository"
echo "  [ ] Set VITE_API_URL environment variable"
echo "  [ ] Deployed site"
echo "  [ ] Updated FRONTEND_URL in Render backend"
echo ""
echo "Testing:"
echo "  [ ] Visit Netlify URL"
echo "  [ ] Check dashboard loads"
echo "  [ ] Verify API calls work"
echo "  [ ] Test on mobile"
echo ""
echo "📖 Full Guide: See NETLIFY_DEPLOYMENT.md"
echo ""
echo "🔗 Quick Links:"
echo "   Render:  https://dashboard.render.com"
echo "   Netlify: https://app.netlify.com"
echo ""
