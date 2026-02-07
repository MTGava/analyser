"""
Analyzer de produção: combina cache + categorias
"""
import numpy as np
from typing import Dict
from image_analyzer_cached import CachedMixtureAnalyzer

class ProductionMixtureAnalyzer(CachedMixtureAnalyzer):
    """
    Versão de produção que combina:
    - Cache de features (carregamento instantâneo)
    - Sistema de categorias (resultado prático)
    """
    
    def __init__(self, reference_dir: str = "images", cache_file: str = "features_cache.pkl"):
        super().__init__(reference_dir, cache_file)
        
        # Define categorias práticas
        self.categories = {
            'muito_concentrado': ['1_1', '1_2', '1_3'],
            'concentrado': ['1_4', '1_5'],
            'ideal': ['1_6', '1_7'],
            'diluido': ['1_8', '1_9', '1_10'],
            'muito_diluido': ['1_11', '1_12', '1_13', '1_14', '1_15']
        }
        
        self.category_names = {
            'muito_concentrado': '⚠️ MUITO CONCENTRADO',
            'concentrado': '✓ BOM - Concentrado',
            'ideal': '✓✓ IDEAL',
            'diluido': '✓ BOM - Diluído',
            'muito_diluido': '⚠️ MUITO DILUÍDO'
        }
        
        self.category_ranges = {
            'muito_concentrado': '1:1 a 1:3',
            'concentrado': '1:4 a 1:5',
            'ideal': '1:6 a 1:7',
            'diluido': '1:8 a 1:10',
            'muito_diluido': '1:11 a 1:15'
        }
    
    def get_ratio_category(self, ratio: str) -> str:
        """Retorna a categoria de uma proporção"""
        for category, ratios in self.categories.items():
            if ratio in ratios:
                return category
        return 'desconhecido'
    
    def analyze_with_category(self, image_path: str, auto_detect_template: bool = True) -> Dict:
        """
        Analisa imagem e retorna categoria + proporção exata
        """
        # Análise básica (usa cache)
        result = self.analyze(image_path, auto_detect_template)
        
        # Calcula confiança por categoria
        category_scores = {cat: [] for cat in self.categories.keys()}
        
        for ratio, similarity in result['all_matches']:
            category = self.get_ratio_category(ratio)
            if category in category_scores:
                category_scores[category].append(similarity)
        
        # Média de confiança por categoria
        category_confidences = {}
        for cat, scores in category_scores.items():
            if scores:
                category_confidences[cat] = np.mean(scores)
            else:
                category_confidences[cat] = 0.0
        
        # Melhor categoria
        best_category = max(category_confidences.items(), key=lambda x: x[1])
        
        # Enriquece resultado
        result['category'] = best_category[0]
        result['category_confidence'] = float(best_category[1])
        result['category_name'] = self.category_names[best_category[0]]
        result['category_range'] = self.category_ranges[best_category[0]]
        result['all_categories'] = sorted(category_confidences.items(), 
                                         key=lambda x: x[1], reverse=True)
        
        return result
