// Model Deployment Module
//
// Deploys a model (GPT-4o or similar) to the Azure AI Services account.
// Used for both the agent model and the evaluation judge model.

@description('Name of the AI Services account to deploy the model to.')
param aiServicesAccountName string

@description('Name for the model deployment.')
param deploymentName string

@description('Model name (e.g., gpt-4o).')
param modelName string

@description('Model version.')
param modelVersion string

@description('Capacity in thousands of tokens per minute (TPM).')
param capacity int

resource aiServices 'Microsoft.CognitiveServices/accounts@2024-10-01' existing = {
  name: aiServicesAccountName
}

resource modelDeployment 'Microsoft.CognitiveServices/accounts/deployments@2025-06-01' = {
  parent: aiServices
  name: deploymentName
  sku: {
    name: 'GlobalStandard'
    capacity: capacity
  }
  properties: {
    model: {
      format: 'OpenAI'
      name: modelName
      version: modelVersion
    }
  }
}

output deploymentName string = modelDeployment.name
