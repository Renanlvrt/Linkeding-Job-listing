# CareerGold - AI Job Search Agent

A powerful job discovery and application tracking system with a FastAPI backend and a React/Vite/MUI frontend.

## 🚀 Getting Started

### 1. Prerequisites

- **Python 3.10+** (for the backend)
- **Node.js 18+** (for the frontend)
- **Supabase Account** (for database and authentication)

### 2. Environment Setup

Create a `.env` file in the project root based on the provided configuration:

- `SUPABASE_URL` and `SUPABASE_ANON_KEY` are required.
- `GEMINI_API_KEY` is required for job parsing features.
- `RAPIDAPI_KEY` is required for LinkedIn scraping.

---

## 🛠️ Running the Backend

The backend is built with FastAPI and handles job scraping, parsing, and database orchestration.

1. **Navigate to the backend folder:**

   ```bash
   cd backend
   ```

2. **Create and activate a virtual environment (optional but recommended):**

   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On Mac/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the server:**

   ```bash
   uvicorn app.main:app --reload
   ```

   The API will be available at `http://localhost:8000`. You can view the docs at `http://localhost:8000/docs`.

---

## 💻 Running the Frontend

The frontend is a modern React application built with Vite and Material UI.

1. **Navigate to the frontend folder:**

   ```bash
   cd frontend/careergold
   ```

2. **Install dependencies:**

   ```bash
   npm install
   ```

3. **Run the development server:**

   ```bash
   npm run dev
   ```

   The application will be available at `http://localhost:5173` (by default).

---

## 🏗️ Project Structure

- `backend/`: FastAPI application, scrapers, and database schema scripts.
- `frontend/careergold/`: React source code, components, and hooks.
- `research/`: Technical research and scraper documentation.
- `.env`: Shared environment configurations.
