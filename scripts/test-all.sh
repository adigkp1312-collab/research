#!/bin/bash
# Run all tests
# Team: DevOps

set -e

echo "Running all tests..."

# Set Python path
export PYTHONPATH=$(pwd)

# Core tests
echo "=== Core Tests ==="
cd packages/core && pytest tests/ -v
cd ../..

# Memory tests
echo "=== Memory Tests ==="
cd packages/langchain-memory && pytest tests/ -v
cd ../..

# Chains tests
echo "=== Chains Tests ==="
cd packages/langchain-chains && pytest tests/ -v
cd ../..

# API tests
echo "=== API Tests ==="
cd packages/api && pytest tests/ -v
cd ../..

# Integration tests
echo "=== Integration Tests ==="
cd packages/testing && pytest integration/ -v
cd ../..

echo ""
echo "All tests passed!"
