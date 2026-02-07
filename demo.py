#!/usr/bin/env python3
"""
Demo interativo do analisador de mistura grafite:água
"""

import sys
from pathlib import Path
from test_categories import ImprovedMixtureAnalyzer
import cv2

def print_header():
    print("\n" + "="*70)
    print("  ANALISADOR DE PROPORÇÃO GRAFITE:ÁGUA")
    print("  Sistema de Visão Computacional")
    print("="*70)

def analyze_image(analyzer, image_path):
    """Analisa e exibe resultado formatado"""
    try:
        result = analyzer.analyze_with_category(str(image_path))
        
        print(f"\n📸 Imagem: {Path(image_path).name}")
        print("-" * 70)
        
        # Proporção exata
        print(f"\n🔍 Proporção Detectada: {result['ratio_formatted']}")
        
        # Barra de confiança
        conf = result['confidence']
        bar_len = 40
        filled = int(conf * bar_len)
        bar = "█" * filled + "░" * (bar_len - filled)
        print(f"   Confiança: [{bar}] {conf:.1%}")
        
        # Categoria
        print(f"\n📊 Categoria: {result['category'].upper()}")
        print(f"   Faixa: {result['category_range']}")
        
        cat_conf = result['category_confidence']
        cat_filled = int(cat_conf * bar_len)
        cat_bar = "█" * cat_filled + "░" * (bar_len - cat_filled)
        print(f"   Confiança: [{cat_bar}] {cat_conf:.1%}")
        
        # Recomendação
        print(f"\n💡 Status: {result['category_name']}")
        
        # Top 3 proporções
        print(f"\n📈 Top 3 Proporções Similares:")
        for i, (ratio, sim) in enumerate(result['all_matches'][:3], 1):
            sim_filled = int(sim * 30)
            sim_bar = "█" * sim_filled + "░" * (30 - sim_filled)
            print(f"   {i}. {ratio.replace('_', ':'):5s} [{sim_bar}] {sim:.1%}")
        
        print()
        
        return result
        
    except Exception as e:
        print(f"\n❌ Erro ao analisar imagem: {e}")
        return None

def interactive_mode(analyzer):
    """Modo interativo para testar múltiplas imagens"""
    print("\n🎯 MODO INTERATIVO")
    print("Digite o caminho da imagem para analisar (ou 'sair' para encerrar)")
    
    while True:
        print("\n" + "-"*70)
        path = input("📂 Caminho da imagem: ").strip()
        
        if path.lower() in ['sair', 'exit', 'quit', '']:
            print("\n👋 Encerrando...\n")
            break
        
        if not Path(path).exists():
            print(f"❌ Arquivo não encontrado: {path}")
            continue
        
        analyze_image(analyzer, path)

def demo_samples(analyzer):
    """Demonstração com amostras de cada categoria"""
    print("\n📚 DEMONSTRAÇÃO - Análise de Amostras por Categoria")
    
    samples = {
        'muito_concentrado': 'images/1_1/IMG_0452.png',
        'concentrado': 'images/1_4/IMG_0467.png',
        'ideal': 'images/1_6/IMG_0475.png',
        'diluido': 'images/1_8/IMG_0488.png',
        'muito_diluido': 'images/1_13/IMG_0512.png'
    }
    
    for category, sample_path in samples.items():
        if Path(sample_path).exists():
            analyze_image(analyzer, sample_path)
            input("\n⏎ Pressione ENTER para próxima amostra...")

def main():
    print_header()
    
    # Inicializa analisador
    print("\n⚙️  Inicializando analisador...")
    analyzer = ImprovedMixtureAnalyzer()
    print("✓ Pronto!\n")
    
    # Menu
    while True:
        print("\n" + "="*70)
        print("MENU:")
        print("  1. Analisar imagem específica")
        print("  2. Modo interativo")
        print("  3. Demonstração com amostras")
        print("  4. Sair")
        print("="*70)
        
        choice = input("\nEscolha uma opção: ").strip()
        
        if choice == '1':
            if len(sys.argv) > 1:
                path = sys.argv[1]
            else:
                path = input("📂 Caminho da imagem: ").strip()
            
            if Path(path).exists():
                analyze_image(analyzer, path)
            else:
                print(f"❌ Arquivo não encontrado: {path}")
        
        elif choice == '2':
            interactive_mode(analyzer)
        
        elif choice == '3':
            demo_samples(analyzer)
        
        elif choice == '4':
            print("\n👋 Encerrando...\n")
            break
        
        else:
            print("❌ Opção inválida")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Interrompido pelo usuário\n")
    except Exception as e:
        print(f"\n❌ Erro: {e}\n")
