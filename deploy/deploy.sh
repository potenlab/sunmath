#!/usr/bin/env bash
set -euo pipefail

# ─── Configuration ──────────────────────────────────────────────────────────
REGION="ap-northeast-2"
APP_NAME="sunmath"
ECR_REPO="${APP_NAME}-backend"
RDS_INSTANCE="${APP_NAME}-db"
RDS_DB_NAME="${APP_NAME}"
RDS_USERNAME="${APP_NAME}"
RDS_ENGINE="postgres"
RDS_ENGINE_VERSION="16"
RDS_INSTANCE_CLASS="db.t4g.micro"
RDS_STORAGE=20
SG_NAME="${APP_NAME}-rds-sg"
LAMBDA_NAME="${APP_NAME}-backend"
LAMBDA_ROLE_NAME="${APP_NAME}-lambda-role"
LAMBDA_MEMORY=512
LAMBDA_TIMEOUT=30
API_NAME="${APP_NAME}-api"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="${SCRIPT_DIR}/../backend"

# ─── Colors ─────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log()  { echo -e "${GREEN}[✓]${NC} $1"; }
warn() { echo -e "${YELLOW}[!]${NC} $1"; }
err()  { echo -e "${RED}[✗]${NC} $1" >&2; }
step() { echo -e "\n${BLUE}═══ $1 ═══${NC}"; }

# ─── Phase 1: Prerequisites ────────────────────────────────────────────────
step "Phase 1: Prerequisites"

if ! command -v aws &> /dev/null; then
    err "AWS CLI not found. Install: https://aws.amazon.com/cli/"
    exit 1
fi
log "AWS CLI found"

if ! command -v docker &> /dev/null; then
    err "Docker not found. Install Docker Desktop."
    exit 1
fi
log "Docker found"

ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text --region "$REGION")
log "AWS Account: ${ACCOUNT_ID}"

ECR_URI="${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com"
IMAGE_URI="${ECR_URI}/${ECR_REPO}:latest"

# ─── Phase 2: ECR Repository ───────────────────────────────────────────────
step "Phase 2: ECR Repository"

if aws ecr describe-repositories --repository-names "$ECR_REPO" --region "$REGION" &> /dev/null; then
    log "ECR repo '${ECR_REPO}' already exists"
else
    aws ecr create-repository \
        --repository-name "$ECR_REPO" \
        --region "$REGION" \
        --image-scanning-configuration scanOnPush=true \
        --output text > /dev/null
    log "Created ECR repo '${ECR_REPO}'"
fi

# ─── Phase 3: Docker Build & Push ──────────────────────────────────────────
step "Phase 3: Docker Build & Push"

# Copy google.json into build context if it exists
GOOGLE_JSON_SRC="${SCRIPT_DIR}/../google.json"
GOOGLE_JSON_DST="${BACKEND_DIR}/google.json"
COPIED_GOOGLE_JSON=false
if [ -f "$GOOGLE_JSON_SRC" ]; then
    cp "$GOOGLE_JSON_SRC" "$GOOGLE_JSON_DST"
    COPIED_GOOGLE_JSON=true
    log "Copied google.json into build context"
else
    warn "google.json not found at project root — Vertex AI won't work"
fi

aws ecr get-login-password --region "$REGION" | \
    docker login --username AWS --password-stdin "$ECR_URI"
log "Logged in to ECR"

docker build --platform linux/arm64 --provenance=false -t "$ECR_REPO" "$BACKEND_DIR"
log "Docker image built (arm64)"

docker tag "$ECR_REPO:latest" "$IMAGE_URI"
docker push "$IMAGE_URI"
log "Pushed image to ECR"

# Cleanup google.json from build context
if [ "$COPIED_GOOGLE_JSON" = true ] && [ -f "$GOOGLE_JSON_DST" ]; then
    rm "$GOOGLE_JSON_DST"
fi

# ─── Phase 4: Security Group ───────────────────────────────────────────────
step "Phase 4: Security Group"

DEFAULT_VPC_ID=$(aws ec2 describe-vpcs \
    --filters Name=isDefault,Values=true \
    --query 'Vpcs[0].VpcId' --output text --region "$REGION")

if [ "$DEFAULT_VPC_ID" = "None" ] || [ -z "$DEFAULT_VPC_ID" ]; then
    err "No default VPC found in ${REGION}. Create one: aws ec2 create-default-vpc --region ${REGION}"
    exit 1
fi
log "Default VPC: ${DEFAULT_VPC_ID}"

SG_ID=$(aws ec2 describe-security-groups \
    --filters Name=group-name,Values="$SG_NAME" Name=vpc-id,Values="$DEFAULT_VPC_ID" \
    --query 'SecurityGroups[0].GroupId' --output text --region "$REGION" 2>/dev/null || echo "None")

if [ "$SG_ID" = "None" ] || [ -z "$SG_ID" ]; then
    SG_ID=$(aws ec2 create-security-group \
        --group-name "$SG_NAME" \
        --description "SunMath RDS security group - public access" \
        --vpc-id "$DEFAULT_VPC_ID" \
        --query 'GroupId' --output text --region "$REGION")

    aws ec2 authorize-security-group-ingress \
        --group-id "$SG_ID" \
        --protocol tcp --port 5432 \
        --cidr 0.0.0.0/0 \
        --region "$REGION" > /dev/null
    log "Created Security Group: ${SG_ID} (TCP 5432 open)"
else
    log "Security Group already exists: ${SG_ID}"
fi

# ─── Phase 5: RDS ──────────────────────────────────────────────────────────
step "Phase 5: RDS PostgreSQL"

RDS_STATUS=$(aws rds describe-db-instances \
    --db-instance-identifier "$RDS_INSTANCE" \
    --query 'DBInstances[0].DBInstanceStatus' --output text --region "$REGION" 2>/dev/null || echo "not-found")

if [ "$RDS_STATUS" = "not-found" ]; then
    RDS_PASSWORD=$(openssl rand -base64 24 | tr -d '/+=' | head -c 24)

    aws rds create-db-instance \
        --db-instance-identifier "$RDS_INSTANCE" \
        --db-instance-class "$RDS_INSTANCE_CLASS" \
        --engine "$RDS_ENGINE" \
        --engine-version "$RDS_ENGINE_VERSION" \
        --master-username "$RDS_USERNAME" \
        --master-user-password "$RDS_PASSWORD" \
        --allocated-storage "$RDS_STORAGE" \
        --storage-type gp3 \
        --db-name "$RDS_DB_NAME" \
        --vpc-security-group-ids "$SG_ID" \
        --publicly-accessible \
        --no-multi-az \
        --backup-retention-period 1 \
        --no-auto-minor-version-upgrade \
        --region "$REGION" \
        --output text > /dev/null

    log "RDS instance '${RDS_INSTANCE}' creation started"
    log "Waiting for RDS to become available (this takes 5-10 minutes)..."

    aws rds wait db-instance-available \
        --db-instance-identifier "$RDS_INSTANCE" \
        --region "$REGION"
    log "RDS is available"
else
    log "RDS instance '${RDS_INSTANCE}' already exists (status: ${RDS_STATUS})"
    warn "Cannot retrieve existing password — if you need it, check your previous deploy output"
    RDS_PASSWORD="<EXISTING_PASSWORD>"

    if [ "$RDS_STATUS" != "available" ]; then
        log "Waiting for RDS to become available..."
        aws rds wait db-instance-available \
            --db-instance-identifier "$RDS_INSTANCE" \
            --region "$REGION"
    fi
fi

RDS_ENDPOINT=$(aws rds describe-db-instances \
    --db-instance-identifier "$RDS_INSTANCE" \
    --query 'DBInstances[0].Endpoint.Address' --output text --region "$REGION")
log "RDS Endpoint: ${RDS_ENDPOINT}"

DATABASE_URL="postgresql+asyncpg://${RDS_USERNAME}:${RDS_PASSWORD}@${RDS_ENDPOINT}:5432/${RDS_DB_NAME}"

# ─── Phase 6: IAM Role ─────────────────────────────────────────────────────
step "Phase 6: IAM Role"

ROLE_ARN=$(aws iam get-role --role-name "$LAMBDA_ROLE_NAME" \
    --query 'Role.Arn' --output text 2>/dev/null || echo "not-found")

if [ "$ROLE_ARN" = "not-found" ]; then
    TRUST_POLICY='{
        "Version": "2012-10-17",
        "Statement": [{
            "Effect": "Allow",
            "Principal": {"Service": "lambda.amazonaws.com"},
            "Action": "sts:AssumeRole"
        }]
    }'

    ROLE_ARN=$(aws iam create-role \
        --role-name "$LAMBDA_ROLE_NAME" \
        --assume-role-policy-document "$TRUST_POLICY" \
        --query 'Role.Arn' --output text)

    aws iam attach-role-policy \
        --role-name "$LAMBDA_ROLE_NAME" \
        --policy-arn "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"

    log "Created IAM role: ${LAMBDA_ROLE_NAME}"
    log "Waiting 10s for IAM propagation..."
    sleep 10
else
    log "IAM role already exists: ${LAMBDA_ROLE_NAME}"
fi

# ─── Phase 7: Lambda ───────────────────────────────────────────────────────
step "Phase 7: Lambda Function"

JWT_SECRET=$(openssl rand -hex 32)

LAMBDA_EXISTS=$(aws lambda get-function --function-name "$LAMBDA_NAME" \
    --region "$REGION" 2>/dev/null && echo "yes" || echo "no")

ENV_VARS='{"Variables":{"DATABASE_URL":"'"${DATABASE_URL}"'","DEBUG":"false","CORS_ORIGINS":"[\"*\"]","JWT_SECRET":"'"${JWT_SECRET}"'","GOOGLE_APPLICATION_CREDENTIALS":"/var/task/google.json","GCP_PROJECT_ID":"express-auth-414411","GCP_LOCATION":"us-central1","GCS_BUCKET_NAME":"express-auth-414411-sunmath-ocr"}}'

if [ "$LAMBDA_EXISTS" = "no" ]; then
    aws lambda create-function \
        --function-name "$LAMBDA_NAME" \
        --package-type Image \
        --code "ImageUri=${IMAGE_URI}" \
        --role "$ROLE_ARN" \
        --architectures arm64 \
        --memory-size "$LAMBDA_MEMORY" \
        --timeout "$LAMBDA_TIMEOUT" \
        --environment "$ENV_VARS" \
        --region "$REGION" \
        --output text > /dev/null
    log "Created Lambda function: ${LAMBDA_NAME}"
else
    aws lambda update-function-code \
        --function-name "$LAMBDA_NAME" \
        --image-uri "$IMAGE_URI" \
        --region "$REGION" \
        --output text > /dev/null

    # Wait for update to complete before updating config
    aws lambda wait function-updated \
        --function-name "$LAMBDA_NAME" \
        --region "$REGION"

    aws lambda update-function-configuration \
        --function-name "$LAMBDA_NAME" \
        --memory-size "$LAMBDA_MEMORY" \
        --timeout "$LAMBDA_TIMEOUT" \
        --environment "$ENV_VARS" \
        --region "$REGION" \
        --output text > /dev/null
    log "Updated Lambda function: ${LAMBDA_NAME}"
fi

# Wait for Lambda to be active
aws lambda wait function-active-v2 \
    --function-name "$LAMBDA_NAME" \
    --region "$REGION"
log "Lambda function is active"

LAMBDA_ARN=$(aws lambda get-function \
    --function-name "$LAMBDA_NAME" \
    --query 'Configuration.FunctionArn' --output text --region "$REGION")

# ─── Phase 8: API Gateway ──────────────────────────────────────────────────
step "Phase 8: API Gateway"

API_ID=$(aws apigatewayv2 get-apis \
    --query "Items[?Name=='${API_NAME}'].ApiId | [0]" --output text --region "$REGION" 2>/dev/null || echo "None")

if [ "$API_ID" = "None" ] || [ -z "$API_ID" ]; then
    API_ID=$(aws apigatewayv2 create-api \
        --name "$API_NAME" \
        --protocol-type HTTP \
        --query 'ApiId' --output text --region "$REGION")

    INTEGRATION_ID=$(aws apigatewayv2 create-integration \
        --api-id "$API_ID" \
        --integration-type AWS_PROXY \
        --integration-uri "$LAMBDA_ARN" \
        --payload-format-version "2.0" \
        --query 'IntegrationId' --output text --region "$REGION")

    aws apigatewayv2 create-route \
        --api-id "$API_ID" \
        --route-key '$default' \
        --target "integrations/${INTEGRATION_ID}" \
        --region "$REGION" --output text > /dev/null

    aws apigatewayv2 create-stage \
        --api-id "$API_ID" \
        --stage-name '$default' \
        --auto-deploy \
        --region "$REGION" --output text > /dev/null

    log "Created API Gateway: ${API_ID}"
else
    log "API Gateway already exists: ${API_ID}"
fi

# Add Lambda invoke permission for API Gateway
aws lambda add-permission \
    --function-name "$LAMBDA_NAME" \
    --statement-id "apigateway-invoke-${API_ID}" \
    --action lambda:InvokeFunction \
    --principal apigateway.amazonaws.com \
    --source-arn "arn:aws:execute-api:${REGION}:${ACCOUNT_ID}:${API_ID}/*" \
    --region "$REGION" 2>/dev/null || true

API_URL="https://${API_ID}.execute-api.${REGION}.amazonaws.com"

# ─── Output ─────────────────────────────────────────────────────────────────
step "Deployment Complete!"

echo ""
echo -e "${GREEN}API URL:${NC}        ${API_URL}"
echo -e "${GREEN}Health:${NC}         ${API_URL}/health"
echo -e "${GREEN}Swagger:${NC}        ${API_URL}/api/docs"
echo -e "${GREEN}RDS Endpoint:${NC}   ${RDS_ENDPOINT}"
echo -e "${GREEN}RDS Password:${NC}   ${RDS_PASSWORD}"
echo -e "${GREEN}JWT Secret:${NC}     ${JWT_SECRET}"
echo ""
echo -e "${YELLOW}Post-deployment steps:${NC}"
echo ""
echo "1. Run Alembic migrations from local machine:"
echo "   cd backend"
echo "   DATABASE_URL=postgresql+asyncpg://${RDS_USERNAME}:${RDS_PASSWORD}@${RDS_ENDPOINT}:5432/${RDS_DB_NAME} \\"
echo "     alembic upgrade head"
echo ""
echo "2. Seed the database:"
echo "   DATABASE_URL=postgresql+asyncpg://${RDS_USERNAME}:${RDS_PASSWORD}@${RDS_ENDPOINT}:5432/${RDS_DB_NAME} \\"
echo "     python scripts/seed_all.py"
echo "   DATABASE_URL=postgresql+asyncpg://${RDS_USERNAME}:${RDS_PASSWORD}@${RDS_ENDPOINT}:5432/${RDS_DB_NAME} \\"
echo "     python scripts/seed_admin_settings.py"
echo ""
echo "3. Verify:"
echo "   curl ${API_URL}/health"
echo ""
echo "4. Check logs:"
echo "   aws logs tail /aws/lambda/${LAMBDA_NAME} --since 5m --region ${REGION}"
echo ""
echo -e "${YELLOW}Save these credentials securely — they won't be shown again!${NC}"
