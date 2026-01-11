#!/bin/bash
# Setup script for artful-striker-483214-b0 project

export GOOGLE_CLOUD_PROJECT=artful-striker-483214-b0
export VERTEX_AI_LOCATION=us-central1

echo "✅ Project configured: $GOOGLE_CLOUD_PROJECT"
echo "✅ Location: $VERTEX_AI_LOCATION"
echo ""
echo "To use in your shell, run:"
echo "  source setup_project.sh"
echo ""
echo "Or export manually:"
echo "  export GOOGLE_CLOUD_PROJECT=artful-striker-483214-b0"
echo "  export VERTEX_AI_LOCATION=us-central1"
