import asyncio
import os
from typing import Optional
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from ..services import TaskService
from ..models import ChatMessage, Role


class FoundryTaskAgent:
    """
    Agent that interfaces with Foundry Agent Service to process user messages.
    
    This agent:
    - Initializes connection to Foundry Agent Service using environment variables
    - Retrieves an existing agent by name from Foundry
    - Manages agent session and conversation
    - Sends user messages to agent and retrieves responses
    - Handles errors and configuration issues gracefully
    
    Environment variables required:
    - AZURE_AI_FOUNDRY_PROJECT_ENDPOINT: The endpoint URL for the Foundry project
    - AZURE_AI_FOUNDRY_AGENT_NAME: The name of the agent to retrieve
    """
    
    def __init__(self, task_service: TaskService):
        self.task_service = task_service
        self.project_client = None
        self.openai_client = None
        self.agent = None
        self.conversation_id = None
        
        # Initialize the agent
        endpoint = os.getenv("AZURE_AI_FOUNDRY_PROJECT_ENDPOINT")
        agent_name = os.getenv("AZURE_AI_FOUNDRY_AGENT_NAME")
        
        if not endpoint or not agent_name:
            print("Foundry Agent Service configuration missing. Set AZURE_AI_FOUNDRY_PROJECT_ENDPOINT and AZURE_AI_FOUNDRY_AGENT_NAME")
            return
        
        try:
            # Create the project client using Azure credentials
            self.project_client = AIProjectClient(
                endpoint=endpoint,
                credential=DefaultAzureCredential()
            )
            
            # Get the OpenAI client for conversation operations
            self.openai_client = self.project_client.get_openai_client()
            
            # Find the existing agent by name
            self.agent = self.project_client.agents.get(agent_name)
            
            if not self.agent:
                print(f"Agent with name '{agent_name}' not found in project.")
                return
                        
            # App Service authentication protects this sample, which intentionally
            # keeps one server-managed conversation per worker process.
            conversation = self.openai_client.conversations.create()
            self.conversation_id = conversation.id
            print("Foundry agent initialized successfully")
            
        except ImportError as e:
            print(f"Azure AI Projects SDK not available. Install azure-ai-projects package: {e}")
        except Exception as e:
            print(f"Failed to initialize Foundry agent: {e}")
    
    async def process_message(self, message: str) -> ChatMessage:
        """
        Process a user message and return the assistant's response.
        
        Args:
            message: The user's message
            
        Returns:
            ChatMessage object containing the assistant's response
        """
        if not self.project_client or not self.agent or not self.conversation_id or not self.openai_client:
            return ChatMessage(
                role=Role.ASSISTANT,
                content="Foundry Agent Service is not properly configured. Please check your settings."
            )
        
        try:
            # Add user message to the conversation
            await asyncio.to_thread(
                self.openai_client.conversations.items.create,
                conversation_id=self.conversation_id,
                items=[{"type": "message", "role": "user", "content": message}],
            )
            
            # Create response using the agent
            response = await asyncio.to_thread(
                self.openai_client.responses.create,
                conversation=self.conversation_id,
                extra_body={"agent": {"name": self.agent.name, "type": "agent_reference"}},
                input="",
            )
            # Extract the response text
            response_text = response.output_text if hasattr(response, 'output_text') else str(response.output)
            
            return ChatMessage(
                role=Role.ASSISTANT,
                content=response_text if response_text else "I received your message but couldn't generate a response."
            )
                
        except Exception as e:
            print(f"Error processing message with Foundry Agent Service: {e}")
            import traceback
            traceback.print_exc()
            return ChatMessage(
                role=Role.ASSISTANT,
                content="I apologize, but I encountered an error processing your request."
            )
    
    async def cleanup(self):
        """Cleanup method for session management (no-op for Foundry Agent Service)."""
        # Foundry Agent Service handles cleanup automatically
        pass
