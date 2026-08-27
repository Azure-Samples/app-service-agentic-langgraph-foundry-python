extension microsoftGraphV1

@description('Environment name used to identify the application')
param envName string

@description('URL of the App Service application')
param webAppUrl string

@description('Principal ID of the managed identity used by App Service authentication')
param managedIdentityPrincipalId string

resource app 'Microsoft.Graph/applications@v1.0' = {
  uniqueName: 'task-manager-${envName}'
  displayName: 'Task Manager (${envName})'
  signInAudience: 'AzureADMyOrg'
  requiredResourceAccess: []
  api: {
    requestedAccessTokenVersion: 2
  }
  web: {
    homePageUrl: webAppUrl
    implicitGrantSettings: {
      enableAccessTokenIssuance: false
      enableIdTokenIssuance: true
    }
    redirectUris: [
      '${webAppUrl}/.auth/login/aad/callback'
    ]
  }

  resource managedIdentityCredential 'federatedIdentityCredentials@v1.0' = {
    name: '${app.uniqueName}/app-service-authentication'
    description: 'App Service authentication managed identity credential'
    audiences: [
      'api://AzureADTokenExchange'
    ]
    issuer: '${environment().authentication.loginEndpoint}${tenant().tenantId}/v2.0'
    subject: managedIdentityPrincipalId
  }
}

resource servicePrincipal 'Microsoft.Graph/servicePrincipals@v1.0' = {
  appId: app.appId
  tags: [
    'AppServiceIntegratedApp'
    'WindowsAzureActiveDirectoryIntegratedApp'
  ]
}

output clientId string = app.appId
output appObjectId string = app.id
output uniqueName string = app.uniqueName
