import cv2
import numpy as np
from pathlib import Path
from typing import Tuple, Dict, List
import json

class MixtureAnalyzer:
    """Analisa proporção de mistura grafite:água baseado em imagens"""
    
    def __init__(self, reference_dir: str = "images"):
        self.reference_dir = Path(reference_dir)
        self.target_gray = (119, 119, 119)  # #777777 em RGB
        self.reference_features = {}
        self.load_references()
    
    def correct_color_by_template(self, image: np.ndarray, template_region: Tuple[int, int, int, int]) -> np.ndarray:
        """
        Corrige a iluminação da imagem baseado no gabarito #777777
        
        Args:
            image: Imagem BGR do OpenCV
            template_region: (x, y, width, height) do gabarito na imagem
        
        Returns:
            Imagem corrigida
        """
        x, y, w, h = template_region
        template_patch = image[y:y+h, x:x+w]
        
        # Calcula cor média do gabarito na foto
        mean_color = cv2.mean(template_patch)[:3]  # BGR
        
        # Converte #777777 para BGR
        target_bgr = (self.target_gray[2], self.target_gray[1], self.target_gray[0])
        
        # Calcula fator de correção para cada canal
        correction_factors = np.array([
            target_bgr[0] / (mean_color[0] + 1e-6),
            target_bgr[1] / (mean_color[1] + 1e-6),
            target_bgr[2] / (mean_color[2] + 1e-6)
        ])
        
        # Aplica correção
        corrected = image.astype(np.float32)
        corrected[:, :, 0] *= correction_factors[0]
        corrected[:, :, 1] *= correction_factors[1]
        corrected[:, :, 2] *= correction_factors[2]
        
        # Limita valores entre 0-255
        corrected = np.clip(corrected, 0, 255).astype(np.uint8)
        
        return corrected
    
    def detect_template_region(self, image: np.ndarray) -> Tuple[int, int, int, int]:
        """
        Detecta automaticamente a região do gabarito cinza na parte superior
        Busca especificamente o retângulo cinza #777777, não áreas brancas
        
        Returns:
            (x, y, width, height) do gabarito detectado
        """
        height, width = image.shape[:2]
        search_region = image[0:int(height * 0.25), :]
        
        # Converte para grayscale
        gray = cv2.cvtColor(search_region, cv2.COLOR_BGR2GRAY)
        
        # Detecta especificamente tons de cinza médio (#777777 = 119)
        # Range: 80-160 (exclui branco >200 e preto <50)
        lower_gray = 80
        upper_gray = 160
        mask = cv2.inRange(gray, lower_gray, upper_gray)
        
        # Remove ruído
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        
        # Encontra contornos
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            # Filtra contornos válidos (retangulares e grandes)
            valid_contours = []
            for contour in contours:
                area = cv2.contourArea(contour)
                if area < width * 20:  # Muito pequeno
                    continue
                
                x, y, w, h = cv2.boundingRect(contour)
                
                # Valida proporções (retângulo horizontal)
                aspect_ratio = w / (h + 1)
                if aspect_ratio < 2:  # Não é retângulo largo
                    continue
                
                # Valida tamanho mínimo
                if w < width * 0.3:  # Largura mínima 30% da imagem
                    continue
                
                # Valida cor média da região (deve ser cinza, não branco)
                region = search_region[y:y+h, x:x+w]
                mean_val = np.mean(region)
                if mean_val > 180 or mean_val < 70:  # Muito claro ou escuro
                    continue
                
                valid_contours.append((contour, area, x, y, w, h))
            
            if valid_contours:
                # Pega o maior contorno válido
                _, _, x, y, w, h = max(valid_contours, key=lambda c: c[1])
                return (x, y, w, h)
        
        # Fallback: assume gabarito no topo centralizado
        return (int(width * 0.05), 10, int(width * 0.9), 50)
    
    def extract_features(self, image: np.ndarray, template_region: Tuple[int, int, int, int]) -> Dict:
        """
        Extrai características da imagem para comparação
        """
        # Corrige iluminação
        corrected = self.correct_color_by_template(image, template_region)
        
        # Região de interesse (abaixo do gabarito)
        _, ty, _, th = template_region
        roi = corrected[ty + th + 10:, :]  # ROI começa após o gabarito
        
        # Calcula histograma de cores
        hist_b = cv2.calcHist([roi], [0], None, [32], [0, 256])
        hist_g = cv2.calcHist([roi], [1], None, [32], [0, 256])
        hist_r = cv2.calcHist([roi], [2], None, [32], [0, 256])
        
        # Normaliza histogramas
        hist_b = hist_b.flatten() / (hist_b.sum() + 1e-6)
        hist_g = hist_g.flatten() / (hist_g.sum() + 1e-6)
        hist_r = hist_r.flatten() / (hist_r.sum() + 1e-6)
        
        # Calcula estatísticas de cor
        mean_color = cv2.mean(roi)[:3]
        std_color = np.std(roi, axis=(0, 1))
        
        # Converte para LAB para análise de luminosidade
        lab = cv2.cvtColor(roi, cv2.COLOR_BGR2LAB)
        mean_lab = cv2.mean(lab)[:3]
        
        return {
            'hist_b': hist_b,
            'hist_g': hist_g,
            'hist_r': hist_r,
            'mean_bgr': mean_color,
            'std_bgr': std_color,
            'mean_lab': mean_lab
        }
    
    def load_references(self):
        """Carrega e processa todas as imagens de referência"""
        print("Carregando imagens de referência...")
        
        for ratio_dir in sorted(self.reference_dir.glob("1_*")):
            if not ratio_dir.is_dir():
                continue
            
            ratio = ratio_dir.name  # ex: "1_5"
            features_list = []
            
            for img_path in sorted(ratio_dir.glob("*.png")):
                try:
                    img = cv2.imread(str(img_path))
                    if img is None:
                        continue
                    
                    template_region = self.detect_template_region(img)
                    features = self.extract_features(img, template_region)
                    features_list.append(features)
                except Exception as e:
                    print(f"Erro ao processar {img_path}: {e}")
            
            if features_list:
                self.reference_features[ratio] = features_list
                print(f"  ✓ {ratio}: {len(features_list)} imagens")
        
        print(f"\nTotal: {len(self.reference_features)} proporções carregadas\n")
    
    def compare_features(self, features1: Dict, features2: Dict) -> float:
        """
        Compara duas features e retorna similaridade (0-1, maior é mais similar)
        """
        # Compara histogramas usando correlação
        hist_sim_b = cv2.compareHist(features1['hist_b'], features2['hist_b'], cv2.HISTCMP_CORREL)
        hist_sim_g = cv2.compareHist(features1['hist_g'], features2['hist_g'], cv2.HISTCMP_CORREL)
        hist_sim_r = cv2.compareHist(features1['hist_r'], features2['hist_r'], cv2.HISTCMP_CORREL)
        
        hist_similarity = (hist_sim_b + hist_sim_g + hist_sim_r) / 3
        
        # Compara cores médias (normalizado)
        color_diff = np.abs(np.array(features1['mean_bgr']) - np.array(features2['mean_bgr']))
        color_similarity = 1 - (np.mean(color_diff) / 255)
        
        # Compara luminosidade LAB
        lab_diff = np.abs(features1['mean_lab'][0] - features2['mean_lab'][0])
        lab_similarity = 1 - (lab_diff / 255)
        
        # Média ponderada
        total_similarity = (
            hist_similarity * 0.5 +
            color_similarity * 0.3 +
            lab_similarity * 0.2
        )
        
        return max(0, min(1, total_similarity))
    
    def analyze(self, image_path: str, auto_detect_template: bool = True) -> Dict:
        """
        Analisa uma imagem e retorna a proporção estimada com confiabilidade
        
        Args:
            image_path: Caminho da imagem a analisar
            auto_detect_template: Se True, detecta automaticamente o gabarito
        
        Returns:
            {
                'ratio': '1_5',
                'confidence': 0.85,
                'ratio_formatted': '1:5',
                'all_matches': [('1_5', 0.85), ('1_6', 0.72), ...]
            }
        """
        # Carrega imagem
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Não foi possível carregar a imagem: {image_path}")
        
        # Detecta ou usa região do gabarito
        if auto_detect_template:
            template_region = self.detect_template_region(img)
        else:
            # Fallback manual
            height, width = img.shape[:2]
            template_region = (int(width * 0.2), 10, int(width * 0.6), 50)
        
        # Extrai features da imagem de teste
        test_features = self.extract_features(img, template_region)
        
        # Compara com todas as referências
        similarities = {}
        
        for ratio, features_list in self.reference_features.items():
            # Calcula similaridade média com todas as imagens daquela proporção
            sims = [self.compare_features(test_features, ref_feat) 
                   for ref_feat in features_list]
            similarities[ratio] = np.mean(sims)
        
        # Ordena por similaridade
        sorted_matches = sorted(similarities.items(), key=lambda x: x[1], reverse=True)
        
        # Melhor match
        best_ratio, best_confidence = sorted_matches[0]
        
        # Formata proporção (1_5 -> 1:5)
        ratio_formatted = best_ratio.replace('_', ':')
        
        return {
            'ratio': best_ratio,
            'confidence': float(best_confidence),
            'ratio_formatted': ratio_formatted,
            'all_matches': [(r, float(s)) for r, s in sorted_matches[:3]],
            'template_region': template_region
        }


def main():
    """Função de teste"""
    analyzer = MixtureAnalyzer()
    
    # Exemplo de análise
    test_image = "images/1_5/IMG_0470.png"
    
    print(f"Analisando: {test_image}\n")
    result = analyzer.analyze(test_image)
    
    print(f"Proporção detectada: {result['ratio_formatted']}")
    print(f"Confiabilidade: {result['confidence']:.2%}")
    print(f"\nTop 3 matches:")
    for ratio, conf in result['all_matches']:
        print(f"  {ratio.replace('_', ':')}: {conf:.2%}")


if __name__ == "__main__":
    main()
