# ⚡ SuperAgent - Quick Deploy (5 Minutes)

## **Fastest Way to Deploy SuperAgent**

---

## 🎯 **Choose Your Method**

### **Method 1: Local (Easiest) - 2 minutes**

```bash
# 1. Install
cd "/Users/armotorz/cursor project"
pip3 install -r requirements.txt
pip3 install -e .

# 2. Configure
export ANTHROPIC_API_KEY="sk-ant-your-key-here"

# 3. Run
superagent create "Hello World app"
```

✅ **Done!** SuperAgent is running locally.

---

### **Method 2: Docker (Recommended) - 3 minutes**

```bash
# 1. Create Dockerfile
cat > Dockerfile << 'EOF'
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
RUN pip install -e .
EXPOSE 8000
CMD ["uvicorn", "superagent.api:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

# 2. Build & Run
docker build -t superagent .
docker run -d -p 8000:8000 \
  -e ANTHROPIC_API_KEY="your-key" \
  superagent

# 3. Test
curl http://localhost:8000/health
```

✅ **Done!** SuperAgent API is running.

---

### **Method 3: Heroku (Cloud) - 5 minutes**

```bash
# 1. Create files
echo "web: uvicorn superagent.api:app --host 0.0.0.0 --port \$PORT" > Procfile
echo "python-3.10.12" > runtime.txt

# 2. Deploy
git init
git add .
git commit -m "Deploy SuperAgent"
heroku create your-app-name
heroku config:set ANTHROPIC_API_KEY=your-key
git push heroku main

# 3. Test
heroku open
```

✅ **Done!** SuperAgent is live on Heroku.

---

### **Method 4: DigitalOcean - 5 minutes**

```bash
# 1. Create droplet (Ubuntu 22.04)
# 2. SSH and run:

apt update && apt install -y python3-pip python3-venv
git clone <your-repo> /opt/superagent
cd /opt/superagent
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e .
export ANTHROPIC_API_KEY="your-key"
uvicorn superagent.api:app --host 0.0.0.0 --port 8000 &

# 3. Test
curl http://your-droplet-ip:8000/health
```

✅ **Done!** SuperAgent is running on DigitalOcean.

---

## 🚀 **That's It!**

SuperAgent is now deployed and ready to use with **Claude 4.5 Sonnet**!

### **Next Steps:**
- Test it: `superagent create "test"`
- Use API: `curl http://localhost:8000/api/v1/execute`
- Add voice: `pip install SpeechRecognition pyttsx3`

### **Full Guide:**
See `DEPLOYMENT_GUIDE.md` for detailed deployment options.

---

**SuperAgent: Deployed in minutes!** ⚡





