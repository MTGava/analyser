import cv2
import numpy as np
from pathlib import Path
from typing import Tuple, Dict, List
from image_analyzer import MixtureAnalyzer

class SmartMixtureAnalyzer(MixtureAnalyzer):
    """
    Versão inteligente com:
    1. Weighted voting por vizinhança (proporções próximas)
    2. Análise de consistência das 5 amostras
    3. Rejeição de outliers
    """
    
    def __init__(self, reference_dir: str = "images"):
        super().__init__(reference_dir)
        self.ratio_order = sorted(self.reference_features.keys(), 
                                  key=lambda x: int(x.split('_')[1]))
    
    def get_neighbor_weight(self, ratio1: str, ratio2: str) -> float:
        """
        Calcula peso baseado na distância entre proporções
        Proporções vizinhas recebem peso maior
        
        1:5 comparando com 1:4 = peso 0.5
        1:5 comparando com 1:6 = peso 0.5
        1:5 comparando com 1:3 = peso 0.2
        1:5 comparando com 1:10 = peso 0.0
        """
        num1 = int(ratio1.split('_')[1])
        num2 = int(ratio2.split('_')[1])
        distance = abs(num1 - num2)
        
        if distance == 0:
            return 1.0  # Mesma proporção
        elif distance == 1:
            return 0.5  # Vizinho direto
        elif distance == 2:
            return 0.2  # Vizinho de 2º grau
        else:
            return 0.0  # Muito distante
    
    def analyze_with_confidence(self, test_features: Dict, ref_features_list: List[Dict]) -> Tuple[float, float]:
        """
        Analisa features COM medida de consistência
        
        Returns:
            (similarity, consistency) - consistência indica confiabilidade
        """
        similarities = [
            self.compare_features(test_features, ref_feat)
            for ref_feat in ref_features_list
        ]
        
        # Remove outliers (valores muito distantes da média)
        mean_sim = np.mean(similarities)
        std_sim = np.std(similarities)
        
        # Filtra valores dentro de 2 desvios padrão
        filtered_sims = [
            s for s in similarities 
            if abs(s - mean_sim) <= 2 * std_sim
        ]
        
        if not filtered_sims:
            filtered_sims = similarities
        
        # Consistência = inverso do desvio padrão (menor variação = mais confiável)
        consistency = 1.0 / (1.0 + np.std(filtered_sims))
        
        return float(np.mean(filtered_sims)), float(consistency)
    
    def analyze(self, image_path: str, auto_detect_template: bool = True) -> Dict:
        """
        Análise INTELIGENTE com weighted voting e consistência
        """
        # Carrega e processa imagem
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Não foi possível carregar a imagem: {image_path}")
        
        if auto_detect_template:
            template_region = self.detect_template_region(img)
        else:
            height, width = img.shape[:2]
            template_region = (int(width * 0.2), 10, int(width * 0.6), 50)
        
        test_features = self.extract_features(img, template_region)
        
        # Calcula similaridade E consistência para cada proporção
        ratio_scores = {}
        
        for ratio, ref_features_list in self.reference_features.items():
            similarity, consistency = self.analyze_with_confidence(test_features, ref_features_list)
            ratio_scores[ratio] = {
                'similarity': similarity,
                'consistency': consistency,
                'weighted_score': similarity * consistency  # Penaliza inconsistentes
            }
        
        # WEIGHTED VOTING: adiciona contribuição dos vizinhos
        final_scores = {}
        
        for ratio in ratio_scores:
            base_score = ratio_scores[ratio]['weighted_score']
            neighbor_contribution = 0.0
            
            # Adiciona contribuição ponderada dos vizinhos
            for other_ratio in ratio_scores:
                if ratio != other_ratio:
                    neighbor_weight = self.get_neighbor_weight(ratio, other_ratio)
                    if neighbor_weight > 0:
                        neighbor_contribution += ratio_scores[other_ratio]['similarity'] * neighbor_weight
            
            # Score final = 70% próprio + 30% vizinhos
            final_scores[ratio] = base_score * 0.7 + neighbor_contribution * 0.3
        
        # Ordena por score final
        sorted_matches = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)
        
        best_ratio = sorted_matches[0][0]
        best_score = sorted_matches[0][1]
        
        # Confiança ajustada pela consistência
        confidence = ratio_scores[best_ratio]['weighted_score']
        consistency = ratio_scores[best_ratio]['consistency']
        
        return {
            'ratio': best_ratio,
            'best_match': best_ratio,  # Para compatibilidade com compare_accuracy.py
            'confidence': float(confidence),
            'consistency': float(consistency),
            'ratio_formatted': best_ratio.replace('_', ':'),
            'all_matches': [(r, float(final_scores[r])) for r, _ in sorted_matches[:5]],
            'raw_similarities': [(r, float(ratio_scores[r]['similarity'])) for r in sorted([k for k in ratio_scores.keys()], key=lambda x: ratio_scores[x]['similarity'], reverse=True)[:3]],
            'template_region': template_region
        }


if __name__ == '__main__':
    print("="*70)
    print("TESTE: ANALYZER INTELIGENTE")
    print("="*70)
    print()
    
    analyzer = SmartMixtureAnalyzer()
    
    print("Características:")
    print("  ✓ Weighted voting por vizinhança")
    print("  ✓ Análise de consistência das 5 amostras")
    print("  ✓ Rejeição automática de outliers")
    print()
    
    # Testa alguns casos
    test_cases = [
        ('images/1_6/IMG_0475.png', '1_6'),
        ('images/1_10/IMG_0498.png', '1_10'),
        ('images/1_3/IMG_0464.png', '1_3'),
        ('images/1_7/IMG_0484.png', '1_7'),
    ]
    
    print("="*70)
    print("Exemplos de análise:")
    print("="*70)
    
    for img_path, expected in test_cases:
        result = analyzer.analyze(img_path)
        correct = '✅' if result['ratio'] == expected else '❌'
        
        print(f"\n{correct} Arquivo: {Path(img_path).name}")
        print(f"   Esperado:    {expected}")
        print(f"   Detectado:   {result['ratio']}")
        print(f"   Confiança:   {result['confidence']:.3f}")
        print(f"   Consistência: {result['consistency']:.3f}")
        print(f"   Top 3: {[(r, f'{s:.3f}') for r, s in result['all_matches'][:3]]}")
