import cv2
import numpy as np
from pathlib import Path
from typing import Tuple, Dict, List
from image_analyzer import MixtureAnalyzer

class EnhancedMixtureAnalyzer(MixtureAnalyzer):
    """
    Versão aprimorada com:
    1. Data Augmentation (5 → 25 amostras por proporção)
    2. Ensemble de Features (BGR + LAB + HSV)
    3. Multi-região com votação
    """
    
    def load_references(self):
        """Carrega referências COM data augmentation"""
        print("Carregando imagens de referência COM AUGMENTATION...")
        
        for ratio_dir in sorted(self.reference_dir.iterdir()):
            if not ratio_dir.is_dir():
                continue
            
            ratio = ratio_dir.name
            images = list(ratio_dir.glob("*.png")) + list(ratio_dir.glob("*.jpg"))
            
            if not images:
                continue
            
            # Carrega imagens originais
            original_features = []
            for img_path in images:
                image = cv2.imread(str(img_path))
                if image is None:
                    continue
                
                # Detecta e corrige por gabarito
                template_region = self.detect_template_region(image)
                corrected = self.correct_color_by_template(image, template_region)
                
                # Extrai features
                features = self.extract_features(corrected)
                original_features.append(features)
            
            # Data Augmentation: gera 4 variações de cada imagem original
            augmented_features = []
            for img_path in images:
                image = cv2.imread(str(img_path))
                if image is None:
                    continue
                
                # 4 variações por imagem
                variations = self._augment_image(image)
                
                for var_img in variations:
                    template_region = self.detect_template_region(var_img)
                    corrected = self.correct_color_by_template(var_img, template_region)
                    features = self.extract_features(corrected)
                    augmented_features.append(features)
            
            # Combina originais + augmentadas
            all_features = original_features + augmented_features
            
            if all_features:
                self.reference_features[ratio] = all_features
                print(f"  ✓ {ratio}: {len(original_features)} originais + {len(augmented_features)} augmentadas = {len(all_features)} total")
        
        print(f"\nTotal: {len(self.reference_features)} proporções carregadas")
    
    def _augment_image(self, image: np.ndarray) -> List[np.ndarray]:
        """
        Gera 4 variações da imagem para data augmentation
        - Variação 1: Brilho +10%
        - Variação 2: Brilho -10%
        - Variação 3: Contraste aumentado
        - Variação 4: Ruído gaussiano leve
        """
        variations = []
        
        # 1. Brilho aumentado (+10%)
        bright = cv2.convertScaleAbs(image, alpha=1.0, beta=25)
        variations.append(bright)
        
        # 2. Brilho reduzido (-10%)
        dark = cv2.convertScaleAbs(image, alpha=1.0, beta=-25)
        variations.append(dark)
        
        # 3. Contraste aumentado
        contrast = cv2.convertScaleAbs(image, alpha=1.15, beta=0)
        variations.append(contrast)
        
        # 4. Ruído gaussiano
        noise = np.random.normal(0, 3, image.shape).astype(np.uint8)
        noisy = cv2.add(image, noise)
        variations.append(noisy)
        
        return variations
    
    def extract_features(self, image: np.ndarray) -> Dict:
        """
        Extrai features APRIMORADAS:
        - BGR histograms (original)
        - LAB histograms (original)
        - HSV histograms (NOVO)
        - Estatísticas de cor (NOVO)
        """
        # Região de análise (parte inferior após gabarito)
        height = image.shape[0]
        analysis_region = image[int(height * 0.3):, :]
        
        features = {}
        
        # 1. BGR histograms (original)
        for i, color in enumerate(['b', 'g', 'r']):
            hist = cv2.calcHist([analysis_region], [i], None, [32], [0, 256])
            features[f'hist_{color}'] = cv2.normalize(hist, hist).flatten()
        
        # 2. LAB histograms (original)
        lab = cv2.cvtColor(analysis_region, cv2.COLOR_BGR2LAB)
        for i, component in enumerate(['l', 'a', 'b']):
            hist = cv2.calcHist([lab], [i], None, [32], [0, 256])
            features[f'hist_lab_{component}'] = cv2.normalize(hist, hist).flatten()
        
        # 3. HSV histograms (NOVO)
        hsv = cv2.cvtColor(analysis_region, cv2.COLOR_BGR2HSV)
        for i, component in enumerate(['h', 's', 'v']):
            ranges = [180, 256, 256][i]
            hist = cv2.calcHist([hsv], [i], None, [32], [0, ranges])
            features[f'hist_hsv_{component}'] = cv2.normalize(hist, hist).flatten()
        
        # 4. Estatísticas de cor (NOVO)
        features['mean_color'] = np.mean(analysis_region, axis=(0, 1))
        features['std_color'] = np.std(analysis_region, axis=(0, 1))
        
        return features
    
    def compare_features(self, features1: Dict, features2: Dict) -> float:
        """
        Compara features usando ENSEMBLE de métricas
        Combina BGR + LAB + HSV + estatísticas
        """
        similarities = []
        
        # Histogramas BGR
        for color in ['b', 'g', 'r']:
            sim = cv2.compareHist(
                features1[f'hist_{color}'],
                features2[f'hist_{color}'],
                cv2.HISTCMP_CORREL
            )
            similarities.append(sim * 0.25)  # Peso 25%
        
        # Histogramas LAB
        for component in ['l', 'a', 'b']:
            sim = cv2.compareHist(
                features1[f'hist_lab_{component}'],
                features2[f'hist_lab_{component}'],
                cv2.HISTCMP_CORREL
            )
            similarities.append(sim * 0.25)  # Peso 25%
        
        # Histogramas HSV
        for component in ['h', 's', 'v']:
            sim = cv2.compareHist(
                features1[f'hist_hsv_{component}'],
                features2[f'hist_hsv_{component}'],
                cv2.HISTCMP_CORREL
            )
            similarities.append(sim * 0.25)  # Peso 25%
        
        # Estatísticas de cor (distância euclidiana invertida)
        mean_dist = np.linalg.norm(features1['mean_color'] - features2['mean_color'])
        mean_sim = 1.0 / (1.0 + mean_dist / 100.0)  # Normaliza
        similarities.append(mean_sim * 0.25)  # Peso 25%
        
        return float(np.sum(similarities))
    
    def analyze_multi_region(self, image_path: str, auto_detect_template: bool = True) -> Dict:
        """
        Análise com MÚLTIPLAS REGIÕES e votação
        Analisa centro + 4 cantos para maior robustez
        """
        image = cv2.imread(image_path)
        if image is None:
            return {'error': 'Não foi possível carregar a imagem'}
        
        height, width = image.shape[:2]
        
        # Define 5 regiões: centro (2x peso) + 4 cantos (1x peso)
        regions = [
            ('centro', image, 2.0),  # Imagem completa com peso maior
            ('esq_sup', image[0:height//2, 0:width//2], 1.0),
            ('dir_sup', image[0:height//2, width//2:], 1.0),
            ('esq_inf', image[height//2:, 0:width//2], 1.0),
            ('dir_inf', image[height//2:, width//2:], 1.0),
        ]
        
        # Analisa cada região
        region_results = []
        
        for region_name, region_img, weight in regions:
            if region_img.size == 0:
                continue
            
            # Detecta gabarito e corrige cor
            template_region = self.detect_template_region(region_img)
            corrected = self.correct_color_by_template(region_img, template_region)
            
            # Extrai features
            test_features = self.extract_features(corrected)
            
            # Compara com referências
            matches = []
            for ratio, ref_features_list in self.reference_features.items():
                similarities = [
                    self.compare_features(test_features, ref_features)
                    for ref_features in ref_features_list
                ]
                avg_similarity = np.mean(similarities)
                matches.append((ratio, avg_similarity * weight))
            
            region_results.append(matches)
        
        # VOTAÇÃO: combina resultados de todas as regiões
        combined_scores = {}
        for matches in region_results:
            for ratio, score in matches:
                if ratio not in combined_scores:
                    combined_scores[ratio] = []
                combined_scores[ratio].append(score)
        
        # Média ponderada
        final_matches = [
            (ratio, np.mean(scores))
            for ratio, scores in combined_scores.items()
        ]
        final_matches.sort(key=lambda x: x[1], reverse=True)
        
        best_match = final_matches[0]
        
        return {
            'best_match': best_match[0],
            'confidence': float(best_match[1]),
            'all_matches': final_matches[:5],
            'regions_analyzed': len(region_results)
        }


if __name__ == '__main__':
    print("="*70)
    print("TESTE: ANALYZER APRIMORADO")
    print("="*70)
    print()
    
    analyzer = EnhancedMixtureAnalyzer()
    
    print("\n" + "="*70)
    print("Testando análise multi-região...")
    print("="*70)
    
    # Testa uma imagem de cada proporção
    test_cases = [
        ('images/1_6/IMG_0475.png', '1_6'),
        ('images/1_10/IMG_0498.png', '1_10'),
        ('images/1_3/IMG_0464.png', '1_3'),
    ]
    
    for img_path, expected in test_cases:
        result = analyzer.analyze_multi_region(img_path)
        correct = '✅' if result['best_match'] == expected else '❌'
        print(f"\n{correct} Esperado: {expected} | Detectado: {result['best_match']} | Confiança: {result['confidence']:.3f}")
        print(f"   Top 3: {result['all_matches'][:3]}")
