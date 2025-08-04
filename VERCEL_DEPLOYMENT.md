# 🚀 Vercel Backend Deployment Guide

## ✅ Fixed Issues

The Vercel deployment error has been resolved! The issue was with the runtime configuration format.

### **What Was Fixed:**

1. **Runtime Format**: Changed from `"runtime": "python3.11"` to `"runtime": "python@3.11"`
2. **Deployment Strategy**: Switched from individual serverless functions to FastAPI app deployment
3. **Configuration**: Updated `vercel.json` to use `@vercel/python` builder

## 📁 Updated Files

### **`vercel.json`** - New Configuration
```json
{
  "version": 2,
  "builds": [
    {
      "src": "main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "main.py"
    }
  ],
  "env": {
    "PYTHONPATH": "."
  }
}
```

### **`requirements-vercel.txt`** - Updated Dependencies
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
anthropic==0.7.8
openai==1.3.7
requests==2.31.0
python-dotenv==1.0.0
pydantic==2.5.0
pydantic-settings==2.1.0
structlog==23.2.0
python-multipart==0.0.6
```

## 🚀 Deployment Steps

### **1. Prepare Your Repository**
```bash
cd web-app/backend
git add .
git commit -m "Fix Vercel deployment configuration"
git push origin main
```

### **2. Deploy to Vercel**

**Option A: Vercel CLI**
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod
```

**Option B: Vercel Dashboard**
1. Go to [vercel.com](https://vercel.com)
2. Import your GitHub repository
3. Set the root directory to `web-app/backend`
4. Deploy

### **3. Environment Variables**
Set these in Vercel dashboard:
```env
ANTHROPIC_API_KEY=your-anthropic-key
GOOSE_AI_API_KEY=your-goose-ai-key
```

## 🎯 API Endpoints

After deployment, your API will be available at:
- **Base URL**: `https://your-app.vercel.app`
- **Health Check**: `GET /health`
- **Conversation**: `POST /api/v1/conversation/start`
- **MCP Status**: `GET /api/v1/mcp/status`

## 🔧 Configuration Details

### **Build Process**
- **Builder**: `@vercel/python`
- **Entry Point**: `main.py`
- **Python Version**: 3.11
- **Dependencies**: `requirements-vercel.txt`

### **Routing**
- All requests route to `main.py`
- FastAPI handles routing internally
- CORS configured for frontend integration

## 🧪 Testing Deployment

### **Health Check**
```bash
curl https://your-app.vercel.app/health
```

### **MCP Status**
```bash
curl https://your-app.vercel.app/api/v1/mcp/status
```

### **Start Conversation**
```bash
curl -X POST https://your-app.vercel.app/api/v1/conversation/start \
  -H "Content-Type: application/json" \
  -d '{"project_idea": "Test project"}'
```

## 🔍 Troubleshooting

### **Common Issues**

1. **Environment Variables Missing**
   - Set `ANTHROPIC_API_KEY` and `GOOSE_AI_API_KEY` in Vercel dashboard

2. **Build Failures**
   - Check `requirements-vercel.txt` for correct dependencies
   - Ensure `main.py` is in the root directory

3. **Runtime Errors**
   - Check Vercel function logs
   - Verify Python version compatibility

### **Debug Commands**
```bash
# Check build logs
vercel logs

# Test locally
vercel dev

# Check environment
vercel env ls
```

## 🎉 Success Indicators

✅ **Build completes** without runtime errors
✅ **Health check** returns `200 OK`
✅ **API endpoints** respond correctly
✅ **MCP functionality** works as expected

## 📞 Support

If you encounter issues:
1. Check Vercel build logs
2. Verify environment variables
3. Test endpoints individually
4. Review this deployment guide

**Your backend should now deploy successfully to Vercel!** 🚀 