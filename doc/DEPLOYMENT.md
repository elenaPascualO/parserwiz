# Railway Deployment Guide

This guide covers deploying ParserWiz to Railway.

## Prerequisites

- GitHub repository with the code pushed
- Railway account ([railway.com](https://railway.com))

## Deployment Files

The following files are required for Railway deployment:

| File | Purpose |
|------|---------|
| `requirements.txt` | Python dependencies (Railway doesn't support `uv` natively) |
| `Procfile` | Start command for the web process |
| `railway.json` | Railway-specific configuration |

### requirements.txt

Generated from `pyproject.toml`:

```bash
uv pip compile pyproject.toml -o requirements.txt
```

**Important**: Regenerate this file whenever you add/update dependencies in `pyproject.toml`.

### Procfile

```
web: uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

Railway provides the `$PORT` environment variable automatically.

### railway.json

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "RAILPACK"
  },
  "deploy": {
    "startCommand": "uvicorn backend.main:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/api/health",
    "healthcheckTimeout": 30
  }
}
```

**Note**: We use `RAILPACK` (not `NIXPACKS`) as Nixpacks is deprecated.

## Deployment Steps

### 1. Commit deployment files

```bash
git add Procfile railway.json requirements.txt
git commit -m "chore: add Railway deployment configuration"
git push
```

### 2. Create Railway project

1. Go to [railway.com](https://railway.com) and sign in
2. Click **"New Project"**
3. Select **"Deploy from GitHub Repo"**
4. Authorize Railway to access your GitHub account
5. Select the `data_toolkit` repository
6. Railway will auto-detect Python and start building

### 3. Configure environment variables

Go to your service → **Variables** tab and add:

| Variable | Value | Required |
|----------|-------|----------|
| `ENVIRONMENT` | `production` | Yes |
| `ALLOWED_ORIGINS` | `https://www.parserwiz.app` | Yes |
| `DISCORD_WEBHOOK_URL` | Your Discord webhook URL | No |
| `MAX_FILE_SIZE_MB` | `10` (default) | No |
| `RAILPACK_PYTHON_VERSION` | `3.12` | Only if build fails |

**CORS Note**: For initial testing, you can use Railway's generated URL (e.g., `https://data-toolkit-production.up.railway.app`). Update this when you add a custom domain.

### 4. Generate public URL

1. Go to **Settings** → **Networking**
2. Click **"Generate Domain"**
3. Railway assigns a URL like `https://data-toolkit-production.up.railway.app`

### 5. Verify deployment

Test the health endpoint:

```bash
curl https://your-railway-url.up.railway.app/api/health
# Should return: {"status":"ok"}
```

## Custom Domain Setup

### Railway side

1. Go to **Settings** → **Networking** → **Custom Domain**
2. Enter your domain (e.g., `parserwiz.example.com`)
3. Railway provides a CNAME target

### DNS side

Add a CNAME record in your DNS provider:

| Type | Name | Value |
|------|------|-------|
| CNAME | `parserwiz` | `your-app.up.railway.app` |

### Update CORS

After adding your custom domain, update `ALLOWED_ORIGINS`:

```
ALLOWED_ORIGINS=https://parserwiz.example.com
```

For multiple origins (comma-separated):

```
ALLOWED_ORIGINS=https://parserwiz.example.com,https://www.parserwiz.example.com
```

**Hobby plan limit**: 2 custom domains per service.

## Cost Management

### Set usage limits

To avoid unexpected charges:

1. Go to **Workspace** → **Usage**
2. Set a usage limit (e.g., $5 or $10)
3. If exceeded, Railway stops your workloads instead of charging more

### Pricing overview

| Plan | Cost | Included Usage | Custom Domains |
|------|------|----------------|----------------|
| Trial | Free (30 days) | $5 credit | 1 |
| Hobby | $5/month | $5 | 2 per service |
| Pro | $20/month | $20 | 10 per service |

If usage exceeds included amount, you pay the difference.

## Troubleshooting

### Build fails with Python version error

Add environment variable:
```
RAILPACK_PYTHON_VERSION=3.12
```

### App crashes on startup

1. Check **Deployments** → **View Logs**
2. Common issues:
   - Missing environment variables
   - Port binding (ensure using `$PORT`)
   - Import errors (check `requirements.txt` is up to date)

### Health check fails

- Verify `/api/health` endpoint returns `{"status":"ok"}`
- Increase `healthcheckTimeout` in `railway.json` if app is slow to start

### CORS errors in browser

- Check `ALLOWED_ORIGINS` includes your frontend URL
- Include protocol (`https://`) in origins
- For multiple domains, use comma-separated values

## Updating the Deployment

When you push to the connected branch, Railway automatically rebuilds and deploys.

### Manual redeploy

1. Go to **Deployments**
2. Click **"Redeploy"** on any previous deployment

### Updating dependencies

```bash
# After modifying pyproject.toml
uv pip compile pyproject.toml -o requirements.txt
git add requirements.txt
git commit -m "chore: update dependencies"
git push
```

## Rollback

To rollback to a previous version:

1. Go to **Deployments**
2. Find the working deployment
3. Click **"Redeploy"**
