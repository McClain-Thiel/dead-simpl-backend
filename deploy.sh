#!/bin/bash

# Dead Simpl Backend - GCP Deployment Script
# This script sets up the initial GCP infrastructure for the application

set -e

# Configuration - Update these variables
PROJECT_ID="your-gcp-project-id"
CLUSTER_NAME="dead-simpl-cluster"
ZONE="us-central1-a"
SERVICE_ACCOUNT_NAME="dead-simpl-deployer"

echo "🚀 Setting up Dead Simpl Backend on GCP..."

# Set the project
echo "📋 Setting GCP project to $PROJECT_ID"
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "🔌 Enabling required GCP APIs..."
gcloud services enable container.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Create GKE cluster
echo "☸️  Creating GKE cluster..."
gcloud container clusters create $CLUSTER_NAME \
  --zone=$ZONE \
  --num-nodes=3 \
  --machine-type=e2-medium \
  --enable-autoscaling \
  --min-nodes=1 \
  --max-nodes=5

# Get cluster credentials
echo "🔑 Getting cluster credentials..."
gcloud container clusters get-credentials $CLUSTER_NAME --zone=$ZONE

# Create service account for GitHub Actions
echo "👤 Creating service account for CI/CD..."
gcloud iam service-accounts create $SERVICE_ACCOUNT_NAME \
  --description="Service account for Dead Simpl deployment" \
  --display-name="Dead Simpl Deployer"

# Grant necessary permissions
echo "🔐 Granting permissions to service account..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/container.developer"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/storage.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/cloudbuild.builds.editor"

# Create service account key
echo "🔑 Creating service account key..."
gcloud iam service-accounts keys create sa-key.json \
  --iam-account=$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com

echo "✅ Initial setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Base64 encode the sa-key.json file: cat sa-key.json | base64 -w 0"
echo "2. Add the following secrets to your GitHub repository:"
echo "   - GCP_PROJECT_ID: $PROJECT_ID"
echo "   - GKE_CLUSTER_NAME: $CLUSTER_NAME"
echo "   - GKE_ZONE: $ZONE"
echo "   - GCP_SA_KEY: <base64-encoded-sa-key>"
echo "3. Update the secrets in k8s/secret.yaml with your Supabase credentials"
echo "4. Push your code to trigger the first deployment!"
echo ""
echo "🔗 Your app will be available at the LoadBalancer external IP once deployed."
