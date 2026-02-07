import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import cv2
import numpy as np
from datetime import datetime
from pathlib import Path
import tempfile
from test_categories import ImprovedMixtureAnalyzer

app = FastAPI(title="Analisador Grafite:Água API")

# CORS para desenvolvimento
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Analyzer será inicializado no startup
analyzer = None

# Serve frontend
frontend_dir = Path(__file__).parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")

@app.get("/")
async def root():
    """Serve o PWA"""
    frontend_file = frontend_dir / "index.html"
    if frontend_file.exists():
        return FileResponse(frontend_file)
    return {"message": "API rodando! Frontend em /static/"}

@app.on_event("startup")
async def startup():
    """Inicializa analyzer no startup"""
    global analyzer
    print("🚀 Inicializando analyzer...")
    analyzer = ImprovedMixtureAnalyzer(
        reference_dir=str(Path(__file__).parent.parent / "images")
    )
    print("✅ Analyzer pronto!\n")
    
    info = analyzer.get_cache_info()
    print(f"📦 Cache carregado:")
    print(f"   Imagens: {info.get('total_images', 'N/A')}")
    print(f"   Tamanho: {info.get('size_kb', 'N/A')} KB")
    print(f"   Criado: {info.get('created', 'N/A')}")
    print()

@app.post("/api/analyze")
async def analyze_mixture(image: UploadFile = File(...)):
    """
    Analisa proporção de mistura grafite:água
    """
    try:
        # Valida tipo de arquivo
        if not image.content_type.startswith('image/'):
            raise HTTPException(400, "Arquivo deve ser uma imagem")
        
        # Lê imagem
        contents = await image.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            raise HTTPException(400, "Não foi possível ler a imagem")
        
        # Salva temporariamente
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
            cv2.imwrite(tmp.name, img)
            temp_path = tmp.name
        
        try:
            # Analisa com categorias
            result = analyzer.analyze_with_category(temp_path)
            
            return {
                "success": True,
                "result": {
                    "category": result['category'],
                    "category_name": result['category_name'],
                    "category_range": result['category_range'],
                    "confidence": round(result['category_confidence'], 2),
                    "exact_ratio": result['ratio_formatted'],
                    "exact_confidence": round(result['confidence'], 2),
                    "recommendation": get_recommendation(result['category']),
                    "color": get_color(result['category']),
                    "icon": get_icon(result['category'])
                },
                "timestamp": datetime.now().isoformat()
            }
            
        finally:
            # Remove arquivo temporário
            try:
                os.unlink(temp_path)
            except:
                pass
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Erro ao analisar: {e}")
        raise HTTPException(500, f"Erro ao processar imagem: {str(e)}")

@app.get("/api/health")
async def health_check():
    """Health check"""
    return {
        "status": "ok",
        "analyzer": "ready",
        "cache_loaded": analyzer.get_cache_info()['exists']
    }

@app.get("/api/cache/info")
async def cache_info():
    """Informações do cache"""
    return analyzer.get_cache_info()

def get_recommendation(category: str) -> str:
    """Retorna recomendação baseada na categoria"""
    recommendations = {
        'muito_concentrado': 'Adicione água gradualmente até atingir a proporção ideal',
        'concentrado': 'Proporção aceitável, pode adicionar um pouco mais de água',
        'ideal': 'Perfeito! Mantenha esta proporção',
        'diluido': 'Proporção aceitável, pode adicionar um pouco mais de produto',
        'muito_diluido': 'Adicione produto gradualmente até atingir a proporção ideal'
    }
    return recommendations.get(category, 'Análise inconclusiva')

def get_color(category: str) -> str:
    """Retorna cor para o indicador"""
    colors = {
        'muito_concentrado': '#FF6B6B',
        'concentrado': '#4ECDC4',
        'ideal': '#51CF66',
        'diluido': '#4ECDC4',
        'muito_diluido': '#FFD43B'
    }
    return colors.get(category, '#868E96')

def get_icon(category: str) -> str:
    """Retorna emoji/icon"""
    icons = {
        'muito_concentrado': '⚠️',
        'concentrado': '✓',
        'ideal': '✓✓',
        'diluido': '✓',
        'muito_diluido': '⚠️'
    }
    return icons.get(category, '?')

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*70)
    print("🚀 Iniciando servidor...")
    print("="*70 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
