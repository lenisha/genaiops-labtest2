import os
import re

class AzureConfig:
    def __init__(self):
        # Load environment variables for Azure configuration
        self.subscription_id = "f06766f1-b4ae-4723-afb7-281e9a742656"
        # os.environ["AZURE_SUBSCRIPTION_ID"]
        self.resource_group = "rg-rag-project-dev02"
        self.workspace_name = "ai-project-2veicpmifv5tw"
        self.location = "eastus2"
        self.aoai_endpoint = "https://aoai-2veicpmifv5tw.openai.azure.com/"
        self.aoai_api_version = "2024-05-01-preview"
        self.search_endpoint = "https://srch-2veicpmifv5tw.search.windows.net/"        
        self.aoai_api_key = os.environ["AZURE_OPENAI_API_KEY"]
        self.aoai_account_name = self.get_domain_prefix(self.aoai_endpoint)
        self.search_account_name = self.get_domain_prefix(self.search_endpoint)

        if not self.aoai_endpoint:
            # Try to get the connection information from AI Project
            # Initialize MLClient with the loaded credentials and configuration
            from azure.ai.ml import MLClient
            from azure.identity import DefaultAzureCredential
            from azure.mgmt.cognitiveservices import CognitiveServicesManagementClient

            # Initialize MLClient with the loaded credentials and configuration
            self.ml_client = MLClient(
                DefaultAzureCredential(),
                self.subscription_id,
                self.resource_group,
                self.workspace_name
            )

            # Retrieve the workspace details from Azure ML
            self.workspace = self.ml_client.workspaces.get(
                name=self.workspace_name,
                resource_group_name=self.resource_group
            )
            self.location = self.workspace.location

            # Retrieve connections for Azure OpenAI and Azure AI Search
            self.aoai_connection = self.ml_client.connections.get('aoai-connection')
            self.search_connection = self.ml_client.connections.get('rag-search')

            # Extract endpoint and API version for Azure OpenAI
            self.aoai_endpoint = self.aoai_connection.target
            self.aoai_api_version = self.aoai_connection.metadata.get('ApiVersion', '')

            # Obtain credentials and API key for Azure OpenAI
            hostname = self.aoai_endpoint.split("://")[1].split("/")[0]
            account_name = hostname.split('.')[0]
            self.cognitive_client = CognitiveServicesManagementClient(DefaultAzureCredential(), self.subscription_id)
            keys = self.cognitive_client.accounts.list_keys(self.resource_group, account_name)
            self.aoai_api_key = keys.key1
            
            # Extract endpoint for Azure AI Search
            self.search_endpoint = self.search_connection.target

            self.aoai_account_name = self.get_domain_prefix(self.aoai_endpoint)
            self.search_account_name = self.get_domain_prefix(self.search_endpoint)

    def get_domain_prefix(self, url):
        match = re.search(r'https?://([^.]+)', url)
        if match:
            return match.group(1)
        return None