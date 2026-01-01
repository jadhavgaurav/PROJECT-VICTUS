#!/bin/bash
echo "🔍 Verifying Microsoft OAuth Configuration..."
echo ""

# Check if MS_CLIENT_SECRET is in .env
if grep -q "^MS_CLIENT_SECRET=" .env 2>/dev/null; then
    echo "✅ MS_CLIENT_SECRET: Found in .env"
    SECRET_LENGTH=$(grep "^MS_CLIENT_SECRET=" .env | cut -d'=' -f2 | wc -c)
    if [ $SECRET_LENGTH -gt 10 ]; then
        echo "   Secret appears to be set (length: $((SECRET_LENGTH-1)) chars)"
    else
        echo "   ⚠️  Secret might be empty or too short"
    fi
else
    echo "❌ MS_CLIENT_SECRET: NOT FOUND in .env"
    echo ""
    echo "To add it:"
    echo "1. Get secret from Azure Portal"
    echo "2. Add this line to .env:"
    echo "   MS_CLIENT_SECRET=your_secret_value_here"
fi

echo ""
echo "📋 Current Microsoft OAuth settings:"
grep -E "^MS_|^MICROSOFT" .env | sed 's/=.*/=***/' | sort
