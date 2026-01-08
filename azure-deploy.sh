#!/bin/bash
# Azure Deployment Script
# This script creates all necessary Azure resources and deploys the application

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
RESOURCE_GROUP="codereview-rg"
LOCATION="eastus"
ACR_NAME="codereviewacr"
CONTAINER_ENV="codereview-env"
POSTGRES_SERVER="codereview-db"
REDIS_NAME="codereview-redis"
LOG_ANALYTICS="codereview-logs"

echo -e "${GREEN}=== AI Code Review Azure Deployment ===${NC}\n"

# Check if user is logged in to Azure
echo -e "${YELLOW}Checking Azure login...${NC}"
az account show > /dev/null 2>&1 || {
    echo -e "${RED}Not logged in to Azure. Please run: az login${NC}"
    exit 1
}

echo -e "${GREEN}✓ Logged in to Azure${NC}\n"

# Create Resource Group
echo -e "${YELLOW}Creating resource group...${NC}"
az group create \
  --name $RESOURCE_GROUP \
  --location $LOCATION \
  --output table

# Create Container Registry
echo -e "\n${YELLOW}Creating Azure Container Registry...${NC}"
az acr create \
  --resource-group $RESOURCE_GROUP \
  --name $ACR_NAME \
  --sku Basic \
  --admin-enabled true \
  --output table

# Get ACR credentials
ACR_USERNAME=$(az acr credential show --name $ACR_NAME --query username -o tsv)
ACR_PASSWORD=$(az acr credential show --name $ACR_NAME --query "passwords[0].value" -o tsv)
ACR_LOGIN_SERVER=$(az acr show --name $ACR_NAME --query loginServer -o tsv)

echo -e "${GREEN}✓ Container Registry created: $ACR_LOGIN_SERVER${NC}"

# Create Log Analytics Workspace
echo -e "\n${YELLOW}Creating Log Analytics workspace...${NC}"
az monitor log-analytics workspace create \
  --resource-group $RESOURCE_GROUP \
  --workspace-name $LOG_ANALYTICS \
  --location $LOCATION \
  --output table

LOG_ANALYTICS_ID=$(az monitor log-analytics workspace show \
  --resource-group $RESOURCE_GROUP \
  --workspace-name $LOG_ANALYTICS \
  --query customerId -o tsv)

LOG_ANALYTICS_KEY=$(az monitor log-analytics workspace get-shared-keys \
  --resource-group $RESOURCE_GROUP \
  --workspace-name $LOG_ANALYTICS \
  --query primarySharedKey -o tsv)

echo -e "${GREEN}✓ Log Analytics workspace created${NC}"

# Create Azure Database for PostgreSQL
echo -e "\n${YELLOW}Creating PostgreSQL database (this may take a few minutes)...${NC}"
az postgres flexible-server create \
  --resource-group $RESOURCE_GROUP \
  --name $POSTGRES_SERVER \
  --location $LOCATION \
  --admin-user dbadmin \
  --admin-password "ChangeThisPassword123!" \
  --sku-name Standard_B1ms \
  --tier Burstable \
  --storage-size 32 \
  --version 15 \
  --public-access 0.0.0.0-255.255.255.255 \
  --output table

# Create database
az postgres flexible-server db create \
  --resource-group $RESOURCE_GROUP \
  --server-name $POSTGRES_SERVER \
  --database-name codereview_db \
  --output table

POSTGRES_CONNECTION="postgresql://dbadmin:ChangeThisPassword123!@${POSTGRES_SERVER}.postgres.database.azure.com:5432/codereview_db?sslmode=require"

echo -e "${GREEN}✓ PostgreSQL database created${NC}"

# Create Azure Cache for Redis
echo -e "\n${YELLOW}Creating Redis cache (this may take several minutes)...${NC}"
az redis create \
  --resource-group $RESOURCE_GROUP \
  --name $REDIS_NAME \
  --location $LOCATION \
  --sku Basic \
  --vm-size c0 \
  --output table

REDIS_KEY=$(az redis list-keys \
  --resource-group $RESOURCE_GROUP \
  --name $REDIS_NAME \
  --query primaryKey -o tsv)

REDIS_HOST="${REDIS_NAME}.redis.cache.windows.net"
REDIS_CONNECTION="rediss://:${REDIS_KEY}@${REDIS_HOST}:6380/0?ssl_cert_reqs=required"

echo -e "${GREEN}✓ Redis cache created${NC}"

# Create Container Apps Environment
echo -e "\n${YELLOW}Creating Container Apps environment...${NC}"
az containerapp env create \
  --name $CONTAINER_ENV \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --logs-workspace-id $LOG_ANALYTICS_ID \
  --logs-workspace-key $LOG_ANALYTICS_KEY \
  --output table

echo -e "${GREEN}✓ Container Apps environment created${NC}"

# Build and push images to ACR
echo -e "\n${YELLOW}Building and pushing Docker images...${NC}"
az acr build \
  --registry $ACR_NAME \
  --image codereview-backend:latest \
  --file ./backend/Dockerfile \
  ./backend

az acr build \
  --registry $ACR_NAME \
  --image codereview-frontend:latest \
  --file ./frontend/Dockerfile \
  ./frontend

echo -e "${GREEN}✓ Images built and pushed${NC}"

# Deploy Backend Container App
echo -e "\n${YELLOW}Deploying backend container...${NC}"
az containerapp create \
  --name codereview-backend \
  --resource-group $RESOURCE_GROUP \
  --environment $CONTAINER_ENV \
  --image ${ACR_LOGIN_SERVER}/codereview-backend:latest \
  --registry-server $ACR_LOGIN_SERVER \
  --registry-username $ACR_USERNAME \
  --registry-password $ACR_PASSWORD \
  --target-port 8000 \
  --ingress external \
  --min-replicas 1 \
  --max-replicas 3 \
  --cpu 0.5 \
  --memory 1.0Gi \
  --env-vars \
    "DATABASE_URL=$POSTGRES_CONNECTION" \
    "REDIS_URL=$REDIS_CONNECTION" \
    "ENVIRONMENT=production" \
    "OPENAI_API_KEY=secretref:openai-api-key" \
  --output table

BACKEND_URL=$(az containerapp show \
  --name codereview-backend \
  --resource-group $RESOURCE_GROUP \
  --query properties.configuration.ingress.fqdn -o tsv)

echo -e "${GREEN}✓ Backend deployed at: https://${BACKEND_URL}${NC}"

# Deploy Frontend Container App
echo -e "\n${YELLOW}Deploying frontend container...${NC}"
az containerapp create \
  --name codereview-frontend \
  --resource-group $RESOURCE_GROUP \
  --environment $CONTAINER_ENV \
  --image ${ACR_LOGIN_SERVER}/codereview-frontend:latest \
  --registry-server $ACR_LOGIN_SERVER \
  --registry-username $ACR_USERNAME \
  --registry-password $ACR_PASSWORD \
  --target-port 5173 \
  --ingress external \
  --min-replicas 1 \
  --max-replicas 3 \
  --cpu 0.25 \
  --memory 0.5Gi \
  --env-vars \
    "VITE_API_URL=https://${BACKEND_URL}" \
  --output table

FRONTEND_URL=$(az containerapp show \
  --name codereview-frontend \
  --resource-group $RESOURCE_GROUP \
  --query properties.configuration.ingress.fqdn -o tsv)

echo -e "${GREEN}✓ Frontend deployed at: https://${FRONTEND_URL}${NC}"

# Deploy Celery Worker Container App
echo -e "\n${YELLOW}Deploying Celery worker...${NC}"
az containerapp create \
  --name codereview-celery \
  --resource-group $RESOURCE_GROUP \
  --environment $CONTAINER_ENV \
  --image ${ACR_LOGIN_SERVER}/codereview-backend:latest \
  --registry-server $ACR_LOGIN_SERVER \
  --registry-username $ACR_USERNAME \
  --registry-password $ACR_PASSWORD \
  --command "celery" "-A" "app.tasks.celery_app" "worker" "--loglevel=info" \
  --min-replicas 1 \
  --max-replicas 2 \
  --cpu 0.5 \
  --memory 1.0Gi \
  --env-vars \
    "DATABASE_URL=$POSTGRES_CONNECTION" \
    "REDIS_URL=$REDIS_CONNECTION" \
    "ENVIRONMENT=production" \
    "OPENAI_API_KEY=secretref:openai-api-key" \
  --output table

echo -e "${GREEN}✓ Celery worker deployed${NC}"

# Initialize database
echo -e "\n${YELLOW}Initializing database...${NC}"
az containerapp exec \
  --name codereview-backend \
  --resource-group $RESOURCE_GROUP \
  --command "python init_db.py"

echo -e "${GREEN}✓ Database initialized${NC}"

# Summary
echo -e "\n${GREEN}=== Deployment Complete! ===${NC}\n"
echo -e "Frontend URL: ${GREEN}https://${FRONTEND_URL}${NC}"
echo -e "Backend URL: ${GREEN}https://${BACKEND_URL}${NC}"
echo -e "API Docs: ${GREEN}https://${BACKEND_URL}/docs${NC}\n"

echo -e "${YELLOW}Next steps:${NC}"
echo -e "1. Set the OPENAI_API_KEY secret:"
echo -e "   az containerapp secret set --name codereview-backend --resource-group $RESOURCE_GROUP --secrets openai-api-key=YOUR_KEY"
echo -e "\n2. Update .env file with:"
echo -e "   DATABASE_URL=$POSTGRES_CONNECTION"
echo -e "   REDIS_URL=$REDIS_CONNECTION"
echo -e "\n3. Set up GitHub Actions secrets:"
echo -e "   AZURE_CONTAINER_REGISTRY=$ACR_NAME"
echo -e "   ACR_USERNAME=$ACR_USERNAME"
echo -e "   ACR_PASSWORD=$ACR_PASSWORD"
echo -e "   AZURE_RESOURCE_GROUP=$RESOURCE_GROUP"
echo -e "   BACKEND_URL=https://${BACKEND_URL}"
