# 🔧 Correções Necessárias no Container

## ⚠️ Problemas Identificados

### 1. **Recursos Muito Altos (Vai Custar Muito!)**
- ❌ **CPU:** 1 vCPU (muito alto)
- ❌ **GPU:** 1 (não precisa!)
- ❌ **Memória Hard:** 3 GB (muito alto)
- ❌ **Memória Soft:** 1 GB (pode ser menor)

### 2. **Variável de Ambiente Incompleta**
- ⚠️ **OPENROUTER_API_KEY:** Parece estar cortada (`sk-or-v1-737745303522906916e5`)
- ⚠️ **PORT:** Não está configurada!

### 3. **O que está correto:**
- ✅ Nome: `iscoolgpt-app`
- ✅ URI da imagem: `176977333713.dkr.ecr.sa-east-1.amazonaws.com/iscoolgpt:latest`
- ✅ Porta: 3000 TCP HTTP
- ✅ Container essencial: Sim

---

## ✅ Configuração Correta

### **Limites de Alocação de Recursos:**

1. **CPU:**
   - Valor: `256` (ou `0.25` se aceitar decimal)
   - Unidade: vCPU
   - **Por quê:** Aplicação simples não precisa de 1 vCPU completo

2. **GPU:**
   - Valor: `0` (ou deixe vazio)
   - **Por quê:** Não precisa de GPU

3. **Limite rígido de memória:**
   - Valor: `512` (ou `0.5` se aceitar decimal)
   - Unidade: MB (não GB!)
   - **Por quê:** Aplicação Python/FastAPI não precisa de 3 GB

4. **Limite flexível de memória:**
   - Valor: `256` (ou `0.25` se aceitar decimal)
   - Unidade: MB
   - **Por quê:** Limite flexível menor que o rígido

### **Variáveis de Ambiente:**

Adicione/Corrija estas variáveis:

1. **OPENROUTER_API_KEY:**
   - **Chave:** `OPENROUTER_API_KEY`
   - **Valor:** Cole a chave COMPLETA do seu arquivo `.env`
   - ⚠️ **IMPORTANTE:** A chave que você colocou parece estar cortada!
   - Deve começar com `sk-or-v1-` e ter muito mais caracteres

2. **PORT:**
   - **Chave:** `PORT`
   - **Valor:** `3000`
   - ⚠️ **FALTA:** Esta variável não está configurada!

3. **APP_URL (Opcional):**
   - **Chave:** `APP_URL`
   - **Valor:** Deixe vazio ou coloque a URL pública (depois que tiver o IP)

---

## 💰 Impacto nos Custos

### Configuração Atual (ERRADA):
- CPU: 1 vCPU = ~$0.04/hora
- Memória: 3 GB = ~$0.03/hora
- **Total:** ~$0.07/hora = **~$50/mês** 💸

### Configuração Correta:
- CPU: 0.25 vCPU = ~$0.01/hora
- Memória: 0.5 GB = ~$0.005/hora
- **Total:** ~$0.015/hora = **~$11/mês** ✅

**Economia:** ~$39/mês! 💰

---

## 📝 Passo a Passo para Corrigir

### 1. Corrigir Recursos
1. Na seção **"Limites de alocação de recursos"**
2. **CPU:** Mude de `1` para `256` (ou `0.25`)
3. **GPU:** Mude de `1` para `0` (ou deixe vazio)
4. **Limite rígido de memória:** Mude de `3 GB` para `512 MB` (ou `0.5 GB`)
5. **Limite flexível de memória:** Mude de `1 GB` para `256 MB` (ou `0.25 GB`)

### 2. Corrigir Variáveis de Ambiente

#### OPENROUTER_API_KEY:
1. Clique em **"Remover"** na variável OPENROUTER_API_KEY atual
2. Clique em **"Adicionar variável de ambiente"**
3. **Chave:** `OPENROUTER_API_KEY`
4. **Tipo:** `Valor`
5. **Valor:** Cole a chave COMPLETA do seu arquivo `.env`
   - Para pegar a chave completa:
   ```bash
   cat .env | grep OPENROUTER_API_KEY
   ```

#### PORT:
1. Clique em **"Adicionar variável de ambiente"**
2. **Chave:** `PORT`
3. **Tipo:** `Valor`
4. **Valor:** `3000`

#### APP_URL (Opcional):
- Se estiver vazio, pode deixar assim ou preencher depois

---

## ✅ Checklist Final

- [ ] CPU: 256 (0.25 vCPU)
- [ ] GPU: 0 (removido)
- [ ] Memória Hard: 512 MB (0.5 GB)
- [ ] Memória Soft: 256 MB (0.25 GB)
- [ ] OPENROUTER_API_KEY: Chave completa e correta
- [ ] PORT: 3000
- [ ] APP_URL: Vazio ou URL pública

---

## 🎯 Resumo

**Mude:**
- CPU: `1` → `256` ou `0.25`
- GPU: `1` → `0`
- Memória Hard: `3 GB` → `512 MB` ou `0.5 GB`
- Memória Soft: `1 GB` → `256 MB` ou `0.25 GB`
- OPENROUTER_API_KEY: Cole a chave COMPLETA
- Adicione: `PORT=3000`

**Isso vai economizar muito dinheiro!** 💰

