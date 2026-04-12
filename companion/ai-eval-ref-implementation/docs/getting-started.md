# Getting Started

This guide walks you through deploying the reference implementation and running your first agent evaluation.

## Prerequisites

- **Azure subscription** with permissions to create Cognitive Services / AI Services resources
- **Azure CLI** (`az`) v2.60+ installed and authenticated (`az login`)
- **Python 3.10+**
- **[uv](https://docs.astral.sh/uv/)** — fast Python package and environment manager (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- **GitHub account** with a repository for CI/CD workflows

## Step 1: Deploy infrastructure

Choose your target environment (dev, test, or prod) and deploy the Bicep templates:

```bash
# Create a resource group (if needed)
az group create --name rg-contoso-eval-dev --location eastus2

# Deploy infrastructure
az deployment group create \
  --resource-group rg-contoso-eval-dev \
  --template-file infra/main.bicep \
  --parameters infra/parameters/dev.bicepparam
```

Note the outputs — you'll need the AI Services endpoint and deployment names.

## Step 2: Create the agent

```bash
# Create a virtual environment and install dependencies
uv venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
uv pip install -r src/requirements.txt

# Set environment variables
export AZURE_AI_PROJECT_ENDPOINT="https://<your-account>.services.ai.azure.com/api/projects/<your-project>"
export AZURE_AI_AGENT_MODEL="contoso-eval-dev-agent"

# Create the agent
python src/agent/agent_definition.py
```

Note the agent name and version from the output.

## Step 3: Configure environment

```bash
cp .env.example .env
```

Edit `.env` with your values:

```
AZURE_AI_PROJECT_ENDPOINT=https://<account>.services.ai.azure.com/api/projects/<project>
AZURE_OPENAI_ENDPOINT=https://<account>.openai.azure.com/
EVALUATION_MODEL=contoso-eval-dev-judge
AGENT_NAME=Contoso-Support-Agent
AGENT_VERSION=1
```

## Step 4: Run local evaluation

```bash
python src/evaluation/run_local_eval.py
```

This runs quality and safety evaluators against the tiny development dataset. Review the output scores and iterate on your agent's instructions or tools.

## Step 5: Run cloud evaluation

```bash
python src/evaluation/run_cloud_eval.py
```

This submits an evaluation job to Foundry that invokes the agent, runs the full evaluator suite, and stores results in the Foundry portal.

## Step 6: Set up GitHub Actions CI/CD

### Configure Azure OIDC (federated credentials)

1. **Create an Azure AD app registration** for GitHub Actions:

```bash
az ad app create --display-name "contoso-eval-github-actions"
```

2. **Create a service principal**:

```bash
az ad sp create --id <app-id>
```

3. **Add a federated credential** for your GitHub repository:

```bash
az ad app federated-credential create --id <app-id> --parameters '{
  "name": "github-actions-main",
  "issuer": "https://token.actions.githubusercontent.com",
  "subject": "repo:<owner>/<repo>:ref:refs/heads/main",
  "audiences": ["api://AzureADTokenExchange"]
}'
```

4. **Assign roles** to the service principal:

```bash
az role assignment create \
  --assignee <sp-object-id> \
  --role "Cognitive Services User" \
  --scope /subscriptions/<sub-id>/resourceGroups/<rg-name>
```

### Set GitHub repository variables

In your repository settings → Secrets and variables → Actions → Variables:

| Variable | Value |
|----------|-------|
| `AZURE_CLIENT_ID` | App registration client ID |
| `AZURE_TENANT_ID` | Your Azure AD tenant ID |
| `AZURE_SUBSCRIPTION_ID` | Your Azure subscription ID |
| `AZURE_AI_PROJECT_ENDPOINT` | Foundry project endpoint URL |
| `EVALUATION_MODEL` | Judge model deployment name |
| `AGENT_ID` | Agent name:version (e.g., `Contoso-Support-Agent:1`) |

### Test the workflow

Push a change or open a PR to trigger the evaluation workflow. Check the Actions tab for the evaluation summary report.

## Adapting to your own agent

1. **Replace the agent**: Modify `src/agent/agent_definition.py` and `src/agent/tools.py` with your agent's instructions and tools
2. **Update datasets**: Create evaluation datasets in `datasets/` that cover your agent's scenarios
3. **Adjust evaluators**: Modify `src/evaluation/evaluator_config.py` to change evaluator selection and thresholds
4. **Update the eval config**: Edit `datasets/eval-config.json` with queries and evaluators relevant to your agent
