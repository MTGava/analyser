#!/usr/bin/env python3
"""
Simulador de API REST para PWA
Demonstra como seria a integração com frontend

Para uso futuro com FastAPI/Flask
"""

import json
import base64
from pathlib import Path
from test_categories import ImprovedMixtureAnalyzer
import cv2
import numpy as np

class PWAAPISimulator:
    """Simula API REST que será usada no PWA"""
    
    def __init__(self):
        self.analyzer = ImprovedMixtureAnalyzer()
        print("✓ API Simulator inicializada")
    
    def analyze_endpoint(self, image_path: str = None, image_base64: str = None) -> dict:
        """
        Simula endpoint POST /api/analyze
        
        Request:
            {
                "image": "base64_string" ou arquivo
            }
        
        Response:
            {
                "success": true,
                "result": {
                    "category": "ideal",
                    "category_name": "✓✓ IDEAL - Proporção perfeita",
                    "category_range": "1:6 a 1:7",
                    "confidence": 0.85,
                    "exact_ratio": "1:6",
                    "exact_confidence": 0.73
                },
                "timestamp": "2026-02-07T11:30:00"
            }
        """
        try:
            # Decodifica imagem se for base64
            if image_base64:
                img_bytes = base64.b64decode(image_base64)
                nparr = np.frombuffer(img_bytes, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                # Salva temporariamente
                temp_path = "/tmp/temp_analysis.png"
                cv2.imwrite(temp_path, img)
                image_path = temp_path
            
            # Analisa
            result = self.analyzer.analyze_with_category(image_path)
            
            # Formata resposta
            response = {
                "success": True,
                "result": {
                    "category": result['category'],
                    "category_name": result['category_name'],
                    "category_range": result['category_range'],
                    "confidence": round(result['category_confidence'], 2),
                    "exact_ratio": result['ratio_formatted'],
                    "exact_confidence": round(result['confidence'], 2),
                    "recommendation": self._get_recommendation(result['category']),
                    "color_indicator": self._get_color_indicator(result['category'])
                },
                "timestamp": "2026-02-07T11:30:00"
            }
            
            return response
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Erro ao processar imagem"
            }
    
    def _get_recommendation(self, category: str) -> str:
        """Retorna recomendação baseada na categoria"""
        recommendations = {
            'muito_concentrado': 'Adicione água gradualmente até atingir proporção ideal',
            'concentrado': 'Proporção aceitável, pode adicionar um pouco de água',
            'ideal': 'Perfeito! Mantenha esta proporção',
            'diluido': 'Proporção aceitável, pode adicionar um pouco de produto',
            'muito_diluido': 'Adicione produto gradualmente até atingir proporção ideal'
        }
        return recommendations.get(category, 'Análise inconclusiva')
    
    def _get_color_indicator(self, category: str) -> str:
        """Retorna cor do indicador para UI"""
        colors = {
            'muito_concentrado': '#FF6B6B',  # Vermelho
            'concentrado': '#4ECDC4',        # Azul-verde
            'ideal': '#95E1D3',              # Verde claro
            'diluido': '#4ECDC4',            # Azul-verde
            'muito_diluido': '#FFE66D'       # Amarelo
        }
        return colors.get(category, '#CCCCCC')
    
    def history_endpoint(self) -> dict:
        """
        Simula endpoint GET /api/history
        Retornaria histórico de análises do usuário
        """
        return {
            "success": True,
            "history": [
                {
                    "id": 1,
                    "timestamp": "2026-02-07T10:30:00",
                    "category": "ideal",
                    "confidence": 0.85,
                    "operator": "João Silva"
                },
                {
                    "id": 2,
                    "timestamp": "2026-02-07T09:15:00",
                    "category": "concentrado",
                    "confidence": 0.78,
                    "operator": "Maria Santos"
                }
            ],
            "total": 2
        }
    
    def stats_endpoint(self) -> dict:
        """
        Simula endpoint GET /api/stats
        Estatísticas de uso
        """
        return {
            "success": True,
            "stats": {
                "total_analyses": 150,
                "by_category": {
                    "muito_concentrado": 20,
                    "concentrado": 35,
                    "ideal": 60,
                    "diluido": 25,
                    "muito_diluido": 10
                },
                "avg_confidence": 0.75,
                "last_7_days": 45
            }
        }


def demo_api():
    """Demonstração da API"""
    print("\n" + "="*70)
    print("  SIMULADOR DE API REST - PWA GRAFITE:ÁGUA")
    print("="*70 + "\n")
    
    api = PWAAPISimulator()
    
    print("\n1️⃣  TESTE: Endpoint de Análise")
    print("-" * 70)
    
    # Testa com imagem real
    test_image = "images/1_6/IMG_0475.png"
    
    if Path(test_image).exists():
        print(f"📸 Analisando: {test_image}\n")
        
        response = api.analyze_endpoint(image_path=test_image)
        
        print("📤 Response JSON:")
        print(json.dumps(response, indent=2, ensure_ascii=False))
    
    print("\n\n2️⃣  TESTE: Endpoint de Histórico")
    print("-" * 70)
    response = api.history_endpoint()
    print("📤 Response JSON:")
    print(json.dumps(response, indent=2, ensure_ascii=False))
    
    print("\n\n3️⃣  TESTE: Endpoint de Estatísticas")
    print("-" * 70)
    response = api.stats_endpoint()
    print("📤 Response JSON:")
    print(json.dumps(response, indent=2, ensure_ascii=False))
    
    print("\n" + "="*70)
    print("💡 ESTRUTURA DA API PARA PWA")
    print("="*70)
    print("""
Endpoints Recomendados:

POST   /api/analyze       - Analisa imagem enviada
GET    /api/history       - Histórico de análises
GET    /api/stats         - Estatísticas de uso
POST   /api/feedback      - Feedback sobre análise
GET    /api/calibrate     - Dados de calibração

Frontend PWA:
- Camera API para captura
- IndexedDB para cache offline
- Service Worker para funcionamento offline
- Material UI ou similar para interface
- Chart.js para gráficos de estatísticas
    """)
    print()


if __name__ == "__main__":
    demo_api()
