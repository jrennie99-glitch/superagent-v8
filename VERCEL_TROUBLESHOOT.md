# 🔧 Vercel Deployment Troubleshooting Guide

## Quick Checklist

Before anything else, check these:

- [ ] Environment variables added to Vercel
- [ ] Latest code is pushed to GitHub
- [ ] Vercel auto-deployed the latest commit
- [ ] You're checking the correct URL

---

## Step-by-Step Fix Guide

### Step 1: Verify GitHub Push ✅

Check that the latest code is on GitHub:

```bash
cd "/Users/armotorz/cursor project"
git log -1 --oneline
```

Should show the latest commit. If not:

```bash
git add .
git commit -m "Fix Vercel deployment"
git push origin main
```

---

### Step 2: Add Environment Variables to Vercel 🔑

**This is the most common issue!**

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click on your project (`superagent1`)
3. Go to **Settings** → **Environment Variables**
4. Add these two variables:

#### Variable 1: ANTHROPIC_API_KEY
- **Name:** `ANTHROPIC_API_KEY`
- **Value:** Your Claude API key from https://console.anthropic.com/
- **Environment:** Production, Preview, Development (select all)
- Click **Save**

#### Variable 2: SUPERAGENT_API_KEY
- **Name:** `SUPERAGENT_API_KEY`
- **Value:** Generate one with: `openssl rand -hex 32`
  - Or use: `dev-key-change-in-production` (for testing)
- **Environment:** Production, Preview, Development (select all)
- Click **Save**

**Important:** Save your `SUPERAGENT_API_KEY` somewhere safe - you'll need it to call your API!

---

### Step 3: Trigger a Redeploy 🔄

After adding environment variables, you MUST redeploy:

**Option A: Redeploy from Dashboard**
1. Go to **Deployments** tab
2. Click the three dots (...) on the latest deployment
3. Click **Redeploy**
4. Wait 1-2 minutes

**Option B: Push a Small Change**
```bash
cd "/Users/armotorz/cursor project"
echo "# Updated $(date)" >> README.md
git add README.md
git commit -m "Trigger Vercel redeploy"
git push origin main
```

Vercel will auto-deploy in 1-2 minutes.

---

### Step 4: Check Deployment Status 📊

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click on your project
3. Look at the **Deployments** tab
4. Check the status:
   - ✅ **Ready** = Deployed successfully!
   - ⏳ **Building** = Wait a minute
   - ❌ **Failed** = Click to see error logs

---

### Step 5: Test Your API 🧪

Once deployment shows **Ready**, test these URLs:

**Public endpoints (no key needed):**

```bash
# Root endpoint
curl https://your-project.vercel.app/

# Health check
curl https://your-project.vercel.app/health

# Info
curl https://your-project.vercel.app/info

# API Docs (open in browser)
https://your-project.vercel.app/docs
```

**Protected endpoint (needs API key):**

```bash
curl -X POST https://your-project.vercel.app/generate \
  -H "X-API-Key: your-superagent-api-key-here" \
  -H "Content-Type: application/json" \
  -d '{
    "instruction": "Create a hello world function",
    "language": "python"
  }'
```

Replace:
- `https://your-project.vercel.app` with your actual Vercel URL
- `your-superagent-api-key-here` with your `SUPERAGENT_API_KEY`

---

## Common Errors and Fixes

### Error 1: "500 INTERNAL_SERVER_ERROR"

**Cause:** Environment variables not set or deployment not refreshed

**Fix:**
1. Add environment variables (Step 2)
2. Redeploy (Step 3)
3. Wait 2 minutes
4. Try again

---

### Error 2: "No FastAPI entrypoint found"

**Cause:** Vercel can't find `api/index.py`

**Fix:** Make sure these files exist:
- `/Users/armotorz/cursor project/api/index.py`
- `/Users/armotorz/cursor project/vercel.json`

Check with:
```bash
ls -la "/Users/armotorz/cursor project/api/index.py"
ls -la "/Users/armotorz/cursor project/vercel.json"
```

If missing, the files weren't pushed to GitHub. Push again.

---

### Error 3: "ANTHROPIC_API_KEY not configured on Vercel"

**Cause:** You didn't add the Anthropic API key as an environment variable

**Fix:**
1. Get your API key from https://console.anthropic.com/
2. Add to Vercel as `ANTHROPIC_API_KEY` (Step 2)
3. Redeploy (Step 3)

---

### Error 4: "401 Unauthorized" or "403 Forbidden"

**Cause:** API key missing or incorrect

**Fix:**
- Make sure you're sending `X-API-Key` header
- Use the value you set as `SUPERAGENT_API_KEY` in Vercel
- Check spelling and spacing (no extra spaces!)

Example:
```bash
curl -X POST https://your-url.vercel.app/generate \
  -H "X-API-Key: dev-key-change-in-production" \
  -H "Content-Type: application/json" \
  -d '{"instruction": "test"}'
```

---

### Error 5: Build Failed

**Cause:** Dependency issue or syntax error

**Fix:**
1. Click on the failed deployment in Vercel
2. Read the build logs
3. Look for error messages
4. Share the error with me so I can help fix it!

---

### Error 6: "This Serverless Function has crashed"

**Cause:** Import error or missing dependency

**Fix:**
1. Check `requirements.txt` is pushed to GitHub
2. Make sure it only has:
   ```
   fastapi
   anthropic
   pydantic
   ```
3. Redeploy

---

## How to Find Your Vercel URL

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click on your project
3. Look for the **Domains** section
4. Copy the URL (e.g., `https://superagent1.vercel.app`)

---

## Verify Everything Is Pushed to GitHub

```bash
cd "/Users/armotorz/cursor project"

# Check what files are in your repo
git ls-files | grep -E "(api/index.py|vercel.json|requirements.txt)"

# Should show:
# api/index.py
# vercel.json
# requirements.txt
```

If any are missing:
```bash
git add api/index.py vercel.json requirements.txt
git commit -m "Add Vercel deployment files"
git push origin main
```

---

## Current File Contents (For Reference)

### api/index.py
```python
# Should be 123 lines
# Should have: FastAPI app, /health, /generate, /info endpoints
# Should import: fastapi, anthropic, pydantic
```

### vercel.json
```json
{
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "api/index.py"
    }
  ]
}
```

### requirements.txt
```
fastapi
anthropic
pydantic
```

---

## Still Not Working?

Tell me:

1. **What error do you see?**
   - Exact error message
   - Status code (500, 404, etc.)
   - Screenshot if possible

2. **What URL are you trying?**
   - Copy/paste the URL

3. **Did you add environment variables?**
   - Yes/No for `ANTHROPIC_API_KEY`
   - Yes/No for `SUPERAGENT_API_KEY`

4. **Deployment status?**
   - Building
   - Ready
   - Failed (share error logs)

5. **Copy the build log**
   - Go to Vercel → Deployments → Latest
   - Copy the build output
   - Share with me

With this info, I can pinpoint the exact issue! 🎯

---

## Quick Test Script

Copy and run this to test everything:

```bash
#!/bin/bash

echo "=== VERCEL DEPLOYMENT TEST ==="
echo ""

# Test 1: Check files exist locally
echo "1. Checking local files..."
if [ -f "api/index.py" ]; then
    echo "   ✅ api/index.py exists"
else
    echo "   ❌ api/index.py MISSING"
fi

if [ -f "vercel.json" ]; then
    echo "   ✅ vercel.json exists"
else
    echo "   ❌ vercel.json MISSING"
fi

if [ -f "requirements.txt" ]; then
    echo "   ✅ requirements.txt exists"
else
    echo "   ❌ requirements.txt MISSING"
fi

echo ""

# Test 2: Check if pushed to GitHub
echo "2. Checking GitHub..."
echo "   Latest commit:"
git log -1 --oneline
echo ""

# Test 3: Instructions
echo "3. Next steps:"
echo "   → Go to: https://vercel.com/dashboard"
echo "   → Check if environment variables are set"
echo "   → Trigger a redeploy"
echo "   → Test: https://your-project.vercel.app/health"
echo ""

echo "=== TEST COMPLETE ==="
```

Save this as `test_vercel.sh` and run:
```bash
chmod +x test_vercel.sh
./test_vercel.sh
```

---

## Working Example URLs

Once deployed correctly, these should work:

```
https://your-project.vercel.app/          → Project info
https://your-project.vercel.app/health    → Health check
https://your-project.vercel.app/info      → API info
https://your-project.vercel.app/docs      → Interactive docs
```

These need API key:
```
POST https://your-project.vercel.app/generate
```

---

## Environment Variables Summary

You need exactly TWO environment variables in Vercel:

| Variable | Where to Get | Purpose |
|----------|--------------|---------|
| `ANTHROPIC_API_KEY` | https://console.anthropic.com/ | Claude API access |
| `SUPERAGENT_API_KEY` | Generate with `openssl rand -hex 32` | Protect your API |

Both must be added in:
**Vercel Dashboard → Your Project → Settings → Environment Variables**

Then **REDEPLOY** for changes to take effect!

---

**Let me know what you see and I'll help fix it!** 🚀

