# Distribution & Publishing Guide

This guide explains how to publish your application to GitHub, deploy the frontend to Vercel, and package the product for your clients.

## 1. Publishing to GitHub (Open Source / Private Repo)

To share your code or collaborate, you should push it to GitHub.

### Steps:
1.  **Initialize Git** (if not already done):
    ```bash
    git init
    git add .
    git commit -m "Initial release v1.0"
    ```
2.  **Create a Repository** on [GitHub.com](https://github.com/new).
3.  **Push the code**:
    ```bash
    git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
    git branch -M main
    git push -u origin main
    ```
4.  **Add a License**: If this is for public use, add a `LICENSE` file (e.g., MIT, Apache 2.0) so users know how they can use it.

---

## 2. Publishing to Vercel (Frontend Only)

Vercel is excellent for hosting the React Frontend. However, since your application has a Python Backend, **Vercel will only host the UI**. The UI must connect to a backend hosted elsewhere (like AWS, DigitalOcean, or a VPS).

### Steps:
1.  **Push to GitHub** (see step 1).
2.  Go to [Vercel Dashboard](https://vercel.com/dashboard) and click **"Add New..."** -> **"Project"**.
3.  Import your GitHub Repository.
4.  **Configure Project**:
    *   **Framework Preset**: Vite
    *   **Root Directory**: `frontend` (Important! Click "Edit" and select the `frontend` folder).
    *   **Environment Variables**:
        *   `VITE_API_URL`: The URL of your live backend (e.g., `https://api.your-product.com`).
5.  Click **Deploy**.

*Note: We added a `vercel.json` file to the frontend folder to handle page routing automatically.*

---

## 3. Delivering to Clients (Self-Hosted Product)

If you want to sell this software to clients for them to run on their own servers (On-Premise), the **Docker** approach is the best "Product" format.

### What to deliver:
You don't need to give them the source code if you don't want to. You can provide:
1.  The `docker-compose.prod.yml` file.
2.  An `.env.example` file.
3.  A setup script or instruction manual.

### The "Boxed Product" Strategy:
Instead of sending code, you can publish your Docker images to a private registry (like Docker Hub) and give clients a simple `docker-compose.yml` that pulls those images.

**Simple Delivery (Source Code method):**
1.  Zip the following files/folders:
    *   `backend/`
    *   `frontend/`
    *   `docker-compose.prod.yml` (Rename to `docker-compose.yml` for them)
    *   `.env.example`
    *   `README.md`
2.  **Client Instructions**:
    > "Unzip the folder. Fill in the .env file. Run `docker-compose up -d`. Open localhost."

---

## 4. Full Cloud Deployment (SaaS)

If you want to host it yourself and charge users access (SaaS), you need a provider that supports Docker or Python.

*   **Frontend**: Vercel or Netlify.
*   **Backend**:
    *   **Render / Railway**: Easiest for Python/FastAPI. Connects to GitHub and deploys automatically.
    *   **DigitalOcean / AWS EC2**: Cheaper, total control. Use the `docker-compose.prod.yml` on a Linux server.

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed technical configuration for these platforms.
