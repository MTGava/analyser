#!/usr/bin/env python3
"""
Compara acurácia entre versão atual e versão aprimorada
"""
import sys
from pathlib import Path
from test_categories import ImprovedMixtureAnalyzer
from image_analyzer_enhanced import EnhancedMixtureAnalyzer

def test_accuracy(analyzer, name, use_enhanced=False):
    """Testa acurácia em todas as 75 imagens"""
    print(f"\n{'='*70}")
    print(f"TESTANDO: {name}")
    print(f"{'='*70}\n")
    
    reference_dir = Path('images')
    
    exact_correct = 0
    category_correct = 0
    total = 0
    
    # Define categorias
    categories = {
        'muito_concentrado': ['1_1', '1_2', '1_3'],
        'concentrado': ['1_4', '1_5'],
        'ideal': ['1_6', '1_7'],
        'diluido': ['1_8', '1_9', '1_10'],
        'muito_diluido': ['1_11', '1_12', '1_13', '1_14', '1_15']
    }
    
    ratio_to_category = {}
    for cat, ratios in categories.items():
        for ratio in ratios:
            ratio_to_category[ratio] = cat
    
    results_by_proportion = {}
    
    for ratio_dir in sorted(reference_dir.iterdir()):
        if not ratio_dir.is_dir():
            continue
        
        ratio = ratio_dir.name
        images = list(ratio_dir.glob("*.png")) + list(ratio_dir.glob("*.jpg"))
        
        correct_exact = 0
        correct_category = 0
        
        for img_path in images:
            total += 1
            
            if use_enhanced:
                result = analyzer.analyze_multi_region(str(img_path))
                predicted = result['best_match']
            else:
                result = analyzer.analyze_with_category(str(img_path))
                predicted = result.get('best_match', result.get('ratio'))
            
            # Acurácia exata
            if predicted == ratio:
                exact_correct += 1
                correct_exact += 1
            
            # Acurácia por categoria
            expected_cat = ratio_to_category.get(ratio)
            predicted_cat = ratio_to_category.get(predicted)
            
            if expected_cat == predicted_cat:
                category_correct += 1
                correct_category += 1
        
        results_by_proportion[ratio] = {
            'exact': f"{correct_exact}/{len(images)}",
            'category': f"{correct_category}/{len(images)}"
        }
    
    # Resumo
    exact_pct = (exact_correct / total) * 100
    category_pct = (category_correct / total) * 100
    
    print(f"\n📊 Resultados por proporção:")
    print(f"{'Proporção':<12} {'Exato':<10} {'Categoria':<10}")
    print("-" * 35)
    for ratio in sorted(results_by_proportion.keys()):
        res = results_by_proportion[ratio]
        print(f"{ratio:<12} {res['exact']:<10} {res['category']:<10}")
    
    print(f"\n{'='*70}")
    print(f"RESUMO FINAL:")
    print(f"  Acurácia Exata:     {exact_correct}/{total} = {exact_pct:.1f}%")
    print(f"  Acurácia Categoria: {category_correct}/{total} = {category_pct:.1f}%")
    print(f"{'='*70}\n")
    
    return exact_pct, category_pct


if __name__ == '__main__':
    print("\n" + "="*70)
    print("COMPARAÇÃO DE ACURÁCIA: ATUAL vs APRIMORADO")
    print("="*70)
    
    # Versão atual
    print("\n🔵 Carregando versão ATUAL...")
    current_analyzer = ImprovedMixtureAnalyzer()
    current_exact, current_cat = test_accuracy(current_analyzer, "VERSÃO ATUAL", use_enhanced=False)
    
    # Versão aprimorada
    print("\n🟢 Carregando versão APRIMORADA...")
    enhanced_analyzer = EnhancedMixtureAnalyzer()
    enhanced_exact, enhanced_cat = test_accuracy(enhanced_analyzer, "VERSÃO APRIMORADA", use_enhanced=True)
    
    # Comparação final
    print("\n" + "="*70)
    print("📈 COMPARAÇÃO")
    print("="*70)
    print(f"\nAcurácia Exata:")
    print(f"  Atual:      {current_exact:.1f}%")
    print(f"  Aprimorada: {enhanced_exact:.1f}%")
    print(f"  Ganho:      {enhanced_exact - current_exact:+.1f}%")
    
    print(f"\nAcurácia por Categoria:")
    print(f"  Atual:      {current_cat:.1f}%")
    print(f"  Aprimorada: {enhanced_cat:.1f}%")
    print(f"  Ganho:      {enhanced_cat - current_cat:+.1f}%")
    
    print("\n" + "="*70)
    print("✨ MELHORIAS IMPLEMENTADAS:")
    print("  • Data Augmentation: 5 → 25 amostras por proporção")
    print("  • Ensemble Features: BGR + LAB + HSV + estatísticas")
    print("  • Análise Multi-região: 5 regiões com votação ponderada")
    print("="*70 + "\n")
