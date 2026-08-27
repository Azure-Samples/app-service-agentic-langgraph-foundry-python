extension microsoftGraphV1

@description('Unique name of the existing App Service authentication application')
param applicationUniqueName string

@description('Client ID of the existing App Service authentication application')
param applicationClientId string

resource app 'Microsoft.Graph/applications@v1.0' = {
  uniqueName: applicationUniqueName
  identifierUris: [
    'api://${applicationClientId}'
  ]
  api: {
    requestedAccessTokenVersion: 2
  }
}

output audience string = 'api://${applicationClientId}'
