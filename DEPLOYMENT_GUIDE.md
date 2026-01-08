# Azure Deployment Guide

This guide will help you deploy the AI Code Review application to Azure with automatic CI/CD.

## Prerequisites

1. **Azure Account** with active subscription
2. **Azure CLI** installed: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli
3. **Git** configured with GitHub
4. **OpenAI API Key** for AI analysis

## Deployment Steps

### Option 1: Automated Deployment (Recommended)

#### Step 1: Login to Azure

```bash
az login
```

#### Step 2: Run Deployment Script

**On Linux/Mac:**
```bash
chmod +x azure-deploy.sh
./azure-deploy.sh
```

**On Windows (PowerShell):**
```powershell
bash azure-deploy.sh
```

The script will:
- Create all Azure resources (Container Apps, Database, Redis, etc.)
- Build and push Docker images
- Deploy the application
- Initialize the database

#### Step 3: Set OpenAI API Key

After deployment completes, set your OpenAI API key:

```bash
az containerapp secret set \
  --name codereview-backend \
  --resource-group codereview-rg \
  --secrets openai-api-key=YOUR_OPENAI_API_KEY
```

Then restart the backend:

```bash
az containerapp revision restart \
  --name codereview-backend \
  --resource-group codereview-rg
```

### Option 2: Setup CI/CD with GitHub Actions

#### Step 1: Get Azure Credentials

```bash
az ad sp create-for-rbac \
  --name "codereview-github-actions" \
  --role contributor \
  --scopes /subscriptions/YOUR_SUBSCRIPTION_ID/resourceGroups/codereview-rg \
  --sdk-auth
```

Save the JSON output - you'll need it for GitHub secrets.

#### Step 2: Get Container Registry Credentials

```bash
# Get username
az acr credential show --name codereviewacr --query username -o tsv

# Get password
az acr credential show --name codereviewacr --query "passwords[0].value" -o tsv
```

#### Step 3: Configure GitHub Secrets

Go to your GitHub repository → Settings → Secrets and variables → Actions

Add these secrets:

| Secret Name | Value |
|------------|-------|
| `AZURE_CREDENTIALS` | The JSON from Step 1 |
| `AZURE_CONTAINER_REGISTRY` | `codereviewacr` |
| `ACR_USERNAME` | Username from Step 2 |
| `ACR_PASSWORD` | Password from Step 2 |
| `AZURE_RESOURCE_GROUP` | `codereview-rg` |
| `BACKEND_URL` | Your backend URL from deployment |

#### Step 4: Push to GitHub

```bash
git add .
git commit -m "Add Azure deployment configuration"
git push origin main
```

The GitHub Action will automatically deploy! 🚀

## Verify Deployment

### Check Application Status

```bash
# Check all container apps
az containerapp list --resource-group codereview-rg --output table

# View backend logs
az containerapp logs show \
  --name codereview-backend \
  --resource-group codereview-rg \
  --follow

# View frontend logs
az containerapp logs show \
  --name codereview-frontend \
  --resource-group codereview-rg \
  --follow
```

### Test the Application

1. Open the frontend URL in your browser
2. Check the backend health endpoint: `https://YOUR-BACKEND-URL/api/health`
3. View API docs: `https://YOUR-BACKEND-URL/docs`

## Configure GitHub App

Now that you have live URLs, configure your GitHub App:

1. Go to GitHub → Settings → Developer settings → GitHub Apps
2. Create a new GitHub App with these settings:

**GitHub App Settings:**
- **Homepage URL**: Your frontend URL
- **Callback URL**: `https://YOUR-BACKEND-URL/api/webhooks/github/callback`
- **Webhook URL**: `https://YOUR-BACKEND-URL/api/webhooks/github`
- **Webhook secret**: Generate a random secret

**Permissions:**
- Repository permissions:
  - Pull requests: Read & write
  - Contents: Read-only
  - Metadata: Read-only

**Subscribe to events:**
- Pull request
- Pull request review

3. Generate a private key and download it
4. Update your backend secrets:

```bash
# Set GitHub App ID
az containerapp secret set \
  --name codereview-backend \
  --resource-group codereview-rg \
  --secrets github-app-id=YOUR_APP_ID

# Set webhook secret
az containerapp secret set \
  --name codereview-backend \
  --resource-group codereview-rg \
  --secrets github-webhook-secret=YOUR_WEBHOOK_SECRET
```

5. Upload the private key to Azure Key Vault or mount it as a secret

## Update Environment Variables

To update any environment variable:

```bash
az containerapp update \
  --name codereview-backend \
  --resource-group codereview-rg \
  --set-env-vars "NEW_VAR=value"
```

## Scaling

### Manual Scaling

```bash
az containerapp update \
  --name codereview-backend \
  --resource-group codereview-rg \
  --min-replicas 2 \
  --max-replicas 5
```

### Auto-scaling Rules

Container Apps automatically scale based on HTTP traffic and CPU usage.

## Monitoring

View metrics in Azure Portal:
1. Go to your Container App
2. Click "Metrics" in the left menu
3. Add metrics for CPU, Memory, HTTP requests, etc.

## Troubleshooting

### View Logs

```bash
# Live logs
az containerapp logs show \
  --name codereview-backend \
  --resource-group codereview-rg \
  --follow

# Recent logs
az containerapp logs show \
  --name codereview-backend \
  --resource-group codereview-rg \
  --tail 100
```

### Restart Container

```bash
az containerapp revision restart \
  --name codereview-backend \
  --resource-group codereview-rg
```

### Check Database Connection

```bash
az postgres flexible-server show \
  --resource-group codereview-rg \
  --name codereview-db
```

## Cost Management

Estimated monthly costs (basic tier):
- Container Apps: ~$30-50
- PostgreSQL: ~$15-30
- Redis: ~$15-20
- Container Registry: ~$5
- **Total: ~$65-105/month**

To reduce costs:
- Use burstable database tier
- Set minimum replicas to 0 for non-production
- Use Basic tier for Redis

## Cleanup

To delete all resources:

```bash
az group delete --name codereview-rg --yes --no-wait
```

## Support

For issues:
1. Check the logs first
2. Verify all secrets are set correctly
3. Check Azure Portal for resource status
4. Review GitHub Actions workflow logs
