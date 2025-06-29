# Chrome Extension Backend API

This is the backend API for the AI Permit Workflow Recording Chrome Extension.

## Purpose
- Receives workflow data from the Chrome extension
- Provides analytics and insights on recorded workflows  
- Offers AI-powered form field suggestions based on recorded data

## Deployment
This folder is designed for Railway.app deployment and contains only the necessary files:

- `app.py` - Entry point for Railway
- `production_backend.py` - Main Flask API
- `requirements.txt` - Python dependencies
- `Dockerfile` - Container configuration
- `railway.json` - Railway deployment settings

## Endpoints
- `GET /api/health` - Health check
- `POST /api/workflows/save` - Save workflow from extension
- `GET /api/workflows/analytics` - Get workflow analytics
- `POST /api/ai/suggestions` - Get AI form field suggestions

## Local Testing
```bash
python app.py
```

## Deploy to Railway
1. Connect this folder to Railway
2. Railway will automatically use the Dockerfile
3. Update the Chrome extension's serverUrl to the Railway app URL # Railway deployment trigger
