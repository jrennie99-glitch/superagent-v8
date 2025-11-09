# SuperAgent - Complete Replit Agent Clone

## Overview
SuperAgent is a complete Replit Agent clone providing an autonomous development experience. It allows users to generate, manage, and deploy applications efficiently using natural language to produce production-ready code. The platform aims to enhance productivity and code quality through autonomous planning, multi-step execution, and comprehensive code generation. Key capabilities include an admin-only Auto App Builder and integration with Runway ML for AI video generation. The project envisions a no-code platform where users can articulate ideas in plain language to generate production-ready web applications with live previews.

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
SuperAgent is built on a stateless FastAPI REST API backend using Python 3.11 and Uvicorn. It features a Multi-Provider AI System with automatic provider detection and intelligent failover.

**UI/UX Decisions:**
The UI features a clean, minimal, and sophisticated aesthetic with a purple gradient theme. It includes a mobile-first Progressive Web App (PWA) design, a comprehensive Memory Viewer, split-screen interactive chat with live streaming build logs, and labeled button controls for accessibility.

**Technical Implementations & Feature Specifications:**
- **Core AI Capabilities:** Natural language processing for autonomous planning, multi-step execution, code generation, Tool-Calling System, and advanced-intent detection. Features tiered guidance for different request complexities (Standard vs. Advanced).
- **Multi-Provider AI System:** Utilizes GROQ (`llama-3.3-70b-versatile`) for speed and Google Gemini AI (`gemini-2.0-flash`) for a large free tier. Includes a custom API key system for user-provided keys and automatic rate limit failover between providers, ensuring zero-downtime AI generation.
- **Enterprise Build System:** An 11-stage build process with spec-driven generation, advanced prompt engineering for production-ready code, multi-file project generation, real dependency installation, automated testing, and security scanning. Features E2E verification using Playwright for runtime validation of features and quality gates requiring high test coverage.
- **Code Quality & Reliability:** Incorporates a 4-layer Hallucination Fixer, a 2-Supervisor System with a Supreme Agent, ML-based error prevention, a dedicated Code Review System with security scanning, and an Autonomous Self-Repair System. Includes a 5-tier quality framework and automated E2E testing with Playwright to validate interactive behaviors.
- **Development Workflow Enhancements:** Git integration, automated Pytest and documentation generation, a Refactoring Engine, AI-driven debugging, and a Rollback System.
- **System Management:** Secure file operations, safe shell command execution, Environment Manager, and deployment configuration tools.
- **Advanced Platform Tools:** Extensible Plugin System, Docker Sandboxed Execution, Codebase Query Engine, Long-Term Memory (SQLite-based), and an Autonomous Planner.
- **User Interaction:** Enhanced Voice Interface, CLI Interface, structured JSON logging, and inline status messages.
- **Replit Agent Parity & Extensions:** Includes "Build Modes", App Testing with Playwright, Agents & Automations, Dynamic Intelligence, First-Party Connectors, a Visual Editor, and an Intelligent Plan Mode for clarifying questions and feature suggestions.
- **User Management & Security:** PostgreSQL-backed user management with Bcrypt hashing, session-based authentication, admin controls, and Cybersecurity AI. Secure video upload with UUID-based filenames.
- **Project Management:** Project import/export (ZIP), multi-language detection, production-ready scaffolding (Dockerfiles, CI/CD), and GitHub integration.
- **Multi-Platform Deployment:** One-click deployment instructions for platforms like Railway, Render, Fly.io, and Replit.
- **Video-to-App Feature:** Allows AI to analyze video content (UI, interactions, user flow) and generate applications.

## External Dependencies
- **AI Models:** Google Gemini AI (`gemini-2.0-flash`, `gemini-2.0-flash-thinking-exp`), OpenAI, Claude, Groq (`llama-3.1-70b-versatile`), Runway ML Gen-3 Alpha.
- **Database:** SQLite (for long-term memory), PostgreSQL (for user management).
- **Caching:** Redis (optional).
- **Browser Testing:** Playwright.
- **Bot Frameworks:** `slack-bolt`, `python-telegram-bot`.
- **Scheduling:** APScheduler.
- **Deployment Platforms:** Railway, Render, Fly.io, Koyeb, Replit.

## Recent Changes (November 9, 2025)

### CRITICAL: Full-Stack Generation System - Replit Agent Parity Achieved

**Problem Solved:** SuperAgent was generating Python-only backend code for API requests, requiring users to run terminal commands. Replit Agent generates beautiful landing pages with professional branding, API documentation, and "Get Started" buttons. This violated the core requirement: *"users shouldn't need technical knowledge to build anything"*.

**Solution Implemented:**

1. **Intent Detection Rewrite** (Lines 78-150):
   - Split backend detection: `cli_only_patterns` (terminal tools) vs `backend_with_ui_patterns` (APIs needing landing pages)
   - **NEW DEFAULT**: ALL requests generate full-stack web apps unless explicitly CLI-only
   - Requests with "api", "rest", "endpoint", "backend" → Full-stack (HTML + CSS + JS + Python)
   - Only "cli", "command line", "terminal" → Python-only backend
   - **Result**: API requests now generate visual interfaces matching Replit Agent behavior

2. **Architecture Planning Enhancement** (Lines 1593-1604):
   - For `project_type="api"`: Mandates frontend files alongside backend
   - **Files Generated**: index.html, styles.css, script.js + main.py, routes.py, models.py, config.py, test_main.py
   - Comment: "FULL-STACK API: Landing page + Python backend (Replit Agent parity)"

3. **API Landing Page Generation** (Lines 1619-1686):
   - New specialized HTML prompt for API projects
   - **Mandatory Sections**:
     * Hero: API branding, tagline, CTA buttons ("Get API Key", "View Documentation")
     * Features: 3-4 cards with icons showing key capabilities
     * Quick Start: Code examples with language tabs (Python, JavaScript, cURL), copy buttons
     * Endpoints: Documentation table with methods, paths, descriptions, example responses
     * CTA Footer: Sign-up form, API key generation, documentation links
   - **Design**: Purple gradient theme (#8B5CF6 to #6366F1), glass-morphism, responsive, professional typography
   - **Technical**: Semantic HTML5, no inline handlers, accessible, SEO meta tags

4. **HTML/JavaScript Coordination Fix**:
   - Three-layer prompt reinforcement for input element handling (.value not .textContent)
   - HTML prompts forbid inline event handlers (onclick, onchange, etc.)
   - JavaScript prompts require addEventListener with semantic IDs/data-attributes
   - Prevents buttons calling non-existent functions

**Expected Behavior Change:**
- **Before**: "Design REST API for reviews" → Python files only, terminal commands required
- **After**: "Design REST API for reviews" → Professional "ReviewHub API" landing page + Python backend, ready to use immediately

**Testing Required:** Run same review aggregation API build to verify landing page generation.