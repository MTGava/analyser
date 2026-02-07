# Analisador Grafite:Água - PWA

Sistema de análise de proporção de mistura grafite:água usando visão computacional.

## 🚀 Deploy no Render.com

1. Criar conta em [render.com](https://render.com)
2. New → Web Service
3. Conectar repositório Git
4. Configurar:
   - **Name:** grafite-analyzer
   - **Environment:** Python 3
   - **Build Command:** `pip install -r backend/requirements.txt && bash build.sh`
   - **Start Command:** `cd backend && uvicorn server:app --host 0.0.0.0 --port $PORT`
   - **Instance Type:** Free

## 📱 Funcionalidades

- ✅ Captura de foto via câmera
- ✅ Upload de imagem
- ✅ Análise automática de proporção
- ✅ Correção de iluminação por gabarito
- ✅ Categorização em 5 níveis
- ✅ Confiabilidade do resultado
- ✅ Funciona offline (PWA)

## 🔧 Desenvolvimento Local

```bash
# Backend
cd backend
pip3 install -r requirements.txt
python3 server.py

# Acesse: http://localhost:8000
```

## 📊 Performance

- Tempo de análise: ~0.1s por imagem
- Cache de features: 43 KB
- Precisão por categoria: 66.7%
