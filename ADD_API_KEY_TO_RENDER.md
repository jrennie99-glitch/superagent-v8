# 🔑 How to Add Gemini API Key to Your Render Deployment

## Quick Overview

Since your SuperAgent v8 is already deployed on Render, you just need to:
1. Get a Gemini API key (5 minutes)
2. Add it to Render's environment variables (2 minutes)
3. Restart your service (automatic)

**Total time: ~7 minutes**

---

## Step 1: Get Your Gemini API Key

### Option A: If You Already Have a Google Account (Faster)

1. **Visit Google AI Studio:**
   - Go to: https://makersuite.google.com/app/apikey
   - Or: https://aistudio.google.com/app/apikey

2. **Sign in with your Google account**
   - Use any Google account (Gmail, Workspace, etc.)

3. **Create API Key:**
   - Click **"Create API Key"** button
   - Select **"Create API key in new project"** (recommended)
   - Or select an existing Google Cloud project

4. **Copy Your API Key:**
   - The key will look like: `AIzaSyD...` (starts with `AIzaSy`)
   - Click the **copy icon** to copy it
   - **Important:** Save it somewhere safe - you won't see it again!

### Option B: If You Don't Have a Google Account

1. **Create a Google Account:**
   - Go to: https://accounts.google.com/signup
   - Fill in your details
   - Verify your email

2. **Then follow Option A above**

---

## Step 2: Add API Key to Render

### Method 1: Using Render Dashboard (Recommended)

1. **Go to Render Dashboard:**
   - Visit: https://dashboard.render.com/
   - Sign in to your account

2. **Find Your Service:**
   - Click on your **supermen-v8** service
   - (It should be in your list of services)

3. **Go to Environment Variables:**
   - In the left sidebar, click **"Environment"**
   - Or click the **"Environment"** tab at the top

4. **Add the API Key:**
   - Click **"Add Environment Variable"** button
   - **Key:** `GEMINI_API_KEY`
   - **Value:** Paste your API key (the one starting with `AIzaSy...`)
   - Click **"Save Changes"**

5. **Render Will Automatically:**
   - Redeploy your service
   - This takes about 2-3 minutes
   - You'll see "Deploying..." status

6. **Wait for Deployment:**
   - Wait until status shows **"Live"** (green)
   - Your app is now ready with the API key!

---

### Method 2: Using Render CLI (Alternative)

If you prefer command line:

```bash
# Install Render CLI (if not installed)
npm install -g @render/cli

# Login to Render
render login

# Add environment variable
render env set GEMINI_API_KEY="your_api_key_here" --service supermen-v8

# The service will automatically redeploy
```

---

## Step 3: Verify It's Working

### Option A: Check Health Endpoint

1. **Visit your app's health endpoint:**
   ```
   https://your-app-name.onrender.com/health
   ```

2. **You should see:**
   ```json
   {
     "status": "healthy",
     "gemini_api_configured": true,
     "message": "All systems operational"
   }
   ```

3. **If `gemini_api_configured` is `true`, you're all set!** ✅

---

### Option B: Test the Build Endpoint

1. **Try building something simple:**
   ```bash
   curl -X POST https://your-app-name.onrender.com/build \
     -H "Content-Type: application/json" \
     -d '{
       "instruction": "Create a simple hello world page",
       "requirements": {
         "frontend": "HTML"
       }
     }'
   ```

2. **If it returns code, it's working!** ✅

---

## 🎯 Complete Visual Guide

### Step-by-Step with Screenshots

#### 1. Get Gemini API Key

```
┌─────────────────────────────────────────────────────────┐
│  Google AI Studio - API Keys                            │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  [+ Create API Key]                                     │
│                                                          │
│  Your API Keys:                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │ AIzaSyD...                          [Copy] [⋮]   │  │
│  │ Created: Nov 6, 2025                             │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**Action:** Click **[Copy]** to copy your API key

---

#### 2. Open Render Dashboard

```
┌─────────────────────────────────────────────────────────┐
│  Render Dashboard                                        │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Your Services:                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │ 🟢 supermen-v8                                   │  │
│  │    Web Service • Live                            │  │
│  │    https://supermen-v8.onrender.com              │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**Action:** Click on **supermen-v8** service

---

#### 3. Go to Environment Tab

```
┌─────────────────────────────────────────────────────────┐
│  supermen-v8                                             │
├─────────────────────────────────────────────────────────┤
│  [Logs] [Events] [Environment] [Settings]               │
│                                                          │
│  Environment Variables                                  │
│  ┌──────────────────────────────────────────────────┐  │
│  │ [+ Add Environment Variable]                     │  │
│  │                                                   │  │
│  │ No environment variables yet                     │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**Action:** Click **[Environment]** tab, then **[+ Add Environment Variable]**

---

#### 4. Add GEMINI_API_KEY

```
┌─────────────────────────────────────────────────────────┐
│  Add Environment Variable                                │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Key:   [GEMINI_API_KEY                            ]    │
│                                                          │
│  Value: [AIzaSyD...                                ]    │
│                                                          │
│  [Cancel]                          [Save Changes]       │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**Action:** 
1. Type `GEMINI_API_KEY` in Key field
2. Paste your API key in Value field
3. Click **[Save Changes]**

---

#### 5. Wait for Deployment

```
┌─────────────────────────────────────────────────────────┐
│  supermen-v8                                             │
├─────────────────────────────────────────────────────────┤
│  Status: 🟡 Deploying...                                │
│                                                          │
│  Deploying changes...                                   │
│  ▓▓▓▓▓▓▓▓▓▓▓░░░░░░░░░ 60%                              │
│                                                          │
│  This usually takes 2-3 minutes                         │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**Action:** Wait for deployment to complete

---

#### 6. Deployment Complete!

```
┌─────────────────────────────────────────────────────────┐
│  supermen-v8                                             │
├─────────────────────────────────────────────────────────┤
│  Status: 🟢 Live                                        │
│                                                          │
│  Environment Variables:                                 │
│  ┌──────────────────────────────────────────────────┐  │
│  │ GEMINI_API_KEY = AIzaSy••••••••••••••           │  │
│  │                                         [Edit]   │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  ✅ Your service is live with the new API key!         │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**Action:** Done! Your app is now ready to use!

---

## 🔍 Troubleshooting

### Issue 1: "API Key Invalid" Error

**Problem:** Getting errors about invalid API key

**Solutions:**
1. **Check the key format:**
   - Should start with `AIzaSy`
   - Should be about 39 characters long
   - No extra spaces or quotes

2. **Regenerate the key:**
   - Go back to Google AI Studio
   - Delete the old key
   - Create a new one
   - Update in Render

3. **Check API is enabled:**
   - Go to: https://console.cloud.google.com/apis/library/generativelanguage.googleapis.com
   - Make sure "Generative Language API" is enabled

---

### Issue 2: Environment Variable Not Showing Up

**Problem:** Added the key but app still says it's missing

**Solutions:**
1. **Make sure you saved:**
   - Click "Save Changes" button
   - Wait for deployment to complete

2. **Check the key name:**
   - Must be exactly: `GEMINI_API_KEY`
   - All caps, with underscores
   - No typos

3. **Restart the service:**
   - Go to Settings
   - Click "Manual Deploy"
   - Click "Deploy latest commit"

---

### Issue 3: Deployment Failed

**Problem:** Deployment fails after adding API key

**Solutions:**
1. **Check the logs:**
   - Click "Logs" tab
   - Look for error messages

2. **Verify the key:**
   - Make sure it's a valid Gemini API key
   - Try the key in Google AI Studio first

3. **Contact support:**
   - If still failing, check Render status page
   - Or contact Render support

---

## 📋 Quick Checklist

Use this checklist to make sure everything is set up:

- [ ] Got Gemini API key from Google AI Studio
- [ ] Copied the API key (starts with `AIzaSy`)
- [ ] Logged into Render dashboard
- [ ] Found supermen-v8 service
- [ ] Clicked Environment tab
- [ ] Added `GEMINI_API_KEY` variable
- [ ] Pasted the API key value
- [ ] Clicked Save Changes
- [ ] Waited for deployment (2-3 min)
- [ ] Status shows "Live" (green)
- [ ] Tested /health endpoint
- [ ] Confirmed `gemini_api_configured: true`

**If all checked, you're done!** ✅

---

## 🎯 What's Your Render URL?

To help you verify, I need to know your Render URL. It should be something like:

- `https://supermen-v8.onrender.com`
- `https://supermen-v8-xyz.onrender.com`
- Or a custom domain you configured

Once you have the API key added, you can test it by visiting:
```
https://your-app-url.onrender.com/health
```

---

## 🚀 After Adding the API Key

Once the API key is configured, you can:

1. **Build applications:**
   ```bash
   curl -X POST https://your-app.onrender.com/build \
     -H "Content-Type: application/json" \
     -d '{"instruction": "Create a todo app"}'
   ```

2. **Use the 99.5% endpoint:**
   ```bash
   curl -X POST https://your-app.onrender.com/api/v1/build-995-percent \
     -H "Content-Type: application/json" \
     -d '{
       "instruction": "Create an e-commerce platform",
       "requirements": {...}
     }'
   ```

3. **Access all 93+ features** - Everything will work!

---

## 💡 Pro Tips

1. **Keep your API key secret:**
   - Never commit it to GitHub
   - Never share it publicly
   - Render keeps it encrypted

2. **Monitor usage:**
   - Check Google AI Studio for usage stats
   - Gemini has free tier limits
   - Set up billing alerts if needed

3. **Use environment-specific keys:**
   - Use different keys for dev/staging/production
   - This helps track usage by environment

4. **Backup your key:**
   - Save it in a password manager
   - You can't view it again in Google AI Studio
   - But you can always create a new one

---

## ❓ Need Help?

If you run into any issues:

1. **Check the health endpoint first:**
   ```
   https://your-app.onrender.com/health
   ```

2. **Check Render logs:**
   - Go to your service
   - Click "Logs" tab
   - Look for errors

3. **Let me know:**
   - Share your Render URL
   - Share any error messages
   - I'll help you debug!

---

## 🎉 That's It!

Once you add the API key, your SuperAgent v8 will be fully operational and ready to build 99.5% production-ready applications!

**The whole process takes about 7 minutes.** ⏱️

Good luck! 🚀
