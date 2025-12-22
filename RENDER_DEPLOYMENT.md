# 🚀 Deploy to Render.com - Simple Guide

## ✅ Good News: Django Settings Already Support DATABASE_URL!

Your `girjasoft/settings.py` already checks for `DATABASE_URL` environment variable (line 117), so this will work automatically!

---

## 📋 Step-by-Step Deployment

### Step 1: Push Your Code to GitHub

```bash
# First time setup
git init
git add .
git commit -m "Ready for deployment with blue theme"

# Create repo on GitHub (go to github.com/new)
# Then push:
git remote add origin https://github.com/YOUR_USERNAME/Girjasoft-hrms.git
git push -u origin main
```

### Step 2: Deploy on Render

1. Go to https://render.com
2. Sign up for FREE (use GitHub account - easiest)
3. Click **"New +"** → **"Web Service"**
4. Connect your GitHub repository
5. Click "Connect" next to your repo

### Step 3: Configure Deployment

**In the deployment form:**

- **Name**: `girjasoft-hrms` (or any name you like)
- **Environment**: Select "Docker"
- **Dockerfile Path**: `Dockerfile` (should auto-detect)
- **Plan**: FREE (select this)

Click **"Add Database"** button
- Choose **PostgreSQL** (FREE tier)
- Name: `girjasoft-db`
- Database: `girjasoft_main`

### Step 4: Set Environment Variables

Render will show you environment variable section. Add these:

```env
# Production settings
DEBUG=false

# Secret key - generate a random one
SECRET_KEY=your-super-secret-key-here-make-it-random

# Allowed hosts - will be auto-generated
ALLOWED_HOSTS=girjasoft-hrms.onrender.com,*.onrender.com

# CSRF protection
CSRF_TRUSTED_ORIGINS=https://girjasoft-hrms.onrender.com

# Database URL - DO NOT ADD THIS MANUALLY!
# Render will add DATABASE_URL automatically when you connect the database
```

**Important**: The `DATABASE_URL` is added automatically by Render when you connect the PostgreSQL database. You don't need to add it manually!

### Step 5: Deploy!

1. Click **"Create Web Service"**
2. Wait 10-15 minutes for first deployment
3. You'll see build logs in real-time

### Step 6: Access Your App

After deployment completes, you'll get a URL like:
`https://girjasoft-hrms.onrender.com`

Visit it and you'll see your Girjasoft HRMS login page!

---

## 🔧 How DATABASE_URL Works

### Automatic Setup:
When you connect a PostgreSQL database in Render:
1. Render creates the database
2. Render automatically adds `DATABASE_URL` environment variable
3. Your Django app reads `DATABASE_URL` from settings.py line 117
4. Everything works automatically!

### Example DATABASE_URL from Render:
```
postgres://girjasoft:randompassword@dpg-xxx-oregon-postgres.render.com/girjasoft_main
```

You don't need to write this - Render does it for you!

---

## 📝 First Time Setup After Deployment

1. Visit your app URL
2. Click **"Initialize Database"**
3. Enter your `DB_INIT_PASSWORD` from your local `.env` file
4. Create admin user and you're ready!

---

## 💡 Tips

### Free Tier Limitations:
- **Spins down** after 15 min of inactivity
- **First request** after spin-down takes ~30 seconds
- **512 MB RAM**
- **No persistent disk** (but database is persistent)

### To Keep It Awake:
- Add a simple cron job to ping your URL every 5 minutes
- Or upgrade to paid ($7/month - stays awake 24/7)

### View Logs:
- Go to Render dashboard → Your service → Logs
- See real-time application logs

### Debug Issues:
- Check "Logs" tab in Render dashboard
- Common issues:
  - Static files not collected → Already configured ✅
  - Database connection → Check DATABASE_URL ✅
  - Import errors → Check requirements.txt ✅

---

## 🎨 What's Already Ready:

✅ Django detects `DATABASE_URL` automatically
✅ Gunicorn setup in `entrypoint.sh`
✅ Static files configured with WhiteNoise
✅ All blue theme changes included
✅ Production-ready settings

---

## ✅ You DON'T Need to:
- ❌ Download anything locally
- ❌ Manually set DATABASE_URL
- ❌ SSH into servers
- ❌ Configure nginx/apache
- ❌ Install PostgreSQL locally

**Just connect GitHub → Deploy → Done!**

