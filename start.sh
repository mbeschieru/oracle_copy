#!/usr/bin/env bash

# --- 1. Verificare tmux ---
echo "🔍 Verific dacă tmux este instalat..."
if ! command -v tmux &> /dev/null; then
  echo "⚠️  tmux nu este găsit. Îl voi instala acum..."
  sudo apt-get update
  sudo apt-get install tmux -y
  if [ $? -ne 0 ]; then
    echo "❌ Eroare la instalarea tmux. Te rog verifică conexiunea la internet și permisiunile sudo."
    exit 1
  fi
  echo "✅ tmux a fost instalat cu succes."
else
  echo "✅ tmux este deja instalat."
fi

# --- 2. Activare virtualenv ---
echo "🐍 Activez mediul virtual..."
source venv/bin/activate
if [ $? -ne 0 ]; then
  echo "❌ Nu am putut activa mediul virtual. Te rog verifică calea către venv/bin/activate."
  exit 1
fi
echo "✅ Mediul virtual activat."

# --- 3. Pornire sesiune tmux ---
SESSION="dev-session"
echo "📦 Pornesc sesiunea tmux \"$SESSION\"..."
# Dacă există deja, o distrugem ca să pornim de la zero
tmux has-session -t $SESSION 2>/dev/null
if [ $? -eq 0 ]; then
  echo "♻️  Sesiunea '$SESSION' există deja. O închid și o repornesc..."
  tmux kill-session -t $SESSION
fi

tmux new-session -d -s $SESSION

# Panoul 1: Streamlit
echo "▶️  Deschid panoul Streamlit..."
tmux send-keys -t $SESSION \
  "cd $(pwd) && PYTHONPATH=$(pwd) streamlit run app/presentation/streamlit_app/main.py" C-m

# Panoul 2: Uvicorn
echo "▶️  Împarte ecranul și deschid panoul Uvicorn..."
tmux split-window -h -t $SESSION
tmux send-keys -t $SESSION \
  "cd $(pwd) && uvicorn app.main:app --reload" C-m

# 4. Atașare sesiune
echo "🔗 Te atașez la sesiunea tmux. Pentru a ieși apăsați Ctrl-b d"
tmux attach -t $SESSION
