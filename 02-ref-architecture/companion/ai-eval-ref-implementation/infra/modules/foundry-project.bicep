// Microsoft Foundry Hub and Project
//
// Creates an Azure AI Services account (which serves as the Foundry hub)
// and a Foundry project for organizing evaluation runs.

@description('Base name for resources.')
param baseName string

@description('Azure region.')
param location string

@description('SKU for the AI Services account.')
param aiServicesSku string

// Azure AI Services account (Foundry hub)
resource aiServices 'Microsoft.CognitiveServices/accounts@2024-10-01' = {
  name: '${baseName}-ai'
  location: location
  kind: 'AIServices'
  sku: {
    name: aiServicesSku
  }
  properties: {
    customSubDomainName: '${baseName}-ai'
    publicNetworkAccess: 'Enabled'
  }
}

// Foundry project
resource foundryProject 'Microsoft.CognitiveServices/accounts/projects@2024-10-01' = {
  parent: aiServices
  name: '${baseName}-eval-project'
  location: location
  properties: {}
}

output aiServicesAccountName string = aiServices.name
output aiServicesEndpoint string = 'https://${aiServices.properties.endpoint}'
output projectName string = foundryProject.name
