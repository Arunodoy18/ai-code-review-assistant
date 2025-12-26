# Quick Netlify Deployment Script
# This script helps you prepare for deployment

Write-Host "AI Code Review - Netlify Deployment Checker" -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host ""

# Check if git repo is clean
$gitStatus = git status -s
if ($gitStatus) {
    Write-Host "Warning: You have uncommitted changes" -ForegroundColor Yellow
    Write-Host "   Commit and push your changes before deploying" -ForegroundColor Yellow
    git status -s
    Write-Host ""
} else {
    Write-Host "Git repository is clean" -ForegroundColor Green
}

# Check if on main branch
$currentBranch = git branch --show-current
if ($currentBranch -ne "main") {
    Write-Host "Warning: You're on branch '$currentBranch'" -ForegroundColor Yellow
    Write-Host "   Netlify typically deploys from 'main' branch" -ForegroundColor Yellow
    Write-Host ""
} else {
    Write-Host "On main branch" -ForegroundColor Green
}

Write-Host ""
Write-Host "Pre-Deployment Checklist:" -ForegroundColor Cyan
Write-Host "==============================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Backend (Render.com):" -ForegroundColor White
Write-Host "  [ ] Created Render account"
Write-Host "  [ ] Connected GitHub repository"
Write-Host "  [ ] Deployed via render.yaml blueprint"
Write-Host "  [ ] Set environment variables"
Write-Host "  [ ] Ran init_db.py in Render shell"
Write-Host "  [ ] Copied backend URL"
Write-Host ""
Write-Host "Frontend (Netlify):" -ForegroundColor White
Write-Host "  [ ] Created Netlify account"
Write-Host "  [ ] Connected GitHub repository"
Write-Host "  [ ] Set VITE_API_URL environment variable"
Write-Host "  [ ] Deployed site"
Write-Host "  [ ] Updated FRONTEND_URL in Render backend"
Write-Host ""
Write-Host "Testing:" -ForegroundColor White
Write-Host "  [ ] Visit Netlify URL"
Write-Host "  [ ] Check dashboard loads"
Write-Host "  [ ] Verify API calls work"
Write-Host "  [ ] Test on mobile"
Write-Host ""
Write-Host "Full Guide: See NETLIFY_DEPLOYMENT.md" -ForegroundColor Cyan
Write-Host ""
Write-Host "Quick Links:" -ForegroundColor Cyan
Write-Host "   Render:  https://dashboard.render.com"
Write-Host "   Netlify: https://app.netlify.com"
Write-Host ""
