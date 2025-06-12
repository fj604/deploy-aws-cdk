# Streamlit Chatbot on AWS (CDK, ECS, Fargate, Bedrock)

This project deploys a Streamlit-based chatbot UI using Amazon Bedrock models, running in a Docker container on AWS ECS Fargate. Infrastructure is defined using AWS CDK (Python).

## Project Structure

```
.
├── app.py                        # CDK app entrypoint (infrastructure launcher)
├── cdk.json                      # CDK configuration
├── requirements.txt              # CDK/infra Python dependencies
├── docker_aws_cdk/
│   ├── docker_aws_cdk_stack.py   # Main CDK stack (infrastructure definition)
│   └── docker_app/
│       ├── streamlit_app.py      # Streamlit chatbot app (uses Bedrock)
│       ├── requirements.txt      # App dependencies (Streamlit, boto3)
│       └── Dockerfile            # Container definition for chatbot app
└── tests/                        # Unit tests
```

**Note:**

- The outer `app.py` (in the project root) is the entrypoint for the CDK application. It launches the infrastructure deployment.
- The inner `streamlit_app.py` (in `docker_aws_cdk/docker_app/`) is the actual Streamlit chatbot application that runs inside the container on ECS.

## Prerequisites

- AWS CLI configured
- AWS CDK v2 installed (`npm install -g aws-cdk`)
- Docker installed and running
- Python 3.8+

## Setup & Deployment

1. **Install dependencies:**

   ```cmd
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Bootstrap your AWS environment (once per account/region):**

   ```cmd
   cdk bootstrap
   ```

3. **Set required context values and deploy (replace with your domain):**

   ```cmd
   cdk deploy -c domain_name=yourdomain.com -c subdomain=bot
   ```

   This will:

   - Build and push the Docker image
   - Provision an ECS Fargate service behind an HTTPS load balancer
   - Set up Route53 DNS and ACM certificate for `bot.yourdomain.com`

4. **Access the chatbot:**

   Visit `https://bot.yourdomain.com` after deployment completes.

## Notes

- The chatbot UI logic is in `docker_aws_cdk/docker_app/streamlit_app.py`.
- Bedrock API access is required for the deployed service.
- To modify the chatbot, edit the Streamlit app and redeploy.
