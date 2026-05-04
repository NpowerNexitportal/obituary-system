# Automated Obituary Content System

A full-stack system designed to fetch, rewrite, store, and automatically publish SEO-optimized obituary content.

## Architecture
1. **Scraper (Python)**: Fetches trending keywords, scrapes content, rewrites it for SEO, and stores it in MongoDB.
2. **API (FastAPI)**: Serves the stored content via lightweight REST endpoints.
3. **WordPress Plugin (PHP)**: Automatically fetches from the API and publishes to WordPress.
4. **Automation (GitHub Actions)**: Runs the scraper every 15 minutes.

## Deployment Guide

### 1. Setting up MongoDB Atlas (Free Tier)
1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas/register) and create a free account.
2. Build a new Shared (Free) Cluster.
3. Under "Database Access", create a user and password.
4. Under "Network Access", allow access from anywhere (`0.0.0.0/0`) since GitHub Actions IPs change.
5. Get your connection string (URI) and replace `<password>` with your DB user's password.

### 2. Deploying FastAPI Server (Free Hosting)
You can deploy the API for free on [Render](https://render.com) or [Railway](https://railway.app).
**Render Deployment:**
1. Connect your GitHub repository to Render.
2. Create a new "Web Service".
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `cd api && uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add Environment Variables: `MONGODB_URI` and `DATABASE_NAME`.
6. Once deployed, note the API URL (e.g., `https://your-api.onrender.com`).

### 3. Setting up GitHub Actions
1. Go to your GitHub repository Settings -> Secrets and variables -> Actions.
2. Add New Repository Secrets:
   - `MONGODB_URI`: Your MongoDB connection string.
   - `DATABASE_NAME`: `obituary_db` (or your chosen name).
   - `OPENAI_API_KEY`: (Optional) If you modify `rewriter.py` to use OpenAI.
3. The scraper will now automatically run every 15 minutes via the `.github/workflows/cron.yml` workflow.

### 4. Installing the WordPress Plugin
1. Zip the `wordpress-plugin` folder into `obituary-auto-poster.zip`.
2. In your WordPress Admin dashboard, go to Plugins -> Add New -> Upload Plugin.
3. Upload the ZIP file and activate the plugin.
4. Go to Settings -> Obituary Poster.
5. Enter your deployed API URL (e.g., `https://your-api.onrender.com/api/obituaries`).
6. Save settings. The plugin will now fetch and publish hourly, or you can click "Fetch Now" to manually trigger it.

## Local Development
1. Clone the repo.
2. Copy `.env.example` to `.env` and fill in values.
3. Install dependencies: `pip install -r requirements.txt`
4. Run Scraper: `cd scraper && python scraper.py`
5. Run API: `cd api && uvicorn main:app --reload`
