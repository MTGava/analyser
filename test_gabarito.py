#!/usr/bin/env python3
"""
Script de debug para verificar detecção do gabarito
Testa se o sistema está capturando o gabarito correto ou confundindo com a mistura
"""

import cv2
import numpy as np
from pathlib import Path
from image_analyzer import MixtureAnalyzer

def test_template_detection():
    """Testa detecção do gabarito em cada proporção"""
    
    print("\n" + "="*70)
    print("TESTE DE DETECÇÃO DO GABARITO")
    print("="*70 + "\n")
    
    analyzer = MixtureAnalyzer()
    target_color = np.array([119, 119, 119])  # #777777
    
    # Testa uma imagem de cada proporção
    results = []
    
    for ratio_dir in sorted(Path("images").glob("1_*")):
        if not ratio_dir.is_dir():
            continue
        
        ratio = ratio_dir.name
        images = list(ratio_dir.glob("*.png"))
        
        if not images:
            continue
        
        # Testa primeira imagem
        test_img = images[0]
        
        print(f"\n📊 Testando {ratio.replace('_', ':')} - {test_img.name}")
        print("-" * 70)
        
        img = cv2.imread(str(test_img))
        if img is None:
            print("  ❌ Erro ao carregar imagem")
            continue
        
        # Detecta gabarito
        template_region = analyzer.detect_template_region(img)
        x, y, w, h = template_region
        
        # Extrai patch do gabarito
        template_patch = img[y:y+h, x:x+w]
        mean_color_bgr = cv2.mean(template_patch)[:3]
        mean_color_rgb = (mean_color_bgr[2], mean_color_bgr[1], mean_color_bgr[0])
        
        # Calcula diferença da cor esperada
        diff = np.abs(np.array(mean_color_rgb) - target_color)
        avg_diff = np.mean(diff)
        
        # Status
        if avg_diff < 30:
            status = "✅ BOM"
        elif avg_diff < 60:
            status = "⚠️  RAZOÁVEL"
        else:
            status = "❌ RUIM"
        
        print(f"  Posição: x={x}, y={y}, largura={w}, altura={h}")
        print(f"  Altura da imagem: {img.shape[0]}px")
        print(f"  Gabarito em: {(y/img.shape[0]*100):.1f}% da altura")
        print(f"  Cor detectada (RGB): {tuple(int(c) for c in mean_color_rgb)}")
        print(f"  Cor esperada (RGB):  (119, 119, 119)")
        print(f"  Diferença média: {avg_diff:.1f} {status}")
        
        # Cria imagem de debug
        debug_img = img.copy()
        
        # Marca gabarito (verde se bom, vermelho se ruim)
        color = (0, 255, 0) if avg_diff < 30 else (0, 165, 255) if avg_diff < 60 else (0, 0, 255)
        cv2.rectangle(debug_img, (x, y), (x+w, y+h), color, 3)
        cv2.putText(debug_img, "GABARITO", (x, y-10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        
        # Marca região de análise da mistura (ROI)
        roi_y = y + h + 10
        roi_h = img.shape[0] - roi_y
        cv2.rectangle(debug_img, (0, roi_y), (img.shape[1], img.shape[0]), 
                     (255, 0, 0), 2)
        cv2.putText(debug_img, "AREA DE ANALISE", (10, roi_y + 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
        
        # Mostra cor média do gabarito
        color_square = np.ones((60, 200, 3), dtype=np.uint8)
        color_square[:30] = mean_color_bgr  # Cor detectada
        color_square[30:] = (119, 119, 119)  # Cor esperada
        
        # Adiciona no canto da imagem
        debug_img[10:70, img.shape[1]-210:img.shape[1]-10] = color_square
        cv2.putText(debug_img, "Detectado", (img.shape[1]-200, 25), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(debug_img, "Esperado", (img.shape[1]-200, 55), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Salva
        output_path = f"debug_gabarito_{ratio}.png"
        cv2.imwrite(output_path, debug_img)
        print(f"  💾 Debug salvo em: {output_path}")
        
        results.append({
            'ratio': ratio,
            'diff': avg_diff,
            'status': status,
            'position_pct': y/img.shape[0]*100
        })
    
    # Resumo
    print("\n" + "="*70)
    print("RESUMO")
    print("="*70 + "\n")
    
    good = sum(1 for r in results if r['diff'] < 30)
    ok = sum(1 for r in results if 30 <= r['diff'] < 60)
    bad = sum(1 for r in results if r['diff'] >= 60)
    
    print(f"✅ Detecção BOA:      {good}/{len(results)}")
    print(f"⚠️  Detecção RAZOÁVEL: {ok}/{len(results)}")
    print(f"❌ Detecção RUIM:     {bad}/{len(results)}")
    
    if bad > 0:
        print("\n⚠️  PROBLEMA DETECTADO!")
        print("Algumas imagens têm gabarito mal detectado.")
        print("Verifique as imagens debug_gabarito_*.png")
        print("\nProporções com problema:")
        for r in results:
            if r['diff'] >= 60:
                print(f"  • {r['ratio']}: diferença de {r['diff']:.1f}")
    else:
        print("\n✅ Todos os gabaritos foram detectados corretamente!")
    
    # Verifica posição
    print("\n📍 Posição do Gabarito:")
    for r in results:
        pos = r['position_pct']
        if pos > 30:
            warning = " ⚠️  (muito baixo?)"
        else:
            warning = ""
        print(f"  {r['ratio']}: {pos:.1f}% da altura{warning}")
    
    print("\n💡 Dica: O gabarito deve estar nos primeiros 20% da imagem")
    print()


def test_single_image(image_path: str):
    """Testa detecção em uma imagem específica com mais detalhes"""
    
    print("\n" + "="*70)
    print(f"ANÁLISE DETALHADA: {image_path}")
    print("="*70 + "\n")
    
    analyzer = MixtureAnalyzer()
    
    img = cv2.imread(image_path)
    if img is None:
        print("❌ Erro ao carregar imagem")
        return
    
    # Info da imagem
    print(f"📐 Dimensões: {img.shape[1]}x{img.shape[0]}px")
    
    # Detecta gabarito
    template_region = analyzer.detect_template_region(img)
    x, y, w, h = template_region
    
    print(f"\n📍 Gabarito Detectado:")
    print(f"  Posição: ({x}, {y})")
    print(f"  Tamanho: {w}x{h}px")
    print(f"  Localização: {(y/img.shape[0]*100):.1f}% da altura")
    
    # Analisa cor do gabarito
    template_patch = img[y:y+h, x:x+w]
    mean_bgr = cv2.mean(template_patch)[:3]
    mean_rgb = (mean_bgr[2], mean_bgr[1], mean_bgr[0])
    std_bgr = np.std(template_patch, axis=(0,1))
    
    print(f"\n🎨 Análise de Cor do Gabarito:")
    print(f"  Cor média (RGB): {tuple(int(c) for c in mean_rgb)}")
    print(f"  Cor esperada:    (119, 119, 119)")
    print(f"  Variação (std):  {tuple(int(s) for s in std_bgr)}")
    
    diff = np.abs(np.array(mean_rgb) - np.array([119, 119, 119]))
    print(f"  Diferença:       {tuple(int(d) for d in diff)}")
    print(f"  Diferença média: {np.mean(diff):.1f}")
    
    # Analisa região da mistura
    roi_y = y + h + 10
    roi = img[roi_y:, :]
    mean_roi_bgr = cv2.mean(roi)[:3]
    mean_roi_rgb = (mean_roi_bgr[2], mean_roi_bgr[1], mean_roi_bgr[0])
    
    print(f"\n🔬 Análise da Região da Mistura:")
    print(f"  Início: y={roi_y} ({(roi_y/img.shape[0]*100):.1f}% da altura)")
    print(f"  Tamanho: {roi.shape[1]}x{roi.shape[0]}px")
    print(f"  Cor média (RGB): {tuple(int(c) for c in mean_roi_rgb)}")
    
    # Verifica se são muito diferentes
    color_diff = np.abs(np.array(mean_rgb) - np.array(mean_roi_rgb))
    print(f"  Diferença gabarito vs mistura: {np.mean(color_diff):.1f}")
    
    if np.mean(color_diff) < 20:
        print("  ⚠️  AVISO: Gabarito e mistura têm cores muito similares!")
    
    # Cria visualização
    debug_img = img.copy()
    cv2.rectangle(debug_img, (x, y), (x+w, y+h), (0, 255, 0), 3)
    cv2.rectangle(debug_img, (0, roi_y), (img.shape[1], img.shape[0]), (255, 0, 0), 2)
    
    output = "debug_detailed.png"
    cv2.imwrite(output, debug_img)
    print(f"\n💾 Debug salvo em: {output}")
    print()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Testa imagem específica
        test_single_image(sys.argv[1])
    else:
        # Testa todas as proporções
        test_template_detection()
