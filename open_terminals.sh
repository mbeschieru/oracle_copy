#!/usr/bin/env bash
set -e

# Deschide o fereastră nouă pentru FastAPI (uvicorn)
if command -v gnome-terminal &> /dev/null; then
  gnome-terminal --title="FastAPI Backend" -- bash -c "\
    echo '🚀 Pornire Uvicorn...'; \
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload; \
    exec bash"
elif command -v xterm &> /dev/null; then
  xterm -T "FastAPI Backend" -e "uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload; bash" &
else
  echo "❌ Nu am găsit gnome-terminal sau xterm. Rulează manual: uvicorn app.main:app"
fi

# Deschide o fereastră nouă pentru Streamlit
if command -v gnome-terminal &> /dev/null; then
  gnome-terminal --title="Streamlit Frontend" -- bash -c "\
    echo '🚀 Pornire Streamlit...'; \
    PYTHONPATH=$(pwd) streamlit run app/presentation/streamlit_app/main.py --server.address=0.0.0.0 --server.port=8501; \
    exec bash"
elif command -v xterm &> /dev/null; then
  xterm -T "Streamlit Frontend" -e "PYTHONPATH=$(pwd) streamlit run app/presentation/streamlit_app/main.py --server.address=0.0.0.0 --server.port=8501; bash" &
else
  echo "❌ Nu am găsit gnome-terminal sau xterm. Rulează manual: streamlit run app/presentation/streamlit_app/main.py"
fi
