# SuperAgent - Complete Replit Agent Clone

## Overview
SuperAgent is a complete Replit Agent clone designed to provide a fully autonomous agent experience. It enables users to generate, manage, and deploy applications efficiently using natural language to produce production-ready code. The project's ambition is to deliver a robust development platform with advanced AI features, enhancing productivity and code quality through autonomous planning, multi-step execution, and comprehensive code generation. 

**Platform Status:** Successfully migrated from Vercel to Replit on November 8, 2025. The application is now running natively on Replit with full compatibility.

**NEW: Intelligent Plan Mode** - SuperAgent now features an intelligent, conversational planning mode that acts like a smart consultant. Before building, it asks clarifying questions, makes intelligent suggestions, proposes enhancements, and creates comprehensive project plans with 5-7 recommended features. This ensures users build better applications by thinking through requirements first.

Key capabilities include an admin-only Auto App Builder for generating complete applications from descriptions or code, and integration with Runway ML for AI video generation.

## Recent Changes
### November 8, 2025 - Split-Screen Interactive Chat + Live Streaming Build Logs
- **Split-Screen Dual-Panel System:** Build panel now splits into two interactive sections
  - **Left Panel:** Build Logs streaming word-by-word like a live chat conversation
  - **Right Panel:** Interactive Chat - users can ask questions and get AI help while builds run
  - Dual-panel grid layout with responsive design and purple gradient styling
  - Both panels operate simultaneously without interfering with each other
- **Interactive Chat Feature:** Chat with AI assistant during builds
  - Real-time streaming responses using Gemini 2.0 Flash with `stream=True` API
  - Chat runs in threadpool (`asyncio.to_thread()`) to avoid blocking build process
  - Message bubbles with avatars, blinking cursor during streaming, auto-scroll
  - Purple gradient theme matching overall design
  - Ask questions about code, features, deployment, etc. while app builds
- **Live Streaming Build Logs:** Build logs stream with chat-like experience
  - Implemented `stream_log_message()` helper yielding text deltas with 15ms delays
  - Added `log-stream` event type with unique message IDs for incremental updates
  - Typing cursor animation (blinking purple cursor) during streaming
  - Auto-scroll to bottom as new text appears
  - Maintains backward compatibility with existing progress/error events
  - Architect-approved with no performance or security concerns

### November 8, 2025 - Labeled Controls & Video-to-App AI Analysis
- **Labeled Button Controls:** All control buttons now have visible text labels for better UX
  - Preview controls: "Refresh", "Open", "Mobile" labels below buttons with purple glow effects
  - Input controls: "File", "Video", "Voice" labels below each button
  - Improved accessibility with ARIA labels for screen readers
  - Hover animations enhance the purple gradient theme
- **Video-to-App Feature:** NEW 🎬 Video upload button enables AI to recreate apps from videos
  - Upload video files (MP4, WebM, MOV - max 100MB) or record screen/camera
  - Gemini 2.0 Flash analyzes video content: UI layout, interactions, components, user flow
  - AI generates app based on what it sees in the video plus user instructions
  - Secure implementation: UUID-based filenames prevent path traversal attacks
  - Full modal interface: upload/record options, live preview, instructions textarea
  - Backend endpoint `/api/v1/upload-video` with size limits and validation
- **Security Enhancements:** Video upload uses UUID filenames to prevent malicious path traversal

### November 8, 2025 - TOP-TIER AI Intelligence & World-Class App Generation
- **Migration Completed:** Successfully migrated the entire SuperAgent platform from Vercel to Replit
- **Port Configuration:** Updated `start.py` to bind to port 5000 (Replit requirement) instead of 8000
- **Build System Overhaul:** Completely rewrote streaming build endpoint to use Gemini AI and EnterpriseBuildSystem
  - Replaced OpenAI dependency with Gemini 2.0 Flash (using available GEMINI_API_KEY)
  - Implemented async queue for real-time progress streaming during 9-stage enterprise builds
  - Integrated with EnterpriseBuildSystem for production-ready applications (multi-file projects, dependency installation, testing, security scanning)
  - Added detailed step-by-step logging that streams to frontend in real-time
- **Intelligent No-Code Operation:** Platform now understands user intent without requiring technical knowledge
  - Smart keyword detection: recognizes 30+ visual/interactive terms (calculator, todo, game, quiz, dashboard, etc.)
  - Web-first defaults: ambiguous requests automatically build web apps instead of CLI/backend
  - Enhanced AI prompts: instructs Gemini to understand user intent and build what non-technical users expect
  - Context-aware generation: "create a calculator" → beautiful web calculator with buttons (not Python CLI)
- **Build Results Panel:** Complete preview system with live iframe for web apps
  - Fixed file size detection: reads actual disk files instead of in-memory data (shows correct KB/MB)
  - Fixed preview URL generation: scans actual project directory to detect HTML files
  - Intelligent preview: shows live iframe for web apps, run instructions for backend/Python apps
  - File browser, download ZIP, and deployment guide integrated
- **Environment Setup:** Installed Python 3.11, all project dependencies, and Playwright with system libraries
- **Workflow Configuration:** Set up FastAPI server to run automatically on port 5000 with webview output
- **AI Quality Revolution:** Completely redesigned AI prompts with comprehensive quality standards
  - Added 5-tier quality framework: Perfect UX, Professional Design, Responsive/Accessible, Advanced Features, Production Polish
  - Specific UX standards: proper symbols (÷ × − +), perfect spacing, intuitive layouts, clear labels
  - Professional design requirements: gradients, animations, shadows, contrast ratios, typography
  - Advanced features mandated: keyboard shortcuts, localStorage persistence, history, validation, error handling
  - Self-review checklist: AI must verify quality before generating code
  - Concrete examples: "Great vs Bad" to teach AI what excellence looks like
  - Result: Apps that are EXCEPTIONAL, not just functional - users say "WOW"
- **Status:** Server running successfully, build system operational with world-class AI intelligence

## User Preferences
- Platform should operate like a true no-code tool - users shouldn't need technical knowledge to build anything
- AI should be intelligent enough to understand user intent from plain language descriptions
- Visual/interactive requests should default to web apps with live previews, not command-line tools
- I prefer clear and concise explanations without technical jargon
- I like to be informed before major changes are made
- I expect the agent to prioritize secure and performant code
- I prefer an iterative development approach with regular updates on progress
- I want the agent to use the most efficient and relevant AI model for the task

## System Architecture
SuperAgent is built on a stateless FastAPI REST API backend using Python 3.11 and Uvicorn. It integrates Google Gemini AI (`gemini-2.0-flash`) for core code generation, complemented by a 2-Supervisor System that utilizes multiple AI providers (Gemini, Claude, OpenAI, Groq) for enhanced code verification and security scanning.

**UI/UX Decisions:**
The UI features a clean, minimal, and sophisticated aesthetic with a purple gradient professional theme, aiming for a premium user experience by eliminating cluttered toolbars. It includes a mobile-first Progressive Web App (PWA) design for on-the-go access and a comprehensive Memory Viewer for conversation history and insights.

**Technical Implementations & Feature Specifications:**
- **Core AI Capabilities:** Natural language processing for autonomous planning, multi-step execution, code generation, and a Tool-Calling System.
- **Enterprise Build System:** 9-stage enterprise-grade build process with automatic checkpoint creation, multi-file project generation, real dependency installation (pip/npm), automated testing (pytest), security scanning, code verification, and production outputs (Dockerfile, CI/CD, documentation). Takes 2-5 minutes but produces truly production-ready applications.
- **Code Quality & Reliability:** Features a 4-layer Hallucination Fixer, a 2-Supervisor System with a Supreme Agent, ML-based error prevention, a dedicated Code Review System with security scanning, and an Autonomous Self-Repair System.
- **Development Workflow Enhancements:** Includes Git integration, automated Pytest generation, documentation generation, a Refactoring Engine, advanced AI-driven debugging, and a Rollback System.
- **System Management:** Supports secure file operations, safe shell command execution, an Environment Manager, and deployment configuration tools.
- **Advanced Platform Tools:** Features an extensible Plugin System, Docker Sandboxed Execution, a Codebase Query Engine, Long-Term Memory (SQLite-based), and an Autonomous Planner.
- **User Interaction:** Offers an enhanced Voice Interface, a CLI Interface, and structured JSON logging.
- **Replit Agent Parity & Extensions:** Includes "Build Modes", App Testing with Playwright, Agents & Automations, Dynamic Intelligence, First-Party Connectors, a Visual Editor, and an **Intelligent Plan Mode** that asks clarifying questions, makes smart suggestions, and proposes 5-7 enhancement features before building.
- **User Management & Security:** Implements a PostgreSQL-backed user management system with Bcrypt hashing, session-based authentication, admin access controls, and a Cybersecurity AI for threat detection.
- **Project Management:** Supports project import/export via ZIP files with multi-language detection, production-ready scaffolding (Dockerfiles, CI/CD), and GitHub integration for one-click repository creation and pushes.
- **Multi-Platform Deployment:** Provides one-click deployment instructions and configurations for various cloud platforms like Railway, Render, Fly.io, and Replit.

## External Dependencies
- **AI Models:** Google Gemini AI (`gemini-2.0-flash`, `gemini-2.0-flash-thinking-exp`), OpenAI, Claude, Groq (`llama-3.1-70b-versatile`), Runway ML Gen-3 Alpha.
- **Database:** SQLite (for long-term memory), PostgreSQL (for user management).
- **Caching:** Redis (optional).
- **Browser Testing:** Playwright.
- **Bot Frameworks:** `slack-bolt`, `python-telegram-bot`.
- **Scheduling:** APScheduler.
- **Deployment Platforms:** Railway, Render, Fly.io, Koyeb, Replit (Vercel, Heroku, AWS, GCP are mentioned as deployment targets but not directly integrated dependencies within the codebase).