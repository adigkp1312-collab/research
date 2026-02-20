#!/bin/bash
# Setup script for project-9881b278-0a45-47c1-9ed project

export GOOGLE_CLOUD_PROJECT=project-9881b278-0a45-47c1-9ed
export VERTEX_AI_LOCATION=us-central1

echo "✅ Project configured: $GOOGLE_CLOUD_PROJECT"
echo "✅ Location: $VERTEX_AI_LOCATION"
echo ""
echo "To use in your shell, run:"
echo "  source setup_project.sh"
echo ""
echo "Or export manually:"
echo "  export GOOGLE_CLOUD_PROJECT=project-9881b278-0a45-47c1-9ed"
echo "  export VERTEX_AI_LOCATION=us-central1"
