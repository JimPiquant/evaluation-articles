// AI Evaluation Pipeline — Main Bicep Orchestrator
//
// Deploys the infrastructure for the AI evaluation reference implementation:
// - Microsoft Foundry hub and project
// - Model deployments (agent model + judge model)
// - Log Analytics workspace for monitoring
//
// Usage:
//   az deployment group create \
//     --resource-group <rg-name> \
//     --template-file infra/main.bicep \
//     --parameters infra/parameters/dev.bicepparam

targetScope = 'resourceGroup'

@description('Base name for all resources. Resources will be named using this prefix.')
param baseName string

@description('Azure region for resource deployment.')
param location string = resourceGroup().location

@description('SKU for the Azure AI Services account.')
@allowed(['S0'])
param aiServicesSku string = 'S0'

@description('Model name for the agent (e.g., gpt-4o).')
param agentModelName string = 'gpt-4o'

@description('Model version for the agent.')
param agentModelVersion string = '2024-11-20'

@description('Capacity (TPM in thousands) for the agent model deployment.')
param agentModelCapacity int = 30

@description('Model name for the evaluation judge (e.g., gpt-4o).')
param judgeModelName string = 'gpt-4o'

@description('Model version for the evaluation judge.')
param judgeModelVersion string = '2024-11-20'

@description('Capacity (TPM in thousands) for the judge model deployment.')
param judgeModelCapacity int = 30

@description('Log Analytics workspace retention in days.')
param logRetentionDays int = 30

// --- Modules ---

module foundryProject 'modules/foundry-project.bicep' = {
  name: 'foundry-project'
  params: {
    baseName: baseName
    location: location
    aiServicesSku: aiServicesSku
  }
}

module agentModelDeployment 'modules/model-deployment.bicep' = {
  name: 'agent-model-deployment'
  params: {
    aiServicesAccountName: foundryProject.outputs.aiServicesAccountName
    deploymentName: '${baseName}-agent'
    modelName: agentModelName
    modelVersion: agentModelVersion
    capacity: agentModelCapacity
  }
}

module judgeModelDeployment 'modules/model-deployment.bicep' = {
  name: 'judge-model-deployment'
  params: {
    aiServicesAccountName: foundryProject.outputs.aiServicesAccountName
    deploymentName: '${baseName}-judge'
    modelName: judgeModelName
    modelVersion: judgeModelVersion
    capacity: judgeModelCapacity
  }
}

module monitoring 'modules/monitoring.bicep' = {
  name: 'monitoring'
  params: {
    baseName: baseName
    location: location
    retentionDays: logRetentionDays
  }
}

// --- Outputs ---

output aiServicesEndpoint string = foundryProject.outputs.aiServicesEndpoint
output projectName string = foundryProject.outputs.projectName
output agentModelDeploymentName string = agentModelDeployment.outputs.deploymentName
output judgeModelDeploymentName string = judgeModelDeployment.outputs.deploymentName
output logAnalyticsWorkspaceId string = monitoring.outputs.workspaceId
