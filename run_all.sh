#!/bin/bash

# Start FastAPI backend
nohup uvicorn app.main:app --reload > backend.log 2>&1 &
BACK_PID=$!
echo "FastAPI backend started (PID $BACK_PID) at http://localhost:8000"

# Start Streamlit frontend
nohup PYTHONPATH=$(pwd) streamlit run app/presentation/streamlit_app/main.py > frontend.log 2>&1 &
FRONT_PID=$!
echo "Streamlit frontend started (PID $FRONT_PID) at http://localhost:8501"

echo "---"
echo "To stop both, run: kill $BACK_PID $FRONT_PID"
echo "Logs: backend.log, frontend.log" 