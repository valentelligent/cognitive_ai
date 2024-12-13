# Cognitive AI Dashboard

Real-time visualization and analysis dashboard for cognitive metrics and patterns.

## Project Structure

```
dashboard/
├── backend/               # FastAPI backend server
│   ├── app/
│   │   ├── main.py       # Main application entry
│   │   ├── models.py     # Database models
│   │   └── database.py   # Database configuration
│   └── .env              # Environment configuration
├── frontend/             # React + TypeScript frontend
│   ├── src/
│   │   ├── App.tsx      # Main React component
│   │   └── main.tsx     # Frontend entry point
│   └── package.json     # Frontend dependencies
```

## Features

- Real-time metric tracking and visualization
- PostgreSQL database for persistent storage
- WebSocket connection for live updates
- Interactive charts using Recharts
- Responsive Tailwind CSS styling

## Prerequisites

- Python 3.11+
- Node.js and npm
- PostgreSQL 17
- Conda (for environment management)

## Setup Instructions

### Database Setup
1. Install PostgreSQL 17
2. Create database:
   ```sql
   CREATE DATABASE cognitive_metrics;
   ```
3. Configure .env file in backend/:
   ```
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=your_password
   POSTGRES_HOST=localhost
   POSTGRES_PORT=5432
   POSTGRES_DB=cognitive_metrics
   ```

### Backend Setup
1. Create conda environment:
   ```bash
   conda env create -f environment.yml
   ```
2. Activate environment:
   ```bash
   conda activate cognitive_dashboard
   ```
3. Start backend server:
   ```bash
   cd backend
   uvicorn app.main:app --reload --port 3000
   ```

### Frontend Setup
1. Install Node.js dependencies:
   ```bash
   cd frontend
   npm install
   ```
2. Start development server:
   ```bash
   npm run dev
   ```

## Accessing the Dashboard

1. Backend API: http://localhost:3000
2. Frontend Dashboard: http://localhost:5173

## Metrics Tracked

- **Acceleration Metrics**
  - Typing Speed
  - Error Recovery
  - Context Switching
  - Problem Solving

- **Pattern Recognition**
  - Recognition Speed
  - Integration Speed
  - Pattern Complexity

- **Growth Metrics**
  - Acceleration Trend
  - Learning Efficiency
  - Adaptability

- **Meta Patterns**
  - Learning Acceleration
  - Pattern Recognition Evolution
  - Integration Speed Changes
  - Adaptability Growth

## Technology Stack

- **Backend**
  - FastAPI
  - SQLAlchemy
  - PostgreSQL
  - WebSockets

- **Frontend**
  - React
  - TypeScript
  - Vite
  - Recharts
  - Tailwind CSS

## Development Status

 Basic Setup Complete
 Database Integration
 Real-time Updates
 Metric Visualization
 Ongoing Development
