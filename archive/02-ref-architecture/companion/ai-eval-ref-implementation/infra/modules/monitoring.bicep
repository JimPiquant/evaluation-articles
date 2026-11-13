// Monitoring Module
//
// Creates a Log Analytics workspace for evaluation monitoring
// and quality drift alerting.

@description('Base name for resources.')
param baseName string

@description('Azure region.')
param location string

@description('Retention period in days.')
param retentionDays int

resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: '${baseName}-logs'
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: retentionDays
  }
}

output workspaceId string = logAnalytics.id
output workspaceName string = logAnalytics.name
