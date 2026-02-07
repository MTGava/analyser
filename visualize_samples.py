#!/usr/bin/env python3
"""
Visualizador de imagens de referência
Útil para validar a qualidade das amostras
"""

import cv2
import numpy as np
from pathlib import Path

def create_comparison_grid():
    """Cria uma grade visual com uma amostra de cada proporção"""
    
    print("Criando grade de comparação visual...")
    
    ratios = sorted([d.name for d in Path("images").glob("1_*") if d.is_dir()])
    
    samples = []
    labels = []
    
    for ratio in ratios:
        ratio_dir = Path("images") / ratio
        images = list(ratio_dir.glob("*.png"))
        
        if images:
            # Pega primeira imagem como amostra
            img = cv2.imread(str(images[0]))
            if img is not None:
                # Redimensiona para tamanho padrão
                h, w = img.shape[:2]
                target_h = 400
                target_w = int(w * (target_h / h))
                img_resized = cv2.resize(img, (target_w, target_h))
                
                # Adiciona label
                label = f"{ratio.replace('_', ':')}"
                cv2.putText(img_resized, label, (10, 40), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
                
                samples.append(img_resized)
                labels.append(ratio)
                print(f"  ✓ {label}")
    
    if not samples:
        print("❌ Nenhuma imagem encontrada!")
        return
    
    # Organiza em grid (5 colunas)
    cols = 5
    rows = (len(samples) + cols - 1) // cols
    
    # Padding entre imagens
    padding = 20
    
    # Tamanho da célula
    cell_h = samples[0].shape[0] + padding
    cell_w = samples[0].shape[1] + padding
    
    # Cria canvas branco
    grid_h = rows * cell_h + padding
    grid_w = cols * cell_w + padding
    grid = np.ones((grid_h, grid_w, 3), dtype=np.uint8) * 255
    
    # Preenche grid
    for idx, img in enumerate(samples):
        row = idx // cols
        col = idx % cols
        
        y = row * cell_h + padding
        x = col * cell_w + padding
        
        h, w = img.shape[:2]
        grid[y:y+h, x:x+w] = img
    
    # Adiciona título
    title_bar = np.ones((80, grid_w, 3), dtype=np.uint8) * 50
    cv2.putText(title_bar, "PROPORCOES DE REFERENCIA - GRAFITE:AGUA", 
               (20, 55), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)
    
    final = np.vstack([title_bar, grid])
    
    # Salva
    output_path = "reference_grid.png"
    cv2.imwrite(output_path, final)
    print(f"\n✅ Grade salva em: {output_path}")
    print(f"   Dimensões: {final.shape[1]}x{final.shape[0]}px")
    print(f"   Total de amostras: {len(samples)}")

def list_all_samples():
    """Lista todas as imagens por proporção"""
    print("\n" + "="*70)
    print("INVENTÁRIO DE AMOSTRAS")
    print("="*70 + "\n")
    
    ratios = sorted([d.name for d in Path("images").glob("1_*") if d.is_dir()])
    
    total = 0
    for ratio in ratios:
        ratio_dir = Path("images") / ratio
        images = list(ratio_dir.glob("*.png"))
        
        print(f"📊 Proporção {ratio.replace('_', ':')}: {len(images)} imagens")
        for img_path in images:
            size = img_path.stat().st_size / 1024  # KB
            print(f"   - {img_path.name} ({size:.1f} KB)")
        print()
        total += len(images)
    
    print(f"Total: {total} imagens de referência")

def analyze_sample_quality():
    """Analisa qualidade das amostras (iluminação, contraste)"""
    print("\n" + "="*70)
    print("ANÁLISE DE QUALIDADE DAS AMOSTRAS")
    print("="*70 + "\n")
    
    ratios = sorted([d.name for d in Path("images").glob("1_*") if d.is_dir()])
    
    for ratio in ratios:
        ratio_dir = Path("images") / ratio
        images = list(ratio_dir.glob("*.png"))
        
        print(f"📊 {ratio.replace('_', ':')}:")
        
        brightnesses = []
        contrasts = []
        
        for img_path in images:
            img = cv2.imread(str(img_path))
            if img is None:
                continue
            
            # Converte para grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Calcula brilho (média)
            brightness = np.mean(gray)
            brightnesses.append(brightness)
            
            # Calcula contraste (desvio padrão)
            contrast = np.std(gray)
            contrasts.append(contrast)
        
        if brightnesses:
            avg_brightness = np.mean(brightnesses)
            avg_contrast = np.mean(contrasts)
            std_brightness = np.std(brightnesses)
            
            print(f"   Brilho médio: {avg_brightness:.1f} (±{std_brightness:.1f})")
            print(f"   Contraste médio: {avg_contrast:.1f}")
            
            # Avalia qualidade
            if std_brightness > 20:
                print(f"   ⚠️  Alta variação de iluminação entre amostras")
            else:
                print(f"   ✓ Iluminação consistente")
        
        print()

if __name__ == "__main__":
    import sys
    
    print("\n" + "="*70)
    print("  VISUALIZADOR DE AMOSTRAS DE REFERÊNCIA")
    print("="*70)
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
    else:
        print("\nOpções:")
        print("  1. Criar grade visual de comparação")
        print("  2. Listar todas as amostras")
        print("  3. Analisar qualidade das amostras")
        print()
        cmd = input("Escolha (1-3): ").strip()
    
    if cmd == "1" or cmd == "grid":
        create_comparison_grid()
    elif cmd == "2" or cmd == "list":
        list_all_samples()
    elif cmd == "3" or cmd == "quality":
        analyze_sample_quality()
    else:
        print("\nExecutando todas as opções...\n")
        list_all_samples()
        analyze_sample_quality()
        create_comparison_grid()
    
    print()
