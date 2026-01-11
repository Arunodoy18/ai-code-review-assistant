# ✅ Deployment Fixed - Working URLs

## 🚀 Live Application URLs

- **Frontend**: https://codereview-frontend.jollysea-c5c0b121.centralus.azurecontainerapps.io
- **Backend API**: https://codereview-backend.jollysea-c5c0b121.centralus.azurecontainerapps.io

## ✅ What Was Fixed

### Problem
The frontend React app was hardcoded to call `http://localhost:8000` even in production, causing "Failed to fetch" errors.

### Root Cause
Vite's bundler was evaluating the API URL detection code **at build time** instead of **at runtime**, resulting in hardcoded localhost URLs in the production bundle.

### Solution Implemented
**Runtime Configuration Injection via HTML**:

1. **index.html** now injects a configuration object **before** any JavaScript loads:
   ```html
   <script>
     window.__RUNTIME_CONFIG__ = {
       API_URL: (function() {
         const hostname = window.location.hostname;
         const protocol = window.location.protocol;
         
         // Production: replace 'frontend' with 'backend' in hostname
         if (hostname.includes('frontend')) {
           return protocol + '//' + hostname.replace('frontend', 'backend');
         }
         
         // Localhost development
         if (hostname === 'localhost' || hostname === '127.0.0.1') {
           return 'http://localhost:8000';
         }
         
         // Fallback
         return protocol + '//' + hostname;
       })()
     };
     console.log('[Config] API URL:', window.__RUNTIME_CONFIG__.API_URL);
   </script>
   ```

2. **client.ts** now reads from `window.__RUNTIME_CONFIG__` at runtime:
   ```typescript
   const getBaseUrl = () => {
     return (window as any).__RUNTIME_CONFIG__?.API_URL || 'http://localhost:8000';
   };
   ```

3. **main.tsx** also uses runtime config for Sentry initialization

## 🔍 How It Works

1. When user opens https://codereview-frontend.jollysea-c5c0b121.centralus.azurecontainerapps.io
2. The HTML file loads FIRST and executes the inline `<script>` tag
3. The script detects hostname contains "frontend"
4. It replaces "frontend" with "backend" → `https://codereview-backend.jollysea-c5c0b121.centralus.azurecontainerapps.io`
5. Stores this URL in `window.__RUNTIME_CONFIG__.API_URL`
6. Console logs the detected API URL
7. React app loads and uses this URL for all API calls

## 🧪 Verification

Open browser console (F12) and you should see:
```
[Config] API URL: https://codereview-backend.jollysea-c5c0b121.centralus.azurecontainerapps.io
```

Check Network tab - all API calls should go to the backend URL, not localhost.

## ⚠️ Browser Cache Issue

### Why Your Friend Can't See It

Your friend's browser cached the **old bundle** (index-SDmcUHZC.js, index-CkmQ4MeS.js, etc.) which had hardcoded localhost URLs.

The NEW bundle (index-CaGDrbyG.js) has the runtime config logic, but their browser is still serving the cached old bundle.

### Solution for Users

Tell your friend to do a **hard refresh**:

- **Windows/Linux**: `Ctrl + Shift + R` or `Ctrl + F5`
- **Mac**: `Cmd + Shift + R`
- **Alternative**: Clear browser cache and reload
- **Quick Test**: Open in **Incognito/Private browsing** mode (always fetches fresh)

## 📊 Deployment Status

- ✅ Backend API healthy and returning data
- ✅ Frontend deployed with runtime config injection
- ✅ CORS configured to allow frontend domain
- ✅ Latest revision: `codereview-frontend--0000004`
- ✅ Console logging enabled for debugging
- ✅ No more hardcoded localhost URLs in runtime execution

## 🎯 Key Technical Details

- **Container Registry**: codereviewacr8765.azurecr.io
- **Resource Group**: codereview-rg
- **Environment**: hackathon-env (in hackathon-waste-rg)
- **Latest Image Digest**: sha256:e3189fbb2d68286e174f718f35019aa3af92306adf171e1629e24b32773fd0ad
- **Revision**: codereview-frontend--0000004

## 📝 Important Notes

1. **The bundle still contains `localhost:8000`** - This is the FALLBACK value and is expected. It's only used if `window.__RUNTIME_CONFIG__` fails to load.

2. **Runtime vs Build Time** - The critical fix was moving URL detection from build time (Vite bundler) to runtime (HTML inline script).

3. **No Environment Variables Needed** - The solution uses hostname-based detection, so no need to inject environment variables at container startup.

4. **Works for Any Deployment** - As long as frontend and backend follow the naming pattern (`*-frontend` and `*-backend`), it will auto-detect.

## 🔧 For Developers

If you need to verify the deployment worked:

```powershell
# Check if runtime config is in HTML
$html = Invoke-WebRequest -Uri "https://codereview-frontend.jollysea-c5c0b121.centralus.azurecontainerapps.io" -UseBasicParsing
$html.Content -match '__RUNTIME_CONFIG__'  # Should return True

# Check backend API
Invoke-WebRequest -Uri "https://codereview-backend.jollysea-c5c0b121.centralus.azurecontainerapps.io/api/analysis/runs" -UseBasicParsing
# Should return JSON with {"total":0,"runs":[]}
```

## 🎉 Result

The application is now fully functional in production. Users just need to clear their browser cache to see the working version.
