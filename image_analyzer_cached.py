import cv2
import numpy as np
import pickle
import json
from pathlib import Path
from typing import Tuple, Dict, List
from datetime import datetime
from image_analyzer import MixtureAnalyzer

class CachedMixtureAnalyzer(MixtureAnalyzer):
    """
    Versão otimizada que usa cache de features pré-processadas
    Carrega imagens UMA VEZ, salva features, e reutiliza
    """
    
    def __init__(self, reference_dir: str = "images", cache_file: str = "features_cache.pkl"):
        self.reference_dir = Path(reference_dir)
        self.cache_file = cache_file
        self.target_gray = (119, 119, 119)  # #777777
        self.reference_features = {}
        
        # Tenta carregar do cache
        if self._load_from_cache():
            print("✓ Features carregadas do cache (instantâneo!)")
        else:
            print("⚙️  Processando imagens pela primeira vez...")
            self.load_references()
            self._save_to_cache()
            print("✓ Cache criado para próximas execuções")
    
    def _load_from_cache(self) -> bool:
        """Carrega features do cache se existir e for válido"""
        cache_path = Path(self.cache_file)
        
        if not cache_path.exists():
            return False
        
        try:
            with open(cache_path, 'rb') as f:
                cache_data = pickle.load(f)
            
            # Valida estrutura do cache
            if 'features' not in cache_data or 'metadata' not in cache_data:
                print("⚠️  Cache inválido, será recriado")
                return False
            
            # Verifica se as imagens de referência mudaram
            current_images = self._count_reference_images()
            cached_images = cache_data['metadata'].get('total_images', 0)
            
            if current_images != cached_images:
                print(f"⚠️  Imagens mudaram ({cached_images} → {current_images}), recriando cache")
                return False
            
            self.reference_features = cache_data['features']
            
            # Info do cache
            created = cache_data['metadata'].get('created', 'desconhecido')
            print(f"📦 Cache válido (criado em {created})")
            print(f"   {len(self.reference_features)} proporções, {cached_images} imagens")
            
            return True
            
        except Exception as e:
            print(f"⚠️  Erro ao carregar cache: {e}")
            return False
    
    def _save_to_cache(self):
        """Salva features processadas no cache"""
        try:
            cache_data = {
                'features': self.reference_features,
                'metadata': {
                    'created': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'total_images': self._count_reference_images(),
                    'proportions': list(self.reference_features.keys()),
                    'version': '1.0'
                }
            }
            
            with open(self.cache_file, 'wb') as f:
                pickle.dump(cache_data, f, protocol=pickle.HIGHEST_PROTOCOL)
            
            cache_size = Path(self.cache_file).stat().st_size / 1024  # KB
            print(f"💾 Cache salvo: {self.cache_file} ({cache_size:.1f} KB)")
            
        except Exception as e:
            print(f"⚠️  Erro ao salvar cache: {e}")
    
    def _count_reference_images(self) -> int:
        """Conta total de imagens de referência"""
        total = 0
        for ratio_dir in self.reference_dir.glob("1_*"):
            if ratio_dir.is_dir():
                total += len(list(ratio_dir.glob("*.png")))
        return total
    
    def rebuild_cache(self):
        """Força reconstrução do cache"""
        print("\n🔄 Reconstruindo cache...")
        self.reference_features = {}
        self.load_references()
        self._save_to_cache()
        print("✓ Cache reconstruído com sucesso\n")
    
    def get_cache_info(self) -> Dict:
        """Retorna informações sobre o cache"""
        cache_path = Path(self.cache_file)
        
        if not cache_path.exists():
            return {
                'exists': False,
                'message': 'Cache não existe'
            }
        
        try:
            with open(cache_path, 'rb') as f:
                cache_data = pickle.load(f)
            
            metadata = cache_data.get('metadata', {})
            cache_size = cache_path.stat().st_size / 1024  # KB
            
            return {
                'exists': True,
                'file': str(cache_path),
                'size_kb': round(cache_size, 2),
                'created': metadata.get('created'),
                'total_images': metadata.get('total_images'),
                'proportions': metadata.get('proportions'),
                'version': metadata.get('version')
            }
            
        except Exception as e:
            return {
                'exists': True,
                'error': str(e)
            }


def compare_performance():
    """Compara performance entre versão com e sem cache"""
    import time
    
    print("\n" + "="*70)
    print("COMPARAÇÃO DE PERFORMANCE - COM vs SEM CACHE")
    print("="*70 + "\n")
    
    # Teste 1: Primeira execução (sem cache)
    print("1️⃣  PRIMEIRA EXECUÇÃO (processando imagens):")
    print("-" * 70)
    
    # Remove cache se existir
    cache_file = "features_cache.pkl"
    if Path(cache_file).exists():
        Path(cache_file).unlink()
    
    start = time.time()
    analyzer1 = CachedMixtureAnalyzer()
    time1 = time.time() - start
    
    print(f"⏱️  Tempo: {time1:.2f} segundos\n")
    
    # Teste 2: Segunda execução (com cache)
    print("2️⃣  SEGUNDA EXECUÇÃO (usando cache):")
    print("-" * 70)
    
    start = time.time()
    analyzer2 = CachedMixtureAnalyzer()
    time2 = time.time() - start
    
    print(f"⏱️  Tempo: {time2:.2f} segundos\n")
    
    # Teste 3: Múltiplas instâncias (simulando requisições)
    print("3️⃣  SIMULANDO 10 REQUISIÇÕES (10 instâncias):")
    print("-" * 70)
    
    start = time.time()
    for i in range(10):
        _ = CachedMixtureAnalyzer()
    time3 = time.time() - start
    
    print(f"⏱️  Tempo total: {time3:.2f} segundos")
    print(f"⏱️  Por requisição: {time3/10:.3f} segundos\n")
    
    # Resumo
    print("="*70)
    print("📊 RESUMO:")
    print("="*70)
    print(f"  Sem cache:    {time1:.2f}s  (primeira vez)")
    print(f"  Com cache:    {time2:.2f}s  (instantâneo!)")
    print(f"  Ganho:        {(time1/time2):.1f}x mais rápido")
    print(f"  Por request:  {time3/10:.3f}s  (produção)")
    print()
    
    # Info do cache
    info = analyzer2.get_cache_info()
    if info['exists']:
        print(f"💾 Cache: {info['size_kb']} KB")
        print(f"   Criado: {info['created']}")
        print(f"   Imagens: {info['total_images']}")
    
    print("\n" + "="*70)
    print("💡 RECOMENDAÇÃO PARA PWA:")
    print("="*70)
    print("""
  1. Processar imagens UMA VEZ ao fazer deploy
  2. Incluir features_cache.pkl no deploy
  3. Cada requisição apenas carrega o cache (instantâneo)
  4. Re-processar apenas quando adicionar novas amostras
    """)


def main():
    """Exemplo de uso"""
    print("\n" + "="*70)
    print("ANALISADOR COM CACHE - Demonstração")
    print("="*70 + "\n")
    
    # Cria analyzer (usa cache se existir)
    analyzer = CachedMixtureAnalyzer()
    
    # Info do cache
    print("\n📋 Informações do Cache:")
    print("-" * 70)
    info = analyzer.get_cache_info()
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    # Teste de análise
    test_image = "images/1_6/IMG_0475.png"
    if Path(test_image).exists():
        print(f"\n🔍 Testando análise: {test_image}")
        print("-" * 70)
        
        import time
        start = time.time()
        result = analyzer.analyze(test_image)
        elapsed = time.time() - start
        
        print(f"✓ Proporção: {result['ratio_formatted']}")
        print(f"✓ Confiança: {result['confidence']:.1%}")
        print(f"⏱️  Tempo: {elapsed:.3f}s")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "benchmark":
        compare_performance()
    else:
        main()
