#!/usr/bin/env bash
set -euo pipefail

echo "🚀 Pushing lumi-api to AWS ECR..."

# ===== Config =====
AWS_REGION="us-east-1"
ACCOUNT_ID="067318328811"
REPO_NAME="lumi-api"
TAG="dev"

REPO_URI="${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${REPO_NAME}"

echo "Repo URI: $REPO_URI"
echo "Region:   $AWS_REGION"
echo "Tag:      $TAG"
echo ""

# ===== Step 1: Login =====
echo "🔑 Logging into ECR..."
aws ecr get-login-password --region "$AWS_REGION" \
| docker login --username AWS --password-stdin "${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"

echo "✅ Login succeeded"
echo ""

# ===== Step 2: Build =====
echo "🏗️ Building Docker image..."
docker build -t "${REPO_NAME}:latest" .

echo "✅ Build complete"
echo ""

# ===== Step 3: Tag =====
echo "🏷️ Tagging image..."
docker tag "${REPO_NAME}:latest" "${REPO_URI}:${TAG}"

echo "✅ Tag complete"
echo ""

# ===== Step 4: Push =====
echo "📦 Pushing to ECR..."
docker push "${REPO_URI}:${TAG}"

echo ""
echo "🎉 Done! Image pushed successfully:"
echo "   ${REPO_URI}:${TAG}"
