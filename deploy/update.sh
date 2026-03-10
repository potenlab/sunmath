#!/usr/bin/env bash
set -euo pipefail

# ─── Configuration ──────────────────────────────────────────────────────────
REGION="ap-northeast-2"
ECR_REPO="sunmath-backend"
LAMBDA_NAME="sunmath-backend"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="${SCRIPT_DIR}/../backend"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log()  { echo -e "${GREEN}[✓]${NC} $1"; }
warn() { echo -e "${YELLOW}[!]${NC} $1"; }

# ─── Build & Push ───────────────────────────────────────────────────────────
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text --region "$REGION")
ECR_URI="${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com"
IMAGE_URI="${ECR_URI}/${ECR_REPO}:latest"

# Copy google.json into build context if it exists
GOOGLE_JSON_SRC="${SCRIPT_DIR}/../google.json"
GOOGLE_JSON_DST="${BACKEND_DIR}/google.json"
COPIED_GOOGLE_JSON=false
if [ -f "$GOOGLE_JSON_SRC" ]; then
    cp "$GOOGLE_JSON_SRC" "$GOOGLE_JSON_DST"
    COPIED_GOOGLE_JSON=true
    log "Copied google.json into build context"
else
    warn "google.json not found — Vertex AI won't work"
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

# ─── Update Lambda ──────────────────────────────────────────────────────────
aws lambda update-function-code \
    --function-name "$LAMBDA_NAME" \
    --image-uri "$IMAGE_URI" \
    --region "$REGION" \
    --output text > /dev/null

aws lambda wait function-updated \
    --function-name "$LAMBDA_NAME" \
    --region "$REGION"

log "Lambda function updated"
echo ""
echo -e "${GREEN}Deployment complete!${NC} New code is live."
