# SuperAgent - Complete Replit Agent Clone

## Overview
SuperAgent is a complete Replit Agent clone providing an autonomous development experience. It allows users to generate, manage, and deploy applications efficiently using natural language to produce production-ready code. The platform aims to enhance productivity and code quality through autonomous planning, multi-step execution, and comprehensive code generation, including an intelligent plan mode for comprehensive project planning and feature suggestions. Key capabilities include an admin-only Auto App Builder and integration with Runway ML for AI video generation.

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
SuperAgent is built on a stateless FastAPI REST API backend using Python 3.11 and Uvicorn. It integrates Google Gemini AI (`gemini-2.0-flash`) for core code generation, complemented by a 2-Supervisor System that utilizes multiple AI providers for enhanced code verification and security scanning.

**UI/UX Decisions:**
The UI features a clean, minimal, and sophisticated aesthetic with a purple gradient theme, aiming for a premium user experience. It includes a mobile-first Progressive Web App (PWA) design, a comprehensive Memory Viewer, split-screen interactive chat with live streaming build logs, and labeled button controls for improved accessibility and user experience.

**Technical Implementations & Feature Specifications:**
- **Core AI Capabilities:** Natural language processing for autonomous planning, multi-step execution, code generation, Tool-Calling System, and advanced-intent detection for sophisticated app generation. Features tiered guidance for different request complexities (Standard vs. Advanced).
- **Enterprise Build System:** A 9-stage build process with automatic checkpoint creation, multi-file project generation, real dependency installation, automated testing, security scanning, code verification, and production outputs (Dockerfile, CI/CD, documentation).
- **Code Quality & Reliability:** Features a 4-layer Hallucination Fixer, a 2-Supervisor System with a Supreme Agent, ML-based error prevention, a dedicated Code Review System with security scanning, and an Autonomous Self-Repair System. Includes a 5-tier quality framework for UX, design, responsiveness, features, and production polish.
- **Development Workflow Enhancements:** Git integration, automated Pytest and documentation generation, a Refactoring Engine, AI-driven debugging, and a Rollback System.
- **System Management:** Secure file operations, safe shell command execution, Environment Manager, and deployment configuration tools.
- **Advanced Platform Tools:** Extensible Plugin System, Docker Sandboxed Execution, Codebase Query Engine, Long-Term Memory (SQLite-based), and an Autonomous Planner.
- **User Interaction:** Enhanced Voice Interface, CLI Interface, structured JSON logging, and inline status messages.
- **Replit Agent Parity & Extensions:** Includes "Build Modes", App Testing with Playwright, Agents & Automations, Dynamic Intelligence, First-Party Connectors, a Visual Editor, and an **Intelligent Plan Mode** for clarifying questions and feature suggestions.
- **User Management & Security:** PostgreSQL-backed user management with Bcrypt hashing, session-based authentication, admin controls, and Cybersecurity AI. Secure video upload with UUID-based filenames to prevent path traversal.
- **Project Management:** Project import/export (ZIP), multi-language detection, production-ready scaffolding (Dockerfiles, CI/CD), and GitHub integration.
- **Multi-Platform Deployment:** One-click deployment instructions for platforms like Railway, Render, Fly.io, and Replit.
- **Video-to-App Feature:** Allows AI to analyze video content (UI, interactions, user flow) and generate applications based on the visual input and user instructions.

## External Dependencies
- **AI Models:** Google Gemini AI (`gemini-2.0-flash`, `gemini-2.0-flash-thinking-exp`), OpenAI, Claude, Groq (`llama-3.1-70b-versatile`), Runway ML Gen-3 Alpha.
- **Database:** SQLite (for long-term memory), PostgreSQL (for user management).
- **Caching:** Redis (optional).
- **Browser Testing:** Playwright.
- **Bot Frameworks:** `slack-bolt`, `python-telegram-bot`.
- **Scheduling:** APScheduler.
- **Deployment Platforms:** Railway, Render, Fly.io, Koyeb, Replit.