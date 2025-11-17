#!/bin/bash
set -e

echo "🏗️ SafeSite AI - Deploying to Cloud Run"

# Configuration
PROJECT_ID="${GCP_PROJECT_ID:-safesite-ai-bnb-2025}"
REGION="${GCP_REGION:-us-central1}"
SERVICE_NAME="safesite-ai"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}:latest"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ Error: gcloud CLI not found. Please install it first."
    echo "Visit: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if Gemini API key is set
if [ -z "$GEMINI_API_KEY" ]; then
    echo "⚠️ Warning: GEMINI_API_KEY not set in environment"
    echo "The deployed app will not work without it."
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Verify gcloud auth
echo "🔐 Verifying authentication..."
gcloud config set project ${PROJECT_ID}

# Build and push image
echo "📦 Building container image..."
gcloud builds submit --tag ${IMAGE_NAME}

if [ $? -ne 0 ]; then
    echo "❌ Build failed. Please check the error messages above."
    exit 1
fi

# Deploy to Cloud Run
echo "🚀 Deploying to Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
  --image ${IMAGE_NAME} \
  --platform managed \
  --region ${REGION} \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --max-instances 10 \
  --set-env-vars "GEMINI_API_KEY=${GEMINI_API_KEY}" \
  --set-env-vars "GCP_PROJECT_ID=${PROJECT_ID}"

if [ $? -ne 0 ]; then
    echo "❌ Deployment failed. Please check the error messages above."
    exit 1
fi

# Get service URL
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} \
  --platform managed \
  --region ${REGION} \
  --format 'value(status.url)')

echo ""
echo "✅ Deployment complete!"
echo "🌐 Service URL: ${SERVICE_URL}"
echo ""
echo "📋 Next steps:"
echo "1. Visit the URL above to test your app"
echo "2. Upload a construction site image"
echo "3. Analyze safety compliance"
echo ""
echo "🔧 To update the deployment, run this script again"
echo "📊 To view logs: gcloud run services logs read ${SERVICE_NAME} --region ${REGION}"
echo ""
