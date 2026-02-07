# GUIA RÁPIDO - Analisador de Proporção Grafite:Água

## 🚀 Início Rápido

```bash
# 1. Instalar dependências
pip3 install -r requirements.txt

# 2. Executar demo interativo
python3 demo.py
```

## 📊 Comandos Principais

### Testar Precisão do Sistema
```bash
python3 test_accuracy.py
```
Executa teste completo em todas as amostras e gera relatório de precisão.

### Testar com Categorias (Recomendado)
```bash
python3 test_categories.py
```
Testa sistema com 5 categorias práticas. Melhor precisão (66.7%).

### Analisar Imagem Específica
```bash
python3 test_accuracy.py caminho/para/imagem.png
```
Analisa uma única imagem e salva resultado visual em `test_result.png`.

### Visualizar Amostras de Referência
```bash
python3 visualize_samples.py 1  # Grade visual
python3 visualize_samples.py 2  # Listar amostras
python3 visualize_samples.py 3  # Analisar qualidade
```

## 🎯 Interpretação dos Resultados

### Categorias
- **⚠️ MUITO CONCENTRADO** (1:1 a 1:3) → Adicionar água
- **✓ BOM - Concentrado** (1:4 a 1:5) → OK
- **✓✓ IDEAL** (1:6 a 1:7) → Perfeito!
- **✓ BOM - Diluído** (1:8 a 1:10) → OK
- **⚠️ MUITO DILUÍDO** (1:11+) → Adicionar produto

### Confiança
- **> 80%** - Alta confiança no resultado
- **60-80%** - Confiança moderada
- **< 60%** - Baixa confiança, revisar imagem

## 📸 Dicas para Captura

1. **Iluminação:** Ambiente bem iluminado, evitar sombras
2. **Distância:** Manter distância consistente (~30-40cm)
3. **Ângulo:** Foto perpendicular ao papel
4. **Gabarito:** Garantir que o retângulo cinza esteja visível
5. **Fundo:** Evitar fundos com cores fortes

## 🔧 Arquivos Principais

- `image_analyzer.py` - Motor de análise
- `test_categories.py` - Sistema com categorias (MELHOR)
- `demo.py` - Interface interativa
- `reference_grid.png` - Grid visual de referências

## 📈 Métricas de Desempenho

**Precisão Exata:** 43.3%
**Precisão por Categoria:** 66.7%

As categorias são mais confiáveis que proporções exatas para uso prático.

## 🐛 Solução de Problemas

### Erro "ModuleNotFoundError: cv2"
```bash
pip3 install opencv-python
```

### Erro "No module named 'numpy'"
```bash
pip3 install numpy
```

### Baixa Confiança nos Resultados
- Verificar iluminação da foto
- Garantir que gabarito está visível
- Verificar se aplicação da mistura está uniforme

### Gabarito Não Detectado
O sistema detecta automaticamente, mas se falhar usa região padrão.
Para debug, ver `result['template_region']` no resultado.

## 💡 Próximos Passos para PWA

1. **Backend:** FastAPI ou Flask para API REST
2. **Frontend:** React/Vue com PWA
3. **Camera:** Acesso à câmera do dispositivo
4. **Offline:** Service Worker para cache
5. **Histórico:** Banco de dados local (IndexedDB)

## 📞 Observações

- Sistema funciona melhor para categorias amplas
- Proporções muito próximas são difíceis de distinguir
- Recomenda-se validação manual inicial
- Coletar mais amostras pode melhorar precisão
