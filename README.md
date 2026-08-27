# Agentic Azure App Service app with LangGraph and Foundry Agent Service

This repository demonstrates how to build a modern FastAPI web application that integrates with both Foundry Agent Service and LangGraph agents. It provides a simple CRUD task list and two interactive chat agents.

## Getting Started

See [Tutorial: Build an agentic web app in Azure App Service with LangGraph or Azure AI Foundry Agent Service (Python)](https://learn.microsoft.com/azure/app-service/tutorial-ai-agent-web-app-langgraph-foundry-python).

## Features

- **Task List**: Simple CRUD web app application.
- **LangGraph Agent**: Chat with an agent powered by LangGraph.
- **Foundry Agent Service**: Chat with an agent powered by Foundry Agent Service.
- **OpenAPI Schema**: Enables integration with Foundry Agent Service.
- **App Service authentication**: Requires Microsoft Entra sign-in for the deployed UI and all API endpoints, including the OpenAPI schema.

## Security and deployment

The Bicep template enables App Service authentication (`authsettingsV2`) with Microsoft Entra ID. The Microsoft Graph Bicep extension creates the tenant-local application, service principal, and federated identity credential. App Service authentication uses a dedicated user-assigned managed identity as its confidential-client assertion, so the setup is declarative and does not use client secrets.

The sample intentionally keeps one authenticated LangGraph thread and one Foundry conversation on the server. Conversation state is in memory, so the deployment runs one Gunicorn worker. Increasing the worker count or scaling out the web app creates separate state per worker unless an external conversation store is added.

When you deploy with `azd up`, copy the printed **Foundry OpenAPI managed identity audience** and configure the Foundry OpenAPI tool to use **Managed identity**, not anonymous authentication. Use the printed `api://<generated-client-id>` value as the audience.

Before testing the OpenAPI tool, allow the parent Foundry resource's system-assigned managed identity to call the protected API:

```bash
azd env set AZURE_AI_FOUNDRY_ACCOUNT_CLIENT_ID <parent-resource-application-id>
azd provision
```

Use the parent Foundry resource identity application ID, not the Foundry project identity. The project endpoint and agent/model settings (`AZURE_AI_FOUNDRY_PROJECT_ENDPOINT`, `AZURE_AI_FOUNDRY_AGENT_NAME`, and the Azure OpenAI settings) remain Python application configuration. `AZURE_AI_FOUNDRY_ACCOUNT_CLIENT_ID` is AZD infrastructure configuration and should not be added to the application's `.env` file.

Run `azd down --purge` to remove the Azure resources. The cross-platform `postdown` hook also deletes the tenant-level Entra application created for App Service authentication.

## Project Structure

```
.devcontainer/
└── devcontainer.json            # Dev container configuration for VS Code
azure.yaml                        # Azure Developer CLI config
infra/
├── bicepconfig.json             # Microsoft Graph Bicep extension
├── entra-app.bicep              # Entra application, service principal, and FIC
├── entra-app-api.bicep          # Application ID URI configuration
├── main.bicep                   # Azure resources and App Service authentication
├── main.parameters.json         # Parameters for Bicep deployment
public/
└── index.html                   # React frontend
src/
├── __init__.py
├── app.py                       # Main FastAPI application
├── agents/                      # AI agent implementations
│   ├── __init__.py
│   ├── foundry_task_agent.py    # Foundry agent
│   └── langgraph_task_agent.py  # LangGraph agent
├── models/                      # Pydantic models for data validation
│   └── __init__.py
├── routes/                      # API route definitions
│   ├── __init__.py
│   └── api.py                   # Task and chat endpoints
└── services/                    # Business logic services
    ├── __init__.py
    └── task_service.py          # Task CRUD operations with SQLite
tasks.db                         # SQLite database file
requirements.txt                 # Python dependencies
README.md                        # Project documentation
```