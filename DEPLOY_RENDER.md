# 🚀 Deploy no Render.com - Passo a Passo

## 📋 PRÉ-REQUISITOS

1. Conta no GitHub
2. Conta no Render.com (gratuita)

---

## 🔥 PASSO A PASSO

### 1️⃣ Subir código para o GitHub

```bash
# Dentro da pasta fuchs/
git init
git add .
git commit -m "Analisador Grafite:Água - PWA"

# Criar repositório no GitHub (pelo site) e depois:
git remote add origin https://github.com/SEU-USUARIO/grafite-analyzer.git
git branch -M main
git push -u origin main
```

---

### 2️⃣ Criar Web Service no Render

1. Acesse: https://dashboard.render.com
2. Clique em **"New +"** → **"Web Service"**
3. Clique em **"Connect GitHub"** (se ainda não conectou)
4. Selecione seu repositório **grafite-analyzer**
5. Clique em **"Connect"**

---

### 3️⃣ Configurar o Web Service

**Name:**
```
grafite-analyzer
```

**Region:**
```
Oregon (US West) - ou qualquer outra
```

**Branch:**
```
main
```

**Root Directory:**
```
(deixe em branco)
```

**Runtime:**
```
Python 3
```

**Build Command:**
```
pip install -r backend/requirements.txt && bash build.sh
```

**Start Command:**
```
bash start.sh
```

**Instance Type:**
```
Free
```

---

### 4️⃣ Variáveis de Ambiente (Opcional)

Nenhuma variável necessária por enquanto.

---

### 5️⃣ Deploy!

1. Clique em **"Create Web Service"**
2. Aguarde o deploy (~5-8 minutos na primeira vez)
3. Acompanhe os logs em tempo real

---

## ✅ APÓS O DEPLOY

Sua aplicação estará disponível em:
```
https://grafite-analyzer.onrender.com
```

(ou o nome que você escolheu)

---

## 🔍 VERIFICAÇÃO

1. Abra a URL do Render
2. Teste o upload de imagem
3. Teste a câmera (se estiver em HTTPS)

---

## ⚠️ IMPORTANTE

- **Cold Start:** O plano gratuito "dorme" após 15min de inatividade
- **Primeira requisição:** Pode levar ~30s para "acordar"
- **Requisições seguintes:** Instantâneas
- **HTTPS:** Automático no Render (necessário para câmera)

---

## 🐛 TROUBLESHOOTING

### Build falhou?
- Verifique os logs no Render
- Certifique-se que `images/` está no repositório
- Verifique que todos os arquivos foram commitados

### Aplicação não abre?
- Verifique se o Start Command está correto
- Verifique os logs em "Logs" no Render
- Aguarde alguns minutos (cold start)

### Análise não funciona?
- Verifique se o cache foi gerado no build
- Veja os logs do Render

---

## 📊 MONITORAMENTO

No dashboard do Render você pode ver:
- Status do serviço
- Logs em tempo real
- Métricas de uso
- Histórico de deploys

---

## 🔄 UPDATES

Para atualizar o app:
```bash
git add .
git commit -m "Atualização"
git push
```

O Render faz deploy automático! 🎉
