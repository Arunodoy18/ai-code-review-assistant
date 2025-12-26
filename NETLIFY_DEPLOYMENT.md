# 🚀 Netlify Deployment Guide

This guide will help you deploy the AI Code Review Assistant to get a live URL for LinkedIn.

## 📋 Architecture

- **Frontend**: Netlify (Static React App)
- **Backend**: Render.com (Free tier with PostgreSQL + Redis)

## 🎯 Step-by-Step Deployment

### Part 1: Deploy Backend to Render (Free)

1. **Create Render Account**
   - Go to https://render.com
   - Sign up with GitHub

2. **Connect Your Repository**
   - Click "New +" → "Blueprint"
   - Connect your GitHub repository
   - Render will automatically detect the `render.yaml` file
   - Click "Apply" to create all services (Backend, PostgreSQL, Redis)

3. **Set Environment Variables** (in Render Dashboard)
   ```
   GITHUB_APP_ID=your_github_app_id
   GITHUB_WEBHOOK_SECRET=your_webhook_secret
   OPENAI_API_KEY=your_openai_key (optional for demo)
   ```

4. **Get Your Backend URL**
   - After deployment completes, copy the backend URL
   - Example: `https://ai-code-review-backend.onrender.com`

5. **Initialize Database**
   - In Render Dashboard → ai-code-review-backend → Shell
   - Run:
     ```bash
     python init_db.py
     python seed_test_data.py
     ```

### Part 2: Deploy Frontend to Netlify

1. **Create Netlify Account**
   - Go to https://netlify.com
   - Sign up with GitHub

2. **Deploy via Git**
   - Click "Add new site" → "Import an existing project"
   - Choose GitHub and select your repository
   - Netlify will auto-detect the `netlify.toml` configuration

3. **Set Environment Variable**
   - In Netlify Dashboard → Site settings → Environment variables
   - Add:
     ```
     VITE_API_URL = https://your-backend-url.onrender.com
     ```
   - Replace with your actual Render backend URL from Part 1

4. **Deploy**
   - Click "Deploy site"
   - Wait 2-3 minutes for build to complete

5. **Get Your Live URL**
   - Netlify will provide a URL like: `https://your-app-name.netlify.app`
   - You can customize the subdomain in Site settings → Domain management

### Part 3: Configure Backend CORS

1. **Update Backend for Netlify Frontend**
   - In Render Dashboard → ai-code-review-backend → Environment
   - Add/Update:
     ```
     FRONTEND_URL=https://your-app-name.netlify.app
     ```
   - This allows the frontend to make API calls to the backend

### Part 4: Test Your Deployment

1. **Visit Your Netlify URL**
   - Example: `https://ai-code-review.netlify.app`

2. **Check the Dashboard**
   - You should see the dashboard with sample data
   - Check browser console for any errors

3. **Test API Connection**
   - Dashboard should show projects and analysis runs
   - If you see "Failed to fetch", check:
     - VITE_API_URL is correct in Netlify
     - FRONTEND_URL is correct in Render
     - Backend is running (check Render logs)

## 🎉 You're Live!

Your URL: `https://your-app-name.netlify.app`

### LinkedIn Post Template

```
🚀 Excited to share my latest project: AI-Powered Code Review Assistant!

✨ Features:
• AI-powered code analysis using GPT-4/Claude
• 24+ rule-based checks for security, quality & performance
• Real-time dashboard with interactive visualizations
• GitHub integration for automated PR reviews

🛠️ Tech Stack:
• Backend: Python, FastAPI, PostgreSQL, Redis
• Frontend: React, TypeScript, TailwindCSS
• AI: OpenAI API, LLM-powered suggestions

Try it live: https://your-app-name.netlify.app

GitHub: https://github.com/yourusername/ai-code-review

#AI #MachineLearning #CodeReview #Python #React #OpenSource
```

## ⚙️ Optional: Custom Domain

1. **In Netlify Dashboard**
   - Go to Domain management
   - Add custom domain (e.g., `codereview.yourdomain.com`)
   - Netlify provides free SSL certificate

## 🐛 Troubleshooting

### Frontend shows "Failed to fetch"
- Check VITE_API_URL in Netlify environment variables
- Verify backend is running on Render
- Check browser console for CORS errors

### Backend not responding
- Check Render logs for errors
- Verify PostgreSQL and Redis services are running
- Check DATABASE_URL and REDIS_URL are set

### Database errors
- Make sure you ran `init_db.py` in Render shell
- Check PostgreSQL service is running

### GitHub webhooks not working
- Update webhook URL in GitHub App settings
- Use: `https://your-backend.onrender.com/api/webhooks/github`

## 💰 Cost

- **Render**: $0/month (Free tier - 750 hours/month)
- **Netlify**: $0/month (Free tier - 100GB bandwidth)
- **Total**: FREE for demo/portfolio projects

## 📊 Free Tier Limits

**Render:**
- 512 MB RAM
- Shared CPU
- PostgreSQL 256MB (expires after 90 days)
- Spins down after 15 min inactivity (cold starts)

**Netlify:**
- 100 GB bandwidth/month
- 300 build minutes/month
- Unlimited sites

## 🔄 Continuous Deployment

Both platforms auto-deploy when you push to GitHub:
- Push to `main` branch → Auto-deploy backend (Render) + frontend (Netlify)

## 📱 Mobile Responsive

The app is fully responsive and works on:
- Desktop (Chrome, Firefox, Safari, Edge)
- Tablet
- Mobile

---

Need help? Check the logs in:
- **Netlify**: Deploy logs in Netlify Dashboard
- **Render**: Logs tab in each service
