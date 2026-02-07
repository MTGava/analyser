#!/bin/bash

# Gera cache de features antes do deploy
echo "🔧 Gerando cache de features..."
cd /opt/render/project/src || cd .
python3 image_analyzer_cached.py

echo "✅ Cache gerado!"
echo "📦 Tamanho do cache:"
ls -lh features_cache.pkl

echo "✅ Build completo!"
