#!/bin/bash

# Script to run all tests for the Health Score API project

# Ensure the script is run from the project root directory
if [ ! -d "health_score_api/app" ]; then
  echo "Error: This script must be run from the project root directory."
  exit 1
fi

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
  echo "pytest is not installed. Installing now..."
  pip install pytest
fi

# Check if pytest-asyncio is installed
if ! pip show pytest-asyncio &> /dev/null; then
  echo "pytest-asyncio is not installed. Installing now..."
  pip install pytest-asyncio
fi

# Run tests with pytest
echo "Running tests for Health Score API..."
cd health_score_api/app
test_result=$(pytest tests/ -v --asyncio-mode=auto 2>&1)
echo "$test_result"
cd ../..

# Check if tests passed or failed
if echo "$test_result" | grep -q "ERRORS"; then
  echo "Test suite completed with errors."
  exit 1
else
  echo "All tests passed successfully."
  exit 0
fi
