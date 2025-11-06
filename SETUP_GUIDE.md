# SuperAgent v8 - Setup Guide

## Quick Start

### 1. Prerequisites

Before you begin, ensure you have:
- **Python 3.10+** installed
- **pip** package manager
- **Git** (optional, for version control)
- **API Keys** from Google Gemini or Anthropic Claude

### 2. Installation

```bash
# Clone the repository (if not already done)
git clone https://github.com/jrennie99-glitch/supermen-v8.git
cd supermen-v8

# Install dependencies
pip install -r requirements.txt
```

### 3. API Key Configuration

#### Option A: Google Gemini (Recommended)

The project uses Google's Gemini AI for code generation. You need a Gemini API key to create apps.

**How to get a Gemini API key:**

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click **"Get API Key"** or **"Create API Key"**
4. Copy your API key

**Gemini API Features:**
- ✅ Free tier available (60 requests per minute)
- ✅ Fast code generation
- ✅ Supports multiple programming languages
- ✅ Good for prototyping and development

#### Option B: Anthropic Claude (Alternative)

Alternatively, you can use Anthropic's Claude AI.

**How to get an Anthropic API key:**

1. Visit [Anthropic Console](https://console.anthropic.com/)
2. Sign up or log in
3. Navigate to **API Keys** section
4. Create a new API key
5. Copy your API key

**Claude API Features:**
- ✅ Excellent code quality
- ✅ Strong reasoning capabilities
- ✅ Better for complex applications
- ❌ Requires paid account (no free tier)

### 4. Environment Setup

Create a `.env` file in the project root:

```bash
# Copy the example file
cp .env.example .env

# Edit the .env file with your favorite editor
nano .env  # or vim, code, etc.
```

**Minimum required configuration:**

```env
# At least one of these is required
GEMINI_API_KEY=your_actual_gemini_api_key_here
# OR
ANTHROPIC_API_KEY=your_actual_anthropic_api_key_here

# CORS configuration (for local development)
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5000
```

**Important:** Replace `your_actual_gemini_api_key_here` with your real API key!

### 5. Start the Server

```bash
# Start the FastAPI server
uvicorn api.index:app --host 0.0.0.0 --port 8000 --reload

# Or use Python directly
python -m uvicorn api.index:app --host 0.0.0.0 --port 8000 --reload
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 6. Access the Application

- **Web Interface:** Open `index.html` in your browser
- **API Documentation:** Visit http://localhost:8000/docs
- **Alternative Docs:** Visit http://localhost:8000/redoc

### 7. Test App Creation

#### Using the Web Interface

1. Open `index.html` in your browser
2. Type an instruction like: "Create a simple calculator app"
3. Click **"Build App"** or press Enter
4. Wait for the app to be generated
5. View your app in the preview

#### Using the API Directly

```bash
# Test the build endpoint
curl -X POST http://localhost:8000/build \
  -H "Content-Type: application/json" \
  -d '{
    "instruction": "Create a simple hello world HTML page with colorful styling",
    "language": "html"
  }'
```

**Expected response:**
```json
{
  "success": true,
  "app_name": "simple_hello_world_html_page_with_colorful_styling",
  "files": [...],
  "preview_url": "/preview/simple_hello_world_html_page_with_colorful_styling",
  "message": "✅ App built successfully!"
}
```

## Advanced Configuration

### Redis Cache (Optional)

For better performance, you can set up Redis caching:

```bash
# Install Redis
sudo apt-get install redis-server  # Ubuntu/Debian
brew install redis                  # macOS

# Start Redis
redis-server

# Add to .env
REDIS_HOST=localhost
REDIS_PORT=6379
```

### Database Setup (Optional)

For features requiring persistent storage:

```bash
# Install PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# Create database
sudo -u postgres createdb superagent

# Add to .env
DATABASE_URL=postgresql://postgres:password@localhost:5432/superagent
```

### Docker Support (Optional)

For isolated app execution:

```bash
# Ensure Docker is installed and running
docker --version

# Enable in .env
ENABLE_DOCKER_SANDBOX=true
```

## Troubleshooting

### Issue: "GEMINI_API_KEY not configured"

**Solution:**
1. Check that `.env` file exists in the project root
2. Verify `GEMINI_API_KEY` is set in `.env`
3. Ensure there are no extra spaces or quotes around the key
4. Restart the server after updating `.env`

### Issue: "Module not found" errors

**Solution:**
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Or install specific missing package
pip install <package_name>
```

### Issue: Server won't start

**Solution:**
```bash
# Check if port 8000 is already in use
lsof -i :8000

# Kill the process using port 8000
kill -9 <PID>

# Or use a different port
uvicorn api.index:app --port 8001
```

### Issue: CORS errors in browser

**Solution:**
Add your frontend URL to `ALLOWED_ORIGINS` in `.env`:
```env
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5000,http://127.0.0.1:5000
```

### Issue: API rate limits

**Solution:**
- **Gemini:** Free tier has 60 requests/minute
- **Claude:** Requires paid account
- Wait a moment between requests or upgrade your plan

## Features Overview

### Core Features
- ✅ **Natural Language to Code** - Describe what you want, get a working app
- ✅ **Multi-Language Support** - Python, JavaScript, HTML, React, Flask, FastAPI
- ✅ **Live Preview** - See your app running immediately
- ✅ **File Management** - Create, edit, delete files
- ✅ **Git Integration** - Version control built-in

### Advanced Features
- 🎙️ **Voice Interface** - Talk to SuperAgent
- 🐳 **Docker Sandbox** - Isolated execution environment
- 👥 **Multiplayer** - Collaborate in real-time
- 🔒 **Security Scanning** - Automatic vulnerability detection
- 📊 **Code Review** - AI-powered code analysis
- 🚀 **One-Click Deploy** - Deploy to Heroku, Vercel, AWS

### Enterprise Features
- 🏢 **Architecture Planning** - System design for complex apps
- 📐 **Schema Designer** - Database schema generation
- 🔌 **API Generator** - RESTful API scaffolding
- 🛠️ **DevOps Config** - CI/CD pipeline setup
- 📝 **Documentation** - Auto-generated docs

## API Endpoints

### App Building
- `POST /build` - Build a basic application
- `POST /enterprise-build` - Build enterprise-grade application
- `POST /api/v1/enterprise/build` - Full-stack enterprise app

### File Operations
- `POST /files/read` - Read file contents
- `POST /files/write` - Write to file
- `POST /files/list` - List directory contents
- `POST /files/delete` - Delete file

### Git Operations
- `POST /git/init` - Initialize repository
- `POST /git/commit` - Commit changes
- `POST /git/push` - Push to remote

### Project Management
- `POST /projects/create` - Create from template
- `GET /projects/templates` - List available templates
- `POST /projects/analyze` - Analyze project structure

### Deployment
- `POST /deploy/heroku` - Deploy to Heroku
- `POST /deploy/vercel` - Deploy to Vercel
- `POST /deploy/docker` - Generate Dockerfile

## Best Practices

### 1. API Key Security
- ❌ Never commit `.env` file to Git
- ❌ Never share your API keys publicly
- ✅ Use environment variables
- ✅ Rotate keys regularly

### 2. Resource Management
- Use Redis cache for better performance
- Monitor API usage to avoid rate limits
- Clean up unused apps periodically

### 3. Development Workflow
1. Start with simple instructions
2. Test in the web interface first
3. Use API for automation
4. Review generated code before deploying

## Getting Help

### Documentation
- **API Docs:** http://localhost:8000/docs
- **README:** See README.md for project overview
- **Issues:** Check ISSUES_FOUND.md for known issues

### Support
- **GitHub Issues:** Report bugs and request features
- **Email:** support@superagent.dev (if available)
- **Community:** Join Discord (if available)

## Next Steps

1. ✅ Complete setup following this guide
2. ✅ Test app creation with a simple project
3. ✅ Explore the API documentation
4. ✅ Try building different types of apps
5. ✅ Experiment with advanced features
6. ✅ Deploy your first app

## Example Projects to Try

### Beginner
```
"Create a simple todo list app with HTML, CSS, and JavaScript"
"Build a calculator with a nice UI"
"Make a random quote generator"
```

### Intermediate
```
"Create a Flask REST API with user authentication"
"Build a React weather app using OpenWeather API"
"Make a blog with FastAPI backend and SQLite database"
```

### Advanced
```
"Create a full-stack e-commerce platform with React frontend, FastAPI backend, PostgreSQL database, and Stripe integration"
"Build a real-time chat application with WebSocket support"
"Make a microservices architecture with Docker and Kubernetes configuration"
```

---

**Ready to build amazing apps? Start creating now! 🚀**
