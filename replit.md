# SuperAgent - Complete Replit Agent Clone

## Overview
SuperAgent V9 is an autonomous AI software engineer that converts natural language descriptions into complete, production-ready, full-stack applications. It aims to generate bug-free applications with modern architecture, including Next.js 15, TypeScript, Tailwind CSS, shadcn/ui, Supabase, and Stripe integration, enabling rapid development and one-click deployment. The project's ambition is to provide a superior, zero-placeholder, automatically tested, and instantly deployable solution for application generation.

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
The UI features a clean, minimal, and sophisticated aesthetic with a purple gradient theme, incorporating a mobile-first Progressive Web App (PWA) design. Key UI components include a Memory Viewer, split-screen interactive chat with live streaming build logs, and labeled button controls for accessibility.

**Technical Implementations & Feature Specifications:**
- **Core AI Capabilities:** Natural language processing for autonomous planning, multi-step execution, code generation, Tool-Calling System, and advanced-intent detection, with tiered guidance for different request complexities.
- **Multi-Provider AI System:** Utilizes GROQ and Google Gemini AI, featuring a custom API key system and automatic rate limit failover for uninterrupted AI generation.
- **Enterprise Build System:** An 11-stage build process with spec-driven generation, advanced prompt engineering, multi-file project generation, real dependency installation, automated testing, security scanning, and E2E verification using Playwright.
- **Code Quality & Reliability:** Incorporates a 4-layer Hallucination Fixer, a 2-Supervisor System with a Supreme Agent, ML-based error prevention, a dedicated Code Review System with security scanning, and an Autonomous Self-Repair System, complemented by a 5-tier quality framework and automated E2E testing.
- **Development Workflow Enhancements:** Git integration, automated Pytest and documentation generation, a Refactoring Engine, AI-driven debugging, and a Rollback System.
- **System Management:** Secure file operations, safe shell command execution, Environment Manager, and deployment configuration tools.
- **Advanced Platform Tools:** Extensible Plugin System, Docker Sandboxed Execution, Codebase Query Engine, Long-Term Memory (SQLite-based), and an Autonomous Planner.
- **User Interaction:** Enhanced Voice Interface, CLI Interface, structured JSON logging, and inline status messages.
- **Replit Agent Parity & Extensions:** Includes "Build Modes", App Testing with Playwright, Agents & Automations, Dynamic Intelligence, First-Party Connectors, a Visual Editor, and an Intelligent Plan Mode for clarifying questions and feature suggestions.
- **User Management & Security:** PostgreSQL-backed user management with Bcrypt hashing, session-based authentication, admin controls, and Cybersecurity AI. Secure video upload with UUID-based filenames.
- **Project Management:** Project import/export (ZIP), multi-language detection, production-ready scaffolding (Dockerfiles, CI/CD), and GitHub integration.
- **Multi-Platform Deployment:** One-click deployment instructions for platforms like Railway, Render, Fly.io, and Replit.
- **Video-to-App Feature:** Allows AI to analyze video content (UI, interactions, user flow) and generate applications.
- **Full-Stack Generation:** Defaults to generating full-stack web applications (HTML + CSS + JS + Python) for API requests, with professional landing pages, and only generates Python-only backends for explicit CLI requests.
- **Design System Integration:** Employs explicit design systems and code templates for HTML, CSS, and JavaScript generation to ensure high visual quality, consistent branding, and responsive design. This includes specific color palettes, spacing systems, component styles (e.g., glass-morphism, gradient buttons), and animations.

## External Dependencies
- **AI Models:** Google Gemini AI (`gemini-2.0-flash`), OpenAI, Claude, Groq (`llama-3.1-70b-versatile`).
- **Database:** SQLite (for long-term memory), PostgreSQL (for user management).
- **Caching:** Redis (optional).
- **Browser Testing:** Playwright.
- **Bot Frameworks:** `slack-bolt`, `python-telegram-bot`.
- **Scheduling:** APScheduler.
- **Deployment Platforms:** Railway, Render, Fly.io, Koyeb, Replit.