# CareerGold: AI-Powered Job Discovery & Application Automation

## Project Overview
**CareerGold** is a high-performance system designed to automate the job search and application process. It combines advanced web scraping, AI-driven job analysis, and a modern frontend to help users find high-relevance job opportunities, specifically targeting those with high response potential (e.g., low applicant counts).

---

## Core Features

### 1. Intelligent Scraping Engine
*   **Dual-Layer Discovery**: Uses DuckDuckGo for free, unlimited job discovery and RapidAPI (LinkedIn Jobs) for detailed enrichment.
*   **Advanced Filtering**: 
    *   **Applicant Count**: Real-time filtering to target jobs with <50 applicants.
    *   **Recency**: Search by "Posted Within" (24h, Week, Month).
    *   **Location Intelligence**: Smart geographical filtering (e.g., strictly UK vs Worldwide).
*   **Auto-Cleaning**: Intelligence to skip closed or outdated postings (in development).

### 2. AI Analysis (Gemini Flash)
*   **Match Scoring**: Automatically compares job descriptions against user skills to provide a percentage match.
*   **Skill Extraction**: Extracts required skills and experience levels directly from job snippets.
*   **Program Classification**: Distinguishes between full-time roles, internships, and placement years (roadmap).

### 3. Modern Dashboard & UI
*   **Tech Stack**: Built with **React 18, TypeScript, and Material UI (M5)** following Material Design 3 principles.
*   **Quota Management**: Real-time tracking of RapidAPI usage limits directly in the UI.
*   **Interactive Scraper**: Visual progress bars and instant result cards for "Quick Search" discovery.

---

## Technical Architecture

### Frontend
- **Framework**: Vite + React + TypeScript
- **Styling**: Vanilla CSS + Material UI (M3 Gold/White theme)
- **State Management**: React Context + TanStack Query
- **Deployment**: Vercel

### Backend
- **API**: FastAPI (Python)
- **Scraper Orchestrator**: Coordinates discovery, parsing, and storage.
- **AI Integration**: Google Gemini Flash (Generative AI SDK)
- **Database/Auth**: Supabase (PostgreSQL)

---

## Directory Structure
```text
.
├── backend/                # FastAPI Application
│   ├── app/
│   │   ├── routers/        # API Endpoints (Scraper, Jobs, etc.)
│   │   └── scraper/        # Discovery, Parser, API Clients
│   └── .env                # Backend Secrets (Gemini/RapidAPI keys)
├── frontend/careergold/     # React Application
│   ├── src/
│   │   ├── components/     # UI Components (Cards, Layouts)
│   │   ├── pages/          # Page Views (Dashboard, Scraper, etc.)
│   │   └── theme/          # MUI Design Tokens
├── prompts/                # Shared prompt engineering files
└── PRD                     # Product Requirements Document
```

---

## Future Roadmap (Planned Features)
- [ ] **Program Selection**: Specific filters for Job vs Internship vs Placement Year.
- [ ] **Duration Tracking**: Extracting program length for internships/placements.
- [ ] **Enhanced Cleaning**: Automatic removal of "No longer accepting applications" listings.
- [ ] **Auto-Apply**: Generating custom CVs and automated submission flow.

---

## Getting Started

### Backend
1. `cd backend`
2. `venv\Scripts\activate` (Windows)
3. `pip install -r requirements.txt`
4. `uvicorn app.main:app --reload`

### Frontend
1. `cd frontend/careergold`
2. `npm install`
3. `npm run dev`
