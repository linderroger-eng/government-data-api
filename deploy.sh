#!/bin/bash
"""
Deploy Government Data API to Railway/Heroku/DigitalOcean
"""

echo "🚀 GOVERNMENT DATA API - DEPLOYMENT SCRIPT"
echo "=========================================="

# Check if we're ready to deploy
if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt not found. Run from project directory."
    exit 1
fi

echo "✅ Project files found"

# Option 1: Railway (Recommended - $5/month)
echo ""
echo "🚂 RAILWAY DEPLOYMENT (Recommended)"
echo "1. Install Railway CLI: curl -fsSL https://railway.app/install.sh | sh"
echo "2. Login: railway login"
echo "3. Deploy: railway up"
echo ""

# Option 2: Heroku
echo "🔷 HEROKU DEPLOYMENT"
echo "1. Install Heroku CLI: brew install heroku/brew/heroku"
echo "2. Login: heroku login"
echo "3. Create app: heroku create your-gov-data-api"
echo "4. Deploy: git push heroku main"
echo ""

# Option 3: DigitalOcean App Platform
echo "🌊 DIGITALOCEAN APP PLATFORM"
echo "1. Push to GitHub: git push origin main"
echo "2. Go to: https://cloud.digitalocean.com/apps"
echo "3. Create App from GitHub repo"
echo ""

# Create Procfile for Heroku
cat > Procfile << EOF
web: uvicorn main:app --host 0.0.0.0 --port \$PORT
EOF

echo "✅ Created Procfile for Heroku"

# Create railway.toml for Railway
cat > railway.toml << EOF
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "uvicorn main:app --host 0.0.0.0 --port \$PORT"
healthcheckPath = "/"
healthcheckTimeout = 300
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 10
EOF

echo "✅ Created railway.toml for Railway"

# Environment variables needed
echo ""
echo "📝 ENVIRONMENT VARIABLES TO SET:"
echo "USASPENDING_BASE_URL=https://api.usaspending.gov/api/v2/"
echo "DATABASE_URL=sqlite:///./government_data.db"
echo "API_HOST=0.0.0.0"
echo "API_PORT=8000"
echo ""

echo "🎯 Next Steps:"
echo "1. Choose deployment platform above"
echo "2. Set environment variables"
echo "3. Deploy!"
echo "4. Test your live API"
echo "5. List on RapidAPI marketplace"
echo ""
echo "💰 Expected Revenue: $5,000-15,000/month"