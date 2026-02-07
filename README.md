# Analisador de Proporção Grafite:Água

Sistema de visão computacional para análise automática de proporção produto:água em misturas de grafite usadas em indústrias metalúrgicas.

## 📋 Resumo

Este projeto analisa fotos de misturas aplicadas em papel sulfite e determina automaticamente a proporção de diluição, auxiliando operadores a manterem a proporção ideal (1:5 a 1:7).

## ✅ Resultados dos Testes

**Precisão Exata:** 43.3% (identificação precisa da proporção)  
**Precisão por Categoria:** 66.7% (identificação da faixa de proporção)

### Por Categoria:
- Muito Concentrado (1:1 a 1:3): 100%
- Concentrado (1:4 a 1:5): 75%
- Ideal (1:6 a 1:7): 50%
- Diluído (1:8 a 1:10): 50%
- Muito Diluído (1:11+): 60%

## 🎯 Categorias de Análise

O sistema classifica as misturas em 5 categorias práticas:

1. **⚠️ MUITO CONCENTRADO** (1:1 a 1:3) - Adicionar água
2. **✓ BOM - Concentrado** (1:4 a 1:5) - Aceitável
3. **✓✓ IDEAL** (1:6 a 1:7) - Proporção perfeita
4. **✓ BOM - Diluído** (1:8 a 1:10) - Aceitável
5. **⚠️ MUITO DILUÍDO** (1:11+) - Adicionar produto

## 🚀 Como Usar

### Instalação

```bash
pip3 install -r requirements.txt
```

### Executar Demo Interativo

```bash
python3 demo.py
```

### Testar Precisão Geral

```bash
python3 test_accuracy.py
```

### Testar com Categorias

```bash
python3 test_categories.py
```

### Analisar Imagem Específica

```bash
python3 test_accuracy.py caminho/da/imagem.png
```

## 📁 Estrutura

```
.
├── image_analyzer.py      # Motor de análise principal
├── test_accuracy.py       # Testes de precisão
├── test_categories.py     # Análise melhorada com categorias
├── demo.py               # Interface interativa
├── requirements.txt      # Dependências
└── images/              # Imagens de referência
    ├── 1_1/            # Proporção 1:1
    ├── 1_2/            # Proporção 1:2
    └── ...
```

## 🔧 Tecnologias

- **Python 3.9+**
- **OpenCV** - Processamento de imagens e correção de cor
- **NumPy** - Cálculos numéricos

## 💡 Funcionamento

1. **Detecção do Gabarito:** Identifica automaticamente o retângulo cinza (#777777) no topo do papel
2. **Correção de Iluminação:** Ajusta a foto baseado no gabarito para compensar variações de luz
3. **Extração de Características:** Analisa histogramas de cor, tonalidade e luminosidade
4. **Comparação:** Compara com banco de imagens de referência
5. **Classificação:** Retorna proporção e categoria com nível de confiança

## 📊 Viabilidade

**Status:** ⚠️ PARCIALMENTE VIÁVEL

A precisão de 66.7% por categoria é funcional para uso prático com ressalvas:

### ✅ Pontos Fortes:
- Excelente precisão para misturas muito concentradas (100%)
- Boa correção de iluminação via gabarito
- Sistema de categorias é prático para operadores

### ⚠️ Limitações:
- Dificuldade em distinguir proporções muito próximas (ex: 1:6 vs 1:7)
- Categorias intermediárias (ideal e diluído) com menor precisão
- Variações na aplicação da mistura afetam resultado

### 🎯 Recomendações para PWA:

1. **Usar sistema de categorias** (não proporção exata)
2. **Coletar mais amostras** de cada proporção
3. **Padronizar captura:** Distância fixa, iluminação ambiente controlada
4. **Adicionar validação:** Permitir operador confirmar/corrigir resultado
5. **Feedback visual:** Mostrar gabarito detectado para validação

## 📝 Próximos Passos

Para desenvolvimento do PWA:

1. Backend API (FastAPI/Flask) para processar imagens
2. Frontend PWA com câmera e preview
3. Modo offline com cache de análises
4. Histórico de análises por operador
5. Dashboard de estatísticas

## 🔬 Melhorias Futuras

- Machine Learning (CNN) para melhor precisão
- Mais amostras de treinamento por proporção
- Análise de textura além de cor
- Calibração por lote de produto
