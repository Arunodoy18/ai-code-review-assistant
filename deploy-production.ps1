#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Production deployment script for Azure Container Apps
    
.DESCRIPTION
    Handles Docker availability, ACR authentication, builds containers, and deploys to Azure.
    Robust error handling with fallbacks for Docker daemon issues.
    
.NOTES
    Author: Production Engineering Team
    Date: 2026-01-11
    Purpose: Zero-downtime deployment to existing Azure Container Apps
#>

param(
    [string]$ResourceGroup = "codereview-rg",
    [string]$RegistryName = "codereviewacr8765",
    [string]$FrontendApp = "codereview-frontend",
    [string]$BackendApp = "codereview-backend",
    [string]$Version = "v2.0",
    [switch]$SkipBuild = $false,
    [switch]$FrontendOnly = $false,
    [switch]$BackendOnly = $false
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

# Colors for output
function Write-Success { Write-Host "[SUCCESS] $args" -ForegroundColor Green }
function Write-Info { Write-Host "[INFO] $args" -ForegroundColor Cyan }
function Write-Warning { Write-Host "[WARNING] $args" -ForegroundColor Yellow }
function Write-Error { Write-Host "[ERROR] $args" -ForegroundColor Red }

Write-Info "🚀 Production Deployment Started"
Write-Info "Target: Azure Container Apps"
Write-Info "Version: $Version"

# Step 1: Check Docker availability
function Test-DockerAvailable {
    try {
        $null = docker version 2>&1
        if ($LASTEXITCODE -eq 0) {
            return $true
        }
        return $false
    } catch {
        return $false
    }
}

$dockerAvailable = Test-DockerAvailable

if ($dockerAvailable) {
    Write-Success "Docker is available"
} else {
    Write-Warning "Docker Desktop not running - will use Azure Container Registry build tasks"
}

# Step 2: Azure Authentication
Write-Info "Checking Azure authentication..."
try {
    $account = az account show 2>$null | ConvertFrom-Json
    Write-Success "Logged in as: $($account.user.name)"
} catch {
    Write-Error "Not logged into Azure. Run: az login"
    exit 1
}

# Step 3: ACR Authentication
$registryUrl = "$RegistryName.azurecr.io"

if ($dockerAvailable) {
    Write-Info "Authenticating with ACR using Docker..."
    try {
        az acr login --name $RegistryName | Out-Null
        Write-Success "ACR authentication successful"
    } catch {
        Write-Warning "Docker login failed, falling back to token-based auth"
        $dockerAvailable = $false
    }
}

if (-not $dockerAvailable) {
    Write-Info "Using token-based authentication..."
    $token = (az acr login --name $RegistryName --expose-token --output json | ConvertFrom-Json).accessToken
    Write-Success "Token obtained successfully"
}

# Step 4: Build and Push Frontend
if (-not $BackendOnly) {
    Write-Info ""
    Write-Info "═══════════════════════════════════════"
    Write-Info "FRONTEND DEPLOYMENT"
    Write-Info "═══════════════════════════════════════"
    
    $frontendImage = "$registryUrl/codereview-frontend:$Version"
    
    if (-not $SkipBuild) {
        Set-Location "$PSScriptRoot\frontend"
        
        if ($dockerAvailable) {
            Write-Info "Building frontend Docker image locally..."
            $buildTime = [int][double]::Parse((Get-Date -UFormat %s))
            
            docker build `
                --build-arg BUILD_TIME=$buildTime `
                --target prod `
                -t $frontendImage `
                -f Dockerfile `
                . 2>&1 | ForEach-Object { Write-Host $_ }
            
            if ($LASTEXITCODE -ne 0) {
                Write-Error "Frontend build failed"
                exit 1
            }
            
            Write-Success "Frontend build complete"
            
            Write-Info "Pushing frontend image to ACR..."
            docker push $frontendImage 2>&1 | ForEach-Object { Write-Host $_ }
            
            if ($LASTEXITCODE -ne 0) {
                Write-Error "Frontend push failed"
                exit 1
            }
        } else {
            Write-Info "Building frontend using Azure Container Registry build task..."
            $buildTime = [int][double]::Parse((Get-Date -UFormat %s))
            
            az acr build `
                --registry $RegistryName `
                --image "codereview-frontend:$Version" `
                --build-arg BUILD_TIME=$buildTime `
                --target prod `
                --file Dockerfile `
                . 2>&1 | ForEach-Object { Write-Host $_ }
            
            if ($LASTEXITCODE -ne 0) {
                Write-Error "Frontend ACR build failed"
                exit 1
            }
        }
        
        Write-Success "Frontend image ready: $frontendImage"
    } else {
        Write-Info "Skipping build, using existing image: $frontendImage"
    }
    
    # Deploy frontend
    Write-Info "Deploying frontend to Azure Container Apps..."
    az containerapp update `
        --name $FrontendApp `
        --resource-group $ResourceGroup `
        --image $frontendImage `
        --output table
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Frontend deployment failed"
        exit 1
    }
    
    Write-Success "Frontend deployed successfully!"
}

# Step 5: Build and Push Backend
if (-not $FrontendOnly) {
    Write-Info ""
    Write-Info "═══════════════════════════════════════"
    Write-Info "BACKEND DEPLOYMENT"
    Write-Info "═══════════════════════════════════════"
    
    $backendImage = "$registryUrl/codereview-backend:$Version"
    
    if (-not $SkipBuild) {
        Set-Location "$PSScriptRoot\backend"
        
        if ($dockerAvailable) {
            Write-Info "Building backend Docker image locally..."
            
            docker build `
                -t $backendImage `
                -f Dockerfile `
                . 2>&1 | ForEach-Object { Write-Host $_ }
            
            if ($LASTEXITCODE -ne 0) {
                Write-Error "Backend build failed"
                exit 1
            }
            
            Write-Success "Backend build complete"
            
            Write-Info "Pushing backend image to ACR..."
            docker push $backendImage 2>&1 | ForEach-Object { Write-Host $_ }
            
            if ($LASTEXITCODE -ne 0) {
                Write-Error "Backend push failed"
                exit 1
            }
        } else {
            Write-Info "Building backend using Azure Container Registry build task..."
            
            az acr build `
                --registry $RegistryName `
                --image "codereview-backend:$Version" `
                --file Dockerfile `
                . 2>&1 | ForEach-Object { Write-Host $_ }
            
            if ($LASTEXITCODE -ne 0) {
                Write-Error "Backend ACR build failed"
                exit 1
            }
        }
        
        Write-Success "Backend image ready: $backendImage"
    } else {
        Write-Info "Skipping build, using existing image: $backendImage"
    }
    
    # Deploy backend
    Write-Info "Deploying backend to Azure Container Apps..."
    az containerapp update `
        --name $BackendApp `
        --resource-group $ResourceGroup `
        --image $backendImage `
        --output table
    
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Backend deployment failed"
        exit 1
    }
    
    Write-Success "Backend deployed successfully!"
}

# Step 6: Verify Deployment
Write-Info ""
Write-Info "═══════════════════════════════════════"
Write-Info "VERIFICATION"
Write-Info "═══════════════════════════════════════"

Start-Sleep -Seconds 10

if (-not $BackendOnly) {
    $frontendUrl = (az containerapp show --name $FrontendApp --resource-group $ResourceGroup --query "properties.configuration.ingress.fqdn" -o tsv)
    Write-Info "Frontend URL: https://$frontendUrl"
}

if (-not $FrontendOnly) {
    $backendUrl = (az containerapp show --name $BackendApp --resource-group $ResourceGroup --query "properties.configuration.ingress.fqdn" -o tsv)
    Write-Info "Backend URL: https://$backendUrl"
    
    Write-Info "Testing backend health..."
    try {
        $health = Invoke-RestMethod -Uri "https://$backendUrl/api/health" -Method Get -TimeoutSec 10
        Write-Success "Backend health check passed: $($health.status)"
    } catch {
        Write-Warning "Backend health check failed (may still be starting): $_"
    }
}

Write-Info ""
Write-Success "======================================="
Write-Success "DEPLOYMENT COMPLETE!"
Write-Success "======================================="

if (-not $BackendOnly) {
    Write-Info ""
    Write-Info "Open your app: https://$frontendUrl"
    Write-Info "Check browser console for:"
    Write-Info "  [Config] Environment: production"
    Write-Info "  [Config] API URL: https://$backendUrl"
}

Write-Info ""
Write-Info "Monitor logs:"
if (-not $BackendOnly) {
    Write-Info "  az containerapp logs show --name $FrontendApp --resource-group $ResourceGroup --follow"
}
if (-not $FrontendOnly) {
    Write-Info "  az containerapp logs show --name $BackendApp --resource-group $ResourceGroup --follow"
}
