import cv2
import numpy as np
from pathlib import Path
from typing import Tuple, Dict, List
from image_analyzer import MixtureAnalyzer

class ImprovedMixtureAnalyzer(MixtureAnalyzer):
    """
    Versão melhorada que agrupa proporções similares em categorias práticas
    """
    
    def __init__(self, reference_dir: str = "images"):
        super().__init__(reference_dir)
        
        # Define categorias práticas de proporção
        # Baseado nas proporções 1:5 a 1:7 que você mencionou serem as ideais
        self.categories = {
            'muito_concentrado': ['1_1', '1_2', '1_3'],  # Muito produto
            'concentrado': ['1_4', '1_5'],                # OK - Concentrado
            'ideal': ['1_6', '1_7'],                      # IDEAL
            'diluido': ['1_8', '1_9', '1_10'],           # OK - Diluído
            'muito_diluido': ['1_11', '1_12', '1_13', '1_14', '1_15']  # Muito água
        }
        
        self.category_names = {
            'muito_concentrado': '⚠️ MUITO CONCENTRADO - Adicionar água',
            'concentrado': '✓ BOM - Levemente concentrado',
            'ideal': '✓✓ IDEAL - Proporção perfeita',
            'diluido': '✓ BOM - Levemente diluído',
            'muito_diluido': '⚠️ MUITO DILUÍDO - Adicionar produto'
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
        Analisa imagem e retorna categoria prática além da proporção exata
        """
        # Análise básica
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


def test_with_categories():
    """Testa sistema com categorias"""
    print("="*70)
    print("TESTE COM CATEGORIAS DE PROPORÇÃO")
    print("="*70)
    print()
    
    analyzer = ImprovedMixtureAnalyzer()
    
    results = {
        'correct_exact': 0,
        'correct_category': 0,
        'total': 0,
        'by_category': {}
    }
    
    for ratio_dir in sorted(Path("images").glob("1_*")):
        if not ratio_dir.is_dir():
            continue
        
        ratio = ratio_dir.name
        expected_category = analyzer.get_ratio_category(ratio)
        
        if expected_category not in results['by_category']:
            results['by_category'][expected_category] = {
                'correct': 0, 'total': 0
            }
        
        images = list(ratio_dir.glob("*.png"))
        
        print(f"\n📊 Testando {ratio.replace('_', ':')} (Categoria: {expected_category}):")
        print("-" * 70)
        
        for test_img_path in images[:2]:
            try:
                result = analyzer.analyze_with_category(str(test_img_path))
                
                is_correct_exact = result['ratio'] == ratio
                is_correct_category = result['category'] == expected_category
                
                results['total'] += 1
                results['by_category'][expected_category]['total'] += 1
                
                if is_correct_exact:
                    results['correct_exact'] += 1
                    
                if is_correct_category:
                    results['correct_category'] += 1
                    results['by_category'][expected_category]['correct'] += 1
                
                status_exact = "✓" if is_correct_exact else "✗"
                status_cat = "✓" if is_correct_category else "✗"
                
                print(f"  {test_img_path.name}:")
                print(f"    Exata: {status_exact} {result['ratio_formatted']} ({result['confidence']:.1%})")
                print(f"    Categ: {status_cat} {result['category']} ({result['category_confidence']:.1%})")
                print(f"    → {result['category_name']}")
                
            except Exception as e:
                print(f"  {test_img_path.name}: ERRO - {e}")
    
    # Relatório
    print("\n" + "="*70)
    print("RELATÓRIO FINAL")
    print("="*70)
    
    exact_acc = (results['correct_exact'] / results['total'] * 100) if results['total'] > 0 else 0
    category_acc = (results['correct_category'] / results['total'] * 100) if results['total'] > 0 else 0
    
    print(f"\n📈 Precisão Exata: {exact_acc:.1f}% ({results['correct_exact']}/{results['total']})")
    print(f"📈 Precisão por Categoria: {category_acc:.1f}% ({results['correct_category']}/{results['total']})")
    
    print(f"\n📋 Precisão por Categoria:")
    for cat in ['muito_concentrado', 'concentrado', 'ideal', 'diluido', 'muito_diluido']:
        if cat in results['by_category']:
            stats = results['by_category'][cat]
            acc = (stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0
            print(f"  {cat:20s}: {acc:5.1f}% ({stats['correct']}/{stats['total']})")
    
    print("\n" + "="*70)
    print("ANÁLISE DE VIABILIDADE")
    print("="*70)
    
    if category_acc >= 70:
        print("\n✅ VIÁVEL com categorias!")
        print(f"   A precisão por categoria ({category_acc:.1f}%) é suficiente para uso prático")
        print("   Recomendação: Desenvolver PWA com sistema de categorias")
    elif category_acc >= 50:
        print("\n⚠️  PARCIALMENTE VIÁVEL")
        print(f"   Precisão de {category_acc:.1f}% pode funcionar com ajustes")
        print("   Recomendação: Coletar mais amostras ou simplificar categorias")
    else:
        print("\n❌ NECESSITA MELHORIAS")
        print("   Recomendação: Revisar abordagem ou hardware de captura")
    
    print()


if __name__ == "__main__":
    test_with_categories()
