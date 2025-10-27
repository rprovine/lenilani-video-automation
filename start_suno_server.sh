#!/bin/bash
#
# Start Suno API Server
# This script starts the local suno-api server for music generation.
#

echo "================================"
echo "STARTING SUNO API SERVER"
echo "================================"
echo ""

# Check if .env has SUNO_COOKIE
if ! grep -q "SUNO_COOKIE=" .env; then
    echo "❌ Error: SUNO_COOKIE not found in .env file"
    echo ""
    echo "To get your Suno cookie:"
    echo "1. Go to https://suno.com/create"
    echo "2. Open Developer Tools (F12 or Cmd+Option+I)"
    echo "3. Go to the Network tab"
    echo "4. Refresh the page"
    echo "5. Click on any request to suno.com"
    echo "6. Find 'Cookie' in Request Headers"
    echo "7. Copy the entire Cookie value"
    echo "8. Add it to .env as: SUNO_COOKIE=your_cookie_value"
    echo ""
    exit 1
fi

# Load .env
export $(cat .env | grep -v '^#' | xargs)

if [ -z "$SUNO_COOKIE" ] || [ "$SUNO_COOKIE" == "your_cookie_here" ]; then
    echo "❌ Error: SUNO_COOKIE is not set or is still the placeholder value"
    echo ""
    echo "Please update SUNO_COOKIE in .env with your actual cookie from suno.com"
    echo ""
    exit 1
fi

echo "✅ Suno cookie found"
echo ""
echo "Starting suno-api server on http://localhost:3000..."
echo ""

# Start the suno-api server
# The package provides a CLI command
suno-api --cookie "$SUNO_COOKIE" --port 3000

echo ""
echo "Server stopped."
