# 🔧 Vercel Environment Variables Setup

## 🚨 500 Error Fix

The **500 Internal Server Error** you're seeing is likely caused by **missing API keys** in your Vercel environment variables.

## ✅ How to Fix

### **1. Set Environment Variables in Vercel Dashboard**

1. **Go to your Vercel dashboard**: https://vercel.com/dashboard
2. **Select your backend project**: `project-launcher-p55e`
3. **Go to Settings** → **Environment Variables**
4. **Add these variables**:

```env
ANTHROPIC_API_KEY=your-anthropic-api-key-here
GOOSE_AI_API_KEY=your-goose-ai-api-key-here
```

### **2. Using Vercel CLI (Alternative)**

```bash
# Install Vercel CLI if not already installed
npm i -g vercel

# Login to Vercel
vercel login

# Set environment variables
vercel env add ANTHROPIC_API_KEY
vercel env add GOOSE_AI_API_KEY

# Redeploy
vercel --prod
```

## 🧪 Test Your Setup

### **1. Check Health Endpoint**
```bash
curl https://project-launcher-p55e.vercel.app/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "service_status": "initialized",
  "api_keys": {
    "anthropic": "configured",
    "goose_ai": "configured"
  },
  "message": "API is ready"
}
```

### **2. Test Debug Endpoint**
```bash
curl https://project-launcher-p55e.vercel.app/api/v1/debug
```

### **3. Test Frontend**
Visit: https://project-launcher.vercel.app/

## 🔍 Troubleshooting

### **If API Keys Are Missing:**
```json
{
  "status": "healthy",
  "service_status": "initialized",
  "api_keys": {
    "anthropic": "missing",
    "goose_ai": "missing"
  },
  "message": "API keys needed"
}
```

### **If Services Are Not Initialized:**
```json
{
  "status": "healthy",
  "service_status": "not initialized",
  "api_keys": {
    "anthropic": "configured",
    "goose_ai": "configured"
  },
  "message": "API is ready"
}
```

## 📋 Required Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `ANTHROPIC_API_KEY` | Your Anthropic API key | Yes (for Claude) |
| `GOOSE_AI_API_KEY` | Your GooseAI API key | Yes (for MCP) |

## 🚀 After Setting Environment Variables

1. **Redeploy your backend** (Vercel will auto-redeploy)
2. **Test the health endpoint** to confirm API keys are set
3. **Try your frontend** again

## 🎯 Success Indicators

✅ **Health endpoint** shows API keys as "configured"
✅ **No more 500 errors** when starting conversations
✅ **Frontend successfully connects** to backend
✅ **Conversations start** without errors

**Once you set the environment variables, your 500 error should be resolved!** 🎉 