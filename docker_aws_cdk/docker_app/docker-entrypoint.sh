#!/bin/sh
set -e

if [ -n "$STREAMLIT_SECRETS" ]; then
  mkdir -p ~/.streamlit
  echo "$STREAMLIT_SECRETS" > ~/.streamlit/secrets.toml
fi

exec streamlit run streamlit_app.py --server.port=8501 --server.address=0.0.0.0
