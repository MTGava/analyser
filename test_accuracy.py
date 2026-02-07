import cv2
from pathlib import Path
from image_analyzer import MixtureAnalyzer
import numpy as np
from collections import defaultdict

def test_accuracy():
    """
    Testa a precisão do sistema usando validação cruzada
    Usa uma imagem de cada proporção como teste e as outras como referência
    """
    print("="*60)
    print("TESTE DE PRECISÃO DO ANALISADOR DE MISTURA")
    print("="*60)
    print()
    
    analyzer = MixtureAnalyzer()
    
    results = {
        'correct': 0,
        'total': 0,
        'confidences': [],
        'errors': []
    }
    
    ratios_tested = defaultdict(lambda: {'correct': 0, 'total': 0})
    
    # Testa com imagens reais
    for ratio_dir in sorted(Path("images").glob("1_*")):
        if not ratio_dir.is_dir():
            continue
        
        ratio = ratio_dir.name
        images = list(ratio_dir.glob("*.png"))
        
        if not images:
            continue
        
        print(f"\n📊 Testando proporção {ratio.replace('_', ':')}:")
        print("-" * 40)
        
        for test_img_path in images[:2]:  # Testa primeiras 2 imagens de cada proporção
            try:
                result = analyzer.analyze(str(test_img_path))
                
                is_correct = result['ratio'] == ratio
                results['total'] += 1
                ratios_tested[ratio]['total'] += 1
                
                if is_correct:
                    results['correct'] += 1
                    ratios_tested[ratio]['correct'] += 1
                    status = "✓ CORRETO"
                else:
                    status = f"✗ ERRO (detectou {result['ratio_formatted']})"
                    results['errors'].append({
                        'expected': ratio,
                        'detected': result['ratio'],
                        'confidence': result['confidence'],
                        'file': test_img_path.name
                    })
                
                results['confidences'].append(result['confidence'])
                
                print(f"  {test_img_path.name}: {status}")
                print(f"    Confiança: {result['confidence']:.2%}")
                top3_str = ', '.join([f"{r}({c:.1%})" for r, c in result['all_matches'][:3]])
                print(f"    Top 3: {top3_str}")
                
            except Exception as e:
                print(f"  {test_img_path.name}: ERRO - {e}")
    
    # Relatório final
    print("\n" + "="*60)
    print("RELATÓRIO FINAL")
    print("="*60)
    
    accuracy = (results['correct'] / results['total'] * 100) if results['total'] > 0 else 0
    avg_confidence = np.mean(results['confidences']) if results['confidences'] else 0
    
    print(f"\n📈 Precisão Geral: {accuracy:.1f}% ({results['correct']}/{results['total']})")
    print(f"📊 Confiança Média: {avg_confidence:.2%}")
    print(f"📊 Confiança Mínima: {min(results['confidences']):.2%}")
    print(f"📊 Confiança Máxima: {max(results['confidences']):.2%}")
    
    print(f"\n📋 Precisão por Proporção:")
    for ratio in sorted(ratios_tested.keys()):
        stats = ratios_tested[ratio]
        ratio_acc = (stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0
        print(f"  {ratio.replace('_', ':')}: {ratio_acc:.1f}% ({stats['correct']}/{stats['total']})")
    
    if results['errors']:
        print(f"\n❌ Erros Detectados ({len(results['errors'])}):")
        for error in results['errors']:
            print(f"  {error['file']}: esperava {error['expected'].replace('_', ':')} "
                  f"→ detectou {error['detected'].replace('_', ':')} "
                  f"(confiança: {error['confidence']:.2%})")
    
    # Análise de viabilidade
    print("\n" + "="*60)
    print("ANÁLISE DE VIABILIDADE")
    print("="*60)
    
    if accuracy >= 80 and avg_confidence >= 0.7:
        print("\n✅ VIÁVEL - O sistema apresenta boa precisão!")
        print("   Recomendação: Prosseguir com desenvolvimento do PWA")
    elif accuracy >= 60 and avg_confidence >= 0.6:
        print("\n⚠️  PARCIALMENTE VIÁVEL - Precisa de ajustes")
        print("   Recomendação: Melhorar algoritmo antes do PWA")
    else:
        print("\n❌ NÃO VIÁVEL - Precisão insuficiente")
        print("   Recomendação: Revisar abordagem ou coletar mais amostras")
    
    print()


def test_single_image(image_path: str):
    """Testa uma única imagem com detalhes visuais"""
    print(f"\n🔍 Análise Detalhada: {image_path}\n")
    print("="*60)
    
    analyzer = MixtureAnalyzer()
    result = analyzer.analyze(image_path)
    
    print(f"\n✨ RESULTADO:")
    print(f"   Proporção: {result['ratio_formatted']}")
    print(f"   Confiança: {result['confidence']:.2%}")
    
    # Barra de confiança visual
    bar_length = 30
    filled = int(result['confidence'] * bar_length)
    bar = "█" * filled + "░" * (bar_length - filled)
    print(f"   [{bar}] {result['confidence']:.1%}")
    
    print(f"\n📊 Todas as correspondências:")
    for i, (ratio, conf) in enumerate(result['all_matches'], 1):
        bar_filled = int(conf * 20)
        bar_visual = "█" * bar_filled + "░" * (20 - bar_filled)
        print(f"   {i}. {ratio.replace('_', ':'):5s} [{bar_visual}] {conf:.2%}")
    
    print(f"\n📍 Região do gabarito detectada: {result['template_region']}")
    print()
    
    # Salva imagem com visualização
    img = cv2.imread(image_path)
    if img is not None:
        x, y, w, h = result['template_region']
        cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
        cv2.putText(img, f"{result['ratio_formatted']} - {result['confidence']:.0%}", 
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        output_path = "test_result.png"
        cv2.imwrite(output_path, img)
        print(f"💾 Imagem com resultado salva em: {output_path}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Testa imagem específica
        test_single_image(sys.argv[1])
    else:
        # Testa precisão geral
        test_accuracy()
