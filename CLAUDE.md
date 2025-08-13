# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PromptX is a web application for AI-powered prompt optimization. It consists of a FastAPI backend that uses OpenAI's API to iteratively improve prompts based on multiple evaluation criteria, and a React+TypeScript frontend with Tailwind CSS for the user interface.

## Architecture

### Backend (Python FastAPI)

- **app.py**: Main FastAPI application with REST endpoints for prompt improvement jobs
- **prompt_engine.py**: Core prompt optimization engine using OpenAI GPT models
- **models.py**: Pydantic models for request/response validation and job tracking
- Uses async job processing with in-memory storage for job status tracking
- Evaluates prompts on configurable criteria: relevance, coherence, simplicity, depth
- Iteratively improves prompts until consecutive improvements threshold is met

### Frontend (React + TypeScript)

- **App.tsx**: Main component handling prompt input, job submission, and result polling
- Uses Vite for build tooling and development server
- Tailwind CSS for styling with dark/light mode support
- Polls backend job status until completion

### Key Integration Points

- Frontend polls `/job/{job_id}` endpoint to track progress of async improvement jobs
- Backend expects `OPENAI_API_KEY` environment variable
- CORS configured for development ports (3000, 5173)

## Development Commands

### Backend Development

```bash
cd backend
pip install -r requirements.txt
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development

```bash
cd frontend
npm install
npm run dev        # Start development server on port 5173
npm run build      # Build for production
npm run lint       # Run ESLint
npm run preview    # Preview production build
```

### Docker Development

```bash
docker-compose up --build    # Start both services
# Backend: http://localhost:8000
# Frontend: http://localhost:3000
```

### Testing

```bash
cd backend
python -m pytest tests/     # Run backend tests
```

## Environment Configuration

### Required Environment Variables

- `OPENAI_API_KEY`: OpenAI API key for prompt evaluation and improvement
- `VITE_BACKEND_URL`: Frontend environment variable for backend API URL

### Docker Environment

- Backend runs on port 8000
- Frontend builds to static files served by nginx on port 80 (mapped to 3000)
- Set `OPENAI_API_KEY` in docker-compose.yml

## API Architecture

### Key Endpoints

- `POST /improve-prompt`: Start async prompt improvement job
- `GET /job/{job_id}`: Get job status and results
- `GET /jobs`: List all jobs
- `DELETE /job/{job_id}`: Delete job
- `GET /health`: Health check

### Job Processing Flow

1. Client submits prompt improvement request
2. Backend creates job with unique ID and starts background processing
3. PromptEngine iteratively scores and improves prompt using OpenAI API
4. Client polls job status until completion
5. Final improved prompt returned in job result

## Code Patterns

### Backend Patterns

- Use Pydantic models for all request/response validation
- Async/await pattern for OpenAI API calls and job processing
- Background tasks for long-running prompt improvement jobs
- Function tools pattern for structured OpenAI API responses

### Frontend Patterns

- Functional React components with hooks
- TypeScript for type safety
- Tailwind classes for styling
- Environment-based API URL configuration
- Polling pattern for async job status updates
