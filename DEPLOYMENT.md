# 🚀 Deployment Guide - Render + Vercel

## Overview
- **Backend (Flask API)**: Deploy to [Render](https://render.com)
- **Frontend (React)**: Deploy to [Vercel](https://vercel.com)

---

## 📋 Prerequisites

### Accounts Required
- [Render.com](https://render.com) account (free tier available)
- [Vercel.com](https://vercel.com) account (free tier available)
- AWS Account with IAM credentials (for data collection)
- GitHub account (recommended for both platforms)

### Local Setup
1. Clone the repository
2. Copy `.env.example` to `.env` and fill in your AWS credentials
3. Run locally first to verify everything works

---

## 🔧 Backend Deployment (Render)

### Step 1: Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/cloud-costing-intelligence.git
git push -u origin main
```

### Step 2: Create Render Service
1. Go to [render.com](https://render.com)
2. Click **New** → **Web Service**
3. Select your GitHub repository
4. Configure:
   - **Name**: `cloud-cost-backend`
   - **Runtime**: Python 3.11
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT wsgi:app`

### Step 3: Add Environment Variables
In Render Dashboard → Your Service → Environment:
```
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=us-east-1
AWS_PROFILE=default
CLOUDWATCH_NAMESPACE=HackathonMetrics
MONITORED_RESOURCES=i-your-instance-id
FLASK_ENV=production
FLASK_DEBUG=false
LOG_LEVEL=INFO
```

### Step 4: Deploy
- Render automatically deploys on Git push
- Your API will be available at: `https://cloud-cost-backend.onrender.com`
- Health check endpoint: `https://cloud-cost-backend.onrender.com/health`
- Stats endpoint: `https://cloud-cost-backend.onrender.com/api/stats`

**Note**: Render free tier services spin down after 15 minutes of inactivity. Use paid tier for production 24/7 uptime.

---

## 🎨 Frontend Deployment (Vercel)

### Step 1: Create Vercel Project
1. Go to [vercel.com](https://vercel.com)
2. Click **Add New** → **Project**
3. Select your GitHub repository
4. Configure:
   - **Framework Preset**: Vite
   - **Root Directory**: `./frontend`
   - **Build Command**: `npm install && npm run build`
   - **Output Directory**: `frontend/dist`

### Step 2: Add Environment Variables
In Vercel Project Settings → Environment Variables:
```
VITE_API_URL=https://cloud-cost-backend.onrender.com
```

### Step 3: Deploy
- Vercel automatically deploys on Git push
- Your frontend will be available at: `https://your-project.vercel.app`
- Production URL: Same as above (Vercel handles domains)

---

## 🔌 Connecting Frontend to Backend

### For Development
1. Start backend locally:
```bash
python -m src.anomaly_detection.server
```

2. Frontend `.env.local`:
```
VITE_API_URL=http://localhost:5000
```

3. Start frontend:
```bash
cd frontend
npm run dev
```

### For Production
Frontend automatically uses `VITE_API_URL` from Vercel environment variables.

---

## 📊 Environment Variables Summary

| Variable | Backend | Frontend | Required |
|----------|---------|----------|----------|
| `AWS_ACCESS_KEY_ID` | ✅ | ❌ | Yes |
| `AWS_SECRET_ACCESS_KEY` | ✅ | ❌ | Yes |
| `AWS_REGION` | ✅ | ❌ | Yes |
| `FLASK_ENV` | ✅ | ❌ | Yes (production) |
| `VITE_API_URL` | ❌ | ✅ | Yes |
| `MONITORED_RESOURCES` | ✅ | ❌ | No (has default) |
| `CLOUDWATCH_NAMESPACE` | ✅ | ❌ | No (has default) |

---

## 🧪 Testing Deployment

### Backend Health Check
```bash
curl https://cloud-cost-backend.onrender.com/health
```

### Backend Stats Endpoint
```bash
curl https://cloud-cost-backend.onrender.com/api/stats
```

### Frontend Live Check
Visit: `https://your-project.vercel.app`

---

## ⚠️ Common Issues

### Issue: Frontend shows "API Error" or blank data
**Solution**: 
- Verify `VITE_API_URL` is set correctly in Vercel
- Check that Render backend is running: `curl https://cloud-cost-backend.onrender.com/health`
- Check browser console for CORS errors

### Issue: Render service keeps spinning down
**Solution**: 
- Upgrade to Paid plan for 24/7 uptime
- Or keep a monitor hitting the `/health` endpoint to prevent spin-down

### Issue: Frontend deployment fails in Vercel
**Solution**:
- Make sure Build Command is: `npm install && npm run build`
- Root Directory should be: `./frontend`
- Check Node.js version (should be v18+)

### Issue: Backend returns 500 error
**Solution**:
- Check Render logs (Dashboard → Your Service → Logs)
- Verify all AWS environment variables are set
- Ensure AWS credentials have CloudWatch permissions

---

## 🔐 Security Best Practices

1. **Never commit `.env` file** - Only share `.env.example`
2. **Use Render/Vercel UI for secrets** - Never hardcode credentials
3. **Rotate AWS keys periodically** - If compromised, regenerate immediately
4. **Enable HTTPS** - Both platforms provide it automatically
5. **Use IAM roles** - Instead of direct AWS keys if possible

---

## 📈 Scaling & Performance

### Render
- **Free Tier**: Auto-sleeps after 15 min inactivity
- **Pro Tier**: $7-12/month, 24/7 uptime, auto-scaling
- **Upgrade**: Dashboard → Your Service → Settings → Upgrade

### Vercel
- **Free Tier**: Unlimited deployments, edge functions limited
- **Pro Tier**: $20/month, advanced analytics, priority support
- **Upgrade**: Account Settings → Billing

---

## 🔄 Continuous Deployment

### Automatic Deployment
- Both Render and Vercel auto-deploy on Git push to main branch
- Monitor deployments in their dashboards

### Custom Deploy Hooks
```bash
# Trigger Render redeploy via webhook
curl -X POST https://api.render.com/deploy/srv-{service-id}?key={api-key}

# Trigger Vercel redeploy via webhook
curl -X POST https://api.vercel.com/v1/deployments \
  -H "Authorization: Bearer $VERCEL_TOKEN" \
  -d '{"name":"cloud-costing-intelligence"}'
```

---

## 📞 Support

- **Render Support**: [docs.render.com](https://docs.render.com)
- **Vercel Support**: [vercel.com/docs](https://vercel.com/docs)
- **Project Issues**: Check GitHub Issues or email maintainer

