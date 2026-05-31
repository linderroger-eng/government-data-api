# 🚂 **RAILWAY DEPLOYMENT GUIDE**

## **Step 1: Push to GitHub First** (Required for Railway)

```bash
# 1. Create GitHub repository at https://github.com/new
#    Repository name: government-data-api
#    Make it public or private (your choice)

# 2. Add GitHub as remote origin
cd ~/ventures/government-data-api
git remote add origin https://github.com/YOURUSERNAME/government-data-api.git

# 3. Push your code
git branch -M main
git push -u origin main
```

## **Step 2: Deploy on Railway** 

1. **Go to**: https://railway.app
2. **Sign up** with your GitHub account
3. **Click**: "Deploy from GitHub repo"
4. **Select**: your `government-data-api` repository  
5. **Configure**:
   - Service name: `government-data-api`
   - Region: US West (or nearest to you)
6. **Set Environment Variables** (Click Variables tab):
   ```
   USASPENDING_BASE_URL=https://api.usaspending.gov/api/v2/
   DATABASE_URL=sqlite:///./government_data.db
   API_HOST=0.0.0.0
   PORT=8000
   ```
7. **Deploy** - Railway auto-detects FastAPI and deploys! ✅

## **Step 3: Test Your Live API**

After deployment (2-3 minutes), Railway gives you a URL like:
`https://government-data-api-production-xxxx.up.railway.app`

Test it:
```bash
curl https://your-railway-url.com/
curl https://your-railway-url.com/stats
```

## **Step 4: Get Your API URL & Update RapidAPI Listing**

1. Copy your Railway URL
2. Update the RapidAPI listing with your live URL
3. List on RapidAPI marketplace
4. Start earning! 💰

---

**⚡ Total time: 10 minutes → Live API earning money! 🚀**