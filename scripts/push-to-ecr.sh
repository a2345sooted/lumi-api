#!/usr/bin/env bash
set -euo pipefail

echo "🚀 Building + Pushing lumi-api to AWS ECR..."

AWS_REGION="us-east-1"
ACCOUNT_ID="067318328811"
REPO_NAME="lumi-api"

TAG_DEV="dev"
TAG_LATEST="latest"
TAG_SHA=$(git rev-parse --short HEAD 2>/dev/null || echo "manual")

REPO_URI="${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${REPO_NAME}"

echo "Repo URI: $REPO_URI"
echo "Region:   $AWS_REGION"
echo "Tags:     $TAG_DEV, $TAG_LATEST, $TAG_SHA"
echo ""

echo "🔑 Logging into ECR..."
aws ecr get-login-password --region "$AWS_REGION" \
| docker login --username AWS --password-stdin \
"${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
echo "✅ Login succeeded"
echo ""

echo "🏗️ Building Docker image (tagging all outputs)..."
docker build \
  -t "${REPO_URI}:${TAG_LATEST}" \
  -t "${REPO_URI}:${TAG_DEV}" \
  -t "${REPO_URI}:${TAG_SHA}" \
  .
echo "✅ Build complete"
echo ""

echo "🔍 Local image ID (latest): $(docker images -q "${REPO_URI}:${TAG_LATEST}")"
docker inspect "${REPO_URI}:${TAG_LATEST}" --format 'Created {{.Created}} Id {{.Id}}'
echo ""

echo "📦 Pushing to ECR..."
docker push "${REPO_URI}:${TAG_DEV}"
docker push "${REPO_URI}:${TAG_LATEST}"
docker push "${REPO_URI}:${TAG_SHA}"

echo ""
echo "🎉 Done! Image pushed successfully:"
echo "   ${REPO_URI}:${TAG_DEV}"
echo "   ${REPO_URI}:${TAG_LATEST}"
echo "   ${REPO_URI}:${TAG_SHA}"
