// Microsoft Foundry Hub and Project
//
// Creates an Azure AI Services account (which serves as the Foundry hub)
// and a Foundry project for organizing evaluation runs.

@description('Base name for resources.')
param baseName string

@description('Unique suffix for globally unique resource names.')
param uniqueSuffix string

@description('Azure region.')
param location string

@description('SKU for the AI Services account.')
param aiServicesSku string

// Azure AI Services account (Foundry hub)
resource aiServices 'Microsoft.CognitiveServices/accounts@2025-06-01' = {
  name: '${baseName}-${uniqueSuffix}-ai'
  location: location
  identity: {
    type: 'SystemAssigned'
  }
  kind: 'AIServices'
  sku: {
    name: aiServicesSku
  }
  properties: {
    allowProjectManagement: true
    customSubDomainName: '${baseName}-${uniqueSuffix}-ai'
    publicNetworkAccess: 'Enabled'
  }
}

// Foundry project
resource foundryProject 'Microsoft.CognitiveServices/accounts/projects@2025-06-01' = {
  parent: aiServices
  name: '${baseName}-${uniqueSuffix}-eval-project'
  location: location
  identity: {
    type: 'SystemAssigned'
  }
  properties: {}
}

output aiServicesAccountName string = aiServices.name
output aiServicesEndpoint string = 'https://${aiServices.properties.endpoint}'
output projectName string = foundryProject.name
