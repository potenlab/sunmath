#!/usr/bin/env bash
set -euo pipefail

# ─── Configuration ──────────────────────────────────────────────────────────
REGION="ap-northeast-2"
APP_NAME="sunmath"
ECR_REPO="${APP_NAME}-backend"
RDS_INSTANCE="${APP_NAME}-db"
LAMBDA_NAME="${APP_NAME}-backend"
LAMBDA_ROLE_NAME="${APP_NAME}-lambda-role"
API_NAME="${APP_NAME}-api"
SG_NAME="${APP_NAME}-rds-sg"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log()  { echo -e "${GREEN}[✓]${NC} $1"; }
warn() { echo -e "${YELLOW}[!]${NC} $1"; }
err()  { echo -e "${RED}[✗]${NC} $1" >&2; }
step() { echo -e "\n${BLUE}═══ $1 ═══${NC}"; }

# ─── Confirmation ───────────────────────────────────────────────────────────
echo -e "${RED}WARNING: This will permanently destroy ALL SunMath AWS resources:${NC}"
echo "  - API Gateway"
echo "  - Lambda function"
echo "  - IAM role"
echo "  - RDS database (ALL DATA WILL BE LOST)"
echo "  - Security group"
echo "  - ECR repository (all images)"
echo ""
read -p "Type 'destroy' to confirm: " CONFIRM
if [ "$CONFIRM" != "destroy" ]; then
    echo "Aborted."
    exit 0
fi

ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text --region "$REGION")

# ─── 1. API Gateway ────────────────────────────────────────────────────────
step "Deleting API Gateway"

API_ID=$(aws apigatewayv2 get-apis \
    --query "Items[?Name=='${API_NAME}'].ApiId | [0]" --output text --region "$REGION" 2>/dev/null || echo "None")

if [ "$API_ID" != "None" ] && [ -n "$API_ID" ]; then
    aws apigatewayv2 delete-api --api-id "$API_ID" --region "$REGION"
    log "Deleted API Gateway: ${API_ID}"
else
    warn "API Gateway not found"
fi

# ─── 2. Lambda ──────────────────────────────────────────────────────────────
step "Deleting Lambda Function"

if aws lambda get-function --function-name "$LAMBDA_NAME" --region "$REGION" &> /dev/null; then
    aws lambda delete-function --function-name "$LAMBDA_NAME" --region "$REGION"
    log "Deleted Lambda: ${LAMBDA_NAME}"
else
    warn "Lambda function not found"
fi

# ─── 3. IAM Role ───────────────────────────────────────────────────────────
step "Deleting IAM Role"

if aws iam get-role --role-name "$LAMBDA_ROLE_NAME" &> /dev/null; then
    # Detach all policies first
    POLICIES=$(aws iam list-attached-role-policies \
        --role-name "$LAMBDA_ROLE_NAME" \
        --query 'AttachedPolicies[].PolicyArn' --output text)

    for POLICY_ARN in $POLICIES; do
        aws iam detach-role-policy \
            --role-name "$LAMBDA_ROLE_NAME" \
            --policy-arn "$POLICY_ARN"
    done

    aws iam delete-role --role-name "$LAMBDA_ROLE_NAME"
    log "Deleted IAM role: ${LAMBDA_ROLE_NAME}"
else
    warn "IAM role not found"
fi

# ─── 4. RDS ─────────────────────────────────────────────────────────────────
step "Deleting RDS Instance"

RDS_STATUS=$(aws rds describe-db-instances \
    --db-instance-identifier "$RDS_INSTANCE" \
    --query 'DBInstances[0].DBInstanceStatus' --output text --region "$REGION" 2>/dev/null || echo "not-found")

if [ "$RDS_STATUS" != "not-found" ]; then
    aws rds delete-db-instance \
        --db-instance-identifier "$RDS_INSTANCE" \
        --skip-final-snapshot \
        --region "$REGION" --output text > /dev/null
    log "RDS deletion started (takes a few minutes)..."

    aws rds wait db-instance-deleted \
        --db-instance-identifier "$RDS_INSTANCE" \
        --region "$REGION"
    log "RDS instance deleted"
else
    warn "RDS instance not found"
fi

# ─── 5. Security Group ─────────────────────────────────────────────────────
step "Deleting Security Group"

DEFAULT_VPC_ID=$(aws ec2 describe-vpcs \
    --filters Name=isDefault,Values=true \
    --query 'Vpcs[0].VpcId' --output text --region "$REGION")

SG_ID=$(aws ec2 describe-security-groups \
    --filters Name=group-name,Values="$SG_NAME" Name=vpc-id,Values="$DEFAULT_VPC_ID" \
    --query 'SecurityGroups[0].GroupId' --output text --region "$REGION" 2>/dev/null || echo "None")

if [ "$SG_ID" != "None" ] && [ -n "$SG_ID" ]; then
    aws ec2 delete-security-group --group-id "$SG_ID" --region "$REGION"
    log "Deleted Security Group: ${SG_ID}"
else
    warn "Security Group not found"
fi

# ─── 6. ECR ─────────────────────────────────────────────────────────────────
step "Deleting ECR Repository"

if aws ecr describe-repositories --repository-names "$ECR_REPO" --region "$REGION" &> /dev/null; then
    aws ecr delete-repository \
        --repository-name "$ECR_REPO" \
        --force \
        --region "$REGION" --output text > /dev/null
    log "Deleted ECR repo: ${ECR_REPO}"
else
    warn "ECR repo not found"
fi

# ─── Done ───────────────────────────────────────────────────────────────────
step "Teardown Complete"
echo -e "${GREEN}All SunMath AWS resources have been destroyed.${NC}"
