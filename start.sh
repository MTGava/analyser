#!/bin/bash

# Script de inicialização para Render
cd backend
uvicorn server:app --host 0.0.0.0 --port ${PORT:-8000}
