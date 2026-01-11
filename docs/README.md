# Deployment Documentation

This folder contains deployment-related documentation and scripts for production environments.

## Contents

- **PRODUCTION_DEPLOYMENT_GUIDE.md** - Complete guide for deploying to Azure Container Apps
- **PRODUCTION_READY_SUMMARY.md** - Production readiness checklist and summary
- **DEPLOYMENT_GUIDE.md** - General deployment information
- **DEPLOYMENT_FIXED.md** - Deployment fixes and troubleshooting
- **CACHE_FIX_GUIDE.md** - Cache-related fixes for production
- **azure-deploy.sh** - Azure deployment script (Bash)
- **deploy-production.ps1** - Azure deployment script (PowerShell)

## Important Note

**The main project is configured for local development only by default.**

These deployment resources are preserved for future use when you're ready to deploy to production environments. The main codebase has been simplified to focus on local development with no deployment dependencies.

## Re-enabling Deployment

To re-enable production deployment later:

1. Review the guides in this folder
2. Re-add production URL configuration to frontend config files
3. Add back runtime environment detection if needed
4. Configure Azure resources following the production guide
5. Run the deployment scripts

The Docker files and docker-compose.yml are already configured and can be used when needed.
